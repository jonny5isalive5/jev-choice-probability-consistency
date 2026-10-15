import unittest,json,tempfile,collections
from pathlib import Path
import diagnostic as d
import analyze
RAW=Path(r'evidence/TypeSafe-Jev-Choice-Report\response.json').read_bytes()
class Checks(unittest.TestCase):
    def test_labels_validated_per_request(self):
        self.assertTrue(d.extract(RAW,['ABSTAIN','ALLOW','DENY'])['mismatch'])
        with self.assertRaises(d.Stop):d.extract(RAW,['IGNORE','ALLOW','DENY'])
        self.assertTrue(d.extract(RAW.replace(b'ABSTAIN',b'IGNORE'),['IGNORE','ALLOW','DENY'])['mismatch'])
    def test_ties_and_invalid(self):
        r=json.loads(RAW);r['answers']['decision']['probabilities']={'ALLOW':.4,'ABSTAIN':.4,'DENY':.2}
        x=d.extract(json.dumps(r),r['answers']['decision']['probabilities']);self.assertTrue(x['tie']);self.assertFalse(x['mismatch'])
        with self.assertRaises(d.Stop):d.strict(b'{"x":1,"x":2}')
        for update in ({'model':'other'},{'usage':{}},{'usage':{'input_tokens':65537,'output_tokens':1}}):
            x=json.loads(RAW);x.update(update)
            with self.assertRaises(d.Stop):d.extract(json.dumps(x),['ALLOW','DENY','ABSTAIN'])
    def test_schedule_balance_and_payloads(self):
        sc=json.loads((d.DESIGN/'schedule.json').read_text());pm=json.loads((d.DESIGN/'payload-manifest.json').read_text())
        self.assertEqual(len(sc),420);self.assertEqual(collections.Counter(x['arm'] for x in sc),{'ABSTAIN':210,'IGNORE':210})
        starts=collections.Counter()
        for j in range(0,420,2):
            a,b=sc[j:j+2];self.assertEqual(a['pair_id'],b['pair_id']);self.assertEqual(a['template'],b['template']);self.assertNotEqual(a['arm'],b['arm']);self.assertEqual([a['pair_position'],b['pair_position']],[1,2])
            starts[(a['template'],a['arm'])]+=1
            payloads={x['arm']:(d.DESIGN/pm[x['payload']]['path']).read_bytes() for x in (a,b)}
            self.assertEqual(payloads['IGNORE'],payloads['ABSTAIN'].replace(b'ABSTAIN',b'IGNORE'))
        for (template,arm),n in starts.items():self.assertEqual(n,15 if template.startswith('order-') else 5)
        for block in range(1,31):self.assertEqual(len([x for x in sc if x['block']==block]),14)
    def mock_pair(self,folder):
        sc=json.loads((d.DESIGN/'schedule.json').read_text())[:2];pm=json.loads((d.DESIGN/'payload-manifest.json').read_text());ps={e['payload']:(d.DESIGN/pm[e['payload']]['path']).read_bytes() for e in sc};seen=[]
        def transport(raw):
            seen.append(raw); label='IGNORE' if 'IGNORE'in json.loads(raw)['questions']['decision']['criteria'] else 'ABSTAIN'
            return 200,{'x-typesafe-request-id':'mock'},RAW.replace(b'ABSTAIN',label.encode()),False
        return d.collect(transport,folder,sc,ps),sc,ps,seen
    def test_mismatch_preserved_and_independent_analysis(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            root=Path(td);result,sc,ps,seen=self.mock_pair(root/'live-run-001')
            self.assertTrue(result['complete']);self.assertEqual(seen,[ps[x['payload']] for x in sc])
            a=analyze.analyze(root,d.DESIGN);self.assertEqual(a['complete_pairs'],1);self.assertEqual(len(a['mismatches']),2)
            self.assertEqual(a['pairs'][0]['probability_deltas_ignore_minus_abstain']['ABSTAIN'],0)
            for e in sc:
                self.assertEqual((root/'live-run-001'/f"{e['attempt']:04d}"/'response.body').read_bytes(),RAW.replace(b'ABSTAIN',e['arm'].encode()))
    def test_unknown_usage_stops_retains_response_and_reserve(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            calls=[];r=json.loads(RAW);r['usage']={};raw=json.dumps(r).encode()
            def mock(b):calls.append(b);return 200,{},raw,False
            payload=(d.DESIGN/'payloads/abstain-order-1.json').read_bytes()
            x=d.collect(mock,Path(td)/'run',[{'attempt':i,'payload':'x'} for i in (1,2)],{'x':payload})
            self.assertEqual(len(calls),1);self.assertEqual(x['guard_accounted_gbp_including_prior'],str(d.PRIOR+d.RESERVE));self.assertEqual((Path(td)/'run/0001/response.body').read_bytes(),raw)
    def test_budget_blocks_before_send(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            def forbidden(b):self.fail('budget exceeded')
            x=d.collect(forbidden,Path(td)/'run',[{'attempt':1,'payload':'x'}],{'x':b'{}'},ceiling=d.PRIOR)
            self.assertEqual(x['attempts'],0)
        self.assertLess(d.PRIOR+420*d.RESERVE,d.LIMIT)
if __name__=='__main__':unittest.main()
