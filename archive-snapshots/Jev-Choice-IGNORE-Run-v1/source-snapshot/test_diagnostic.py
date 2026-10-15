import unittest,tempfile,json
from pathlib import Path
import diagnostic as d

RAW=Path(r'evidence/TypeSafe-Jev-Choice-Report\response.json').read_bytes().replace(b'ABSTAIN',b'IGNORE')
class Checks(unittest.TestCase):
    def test_only_label_changes_from_frozen_baseline(self):
        original=Path(r'evidence/Jev-Choice-Diagnostic-Design-v1')
        self.assertEqual((d.DESIGN/'schedule.json').read_bytes(),(original/'schedule.json').read_bytes())
        for p in (original/'payloads').glob('*.json'):
            new=(d.DESIGN/'payloads'/p.name).read_bytes()
            self.assertEqual(new,p.read_bytes().replace(b'ABSTAIN',b'IGNORE'))
            self.assertNotIn(b'ABSTAIN',new)
            self.assertEqual(list(json.loads(new)['questions']['decision']['criteria']),[x.replace('ABSTAIN','IGNORE') for x in json.loads(p.read_bytes())['questions']['decision']['criteria']])
        self.assertEqual(json.loads((d.DESIGN/'control-answers.json').read_text())['control-abstain'],'IGNORE')
    def test_original_failure_retained(self):
        x=d.extract(RAW)
        self.assertTrue(x['mismatch']); self.assertEqual(x['gap'],d.D('.01')); self.assertEqual(x['choice'],'ALLOW')
    def test_ties(self):
        r=json.loads(RAW); r['answers']['decision']['probabilities']={'ALLOW':.4,'IGNORE':.4,'DENY':.2}
        x=d.extract(json.dumps(r)); self.assertTrue(x['tie']); self.assertFalse(x['mismatch'])
    def test_invalid(self):
        for mutate in (lambda r:r.update(model='other'),lambda r:r.update(usage={}),lambda r:r['answers']['decision'].update(choice='NONE')):
            r=json.loads(RAW); mutate(r)
            with self.assertRaises(d.Stop): d.extract(json.dumps(r))
        with self.assertRaises(d.Stop): d.strict(b'{"x":1,"x":2}')
    def test_continue_mismatch_and_preserve_wire(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            payload=(d.DESIGN/'payloads/order-6.json').read_bytes(); sent=[]
            def mock(b): sent.append(b); return 200,{'x-typesafe-request-id':'mock'},RAW,False
            schedule=[{'attempt':i,'block':1,'module':'option-order','payload':'test'} for i in (1,2)]
            folder=Path(td)/'run'; x=d.collect(mock,folder,schedule,{'test':payload})
            self.assertTrue(x['complete']); self.assertEqual(sent,[payload,payload]); self.assertEqual((folder/'0001/response.body').read_bytes(),RAW)
    def test_stop_unknown_usage_no_retry(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            r=json.loads(RAW); r['usage']={}; bad=json.dumps(r).encode(); sent=[]
            def mock(b): sent.append(b); return 200,{},bad,False
            x=d.collect(mock,Path(td)/'run',[{'attempt':i,'payload':'x'} for i in (1,2)],{'x':b'{}'})
            self.assertEqual(len(sent),1); self.assertEqual(x['guard_accounted_gbp_including_prior'],str(d.PRIOR+d.RESERVE))
            self.assertEqual((Path(td)/'run/0001/response.body').read_bytes(),bad)
    def test_budget_blocks_before_transport(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            def forbidden(b): self.fail('transport called over budget')
            x=d.collect(forbidden,Path(td)/'run',[{'attempt':1,'payload':'x'}],{'x':b'{}'},ceiling=d.PRIOR)
            self.assertEqual(x['attempts'],0)
    def test_schedule_and_option_bytes(self):
        s=json.loads((d.DESIGN/'schedule.json').read_text()); self.assertEqual(len(s),240)
        base=json.loads((d.DESIGN/'payloads/original.json').read_bytes())
        orders=set()
        for i in range(1,7):
            x=json.loads((d.DESIGN/f'payloads/order-{i}.json').read_bytes())
            self.assertEqual(x,base); orders.add(tuple(x['questions']['decision']['criteria']))
        self.assertEqual(len(orders),6)

if __name__=='__main__': unittest.main()
