import unittest,json,tempfile,random,collections
from decimal import Decimal as D,ROUND_HALF_UP
from pathlib import Path
import diagnostic as d
from hypothesis import classify
import analyze
class Checks(unittest.TestCase):
    def test_counterexample_not_false_refutation(self):
        r=classify({'A':'.34','B':'.33','C':'.33'},'B')
        self.assertEqual(r['residual_status'],'interior_compatible');self.assertTrue(r['nonzero_correction_required']);self.assertEqual(r['plain']['status'],'incompatible')
    def test_refuters_and_known_failure(self):
        self.assertEqual(classify({'A':'.17','B':'.02','C':'.80'},'C')['residual_status'],'incompatible')
        self.assertEqual(classify({'A':'.17','B':'.02','C':'.80'},'C')['plain']['status'],'interior_compatible')
        self.assertEqual(classify({'A':'.49','B':'.51'},'A')['residual_status'],'incompatible')
        self.assertEqual(classify({'A':'.36','B':'.34','C':'.30'},'B')['residual_status'],'incompatible')
        self.assertEqual(classify({'A':'.35','B':'.34','C':'.31'},'B')['residual_status'],'interior_compatible')
    def test_generated_forward_examples(self):
        rng=random.Random(731)
        for n in (2,3):
            for _ in range(250):
                cuts=sorted(rng.sample(range(1,10000),n-1));points=[0]+cuts+[10000];u={str(i):D(points[i+1]-points[i])/10000 for i in range(n)};c=max(u,key=u.get);q={k:v.quantize(D('.01'),rounding=ROUND_HALF_UP) for k,v in u.items()};p=dict(q);p[c]+=1-sum(q.values())
                fit=classify(p,c);self.assertNotEqual(fit['residual_status'],'incompatible')
                for cand in fit['candidates']:
                    w=cand['latent_witness'];self.assertEqual(sum(w.values()),1);self.assertEqual(w[c],max(w.values()))
    def test_schedule_and_balanced_orders(self):
        sc=json.loads((d.DESIGN/'schedule.json').read_text());self.assertEqual(len(sc),100)
        self.assertEqual(collections.Counter(x['arm'] for x in sc),{'binary':40,'ternary':60})
        counts=collections.Counter(x['payload'] for x in sc)
        for k,n in counts.items():self.assertEqual(n,20 if k.startswith('binary') else 10)
        pm=json.loads((d.DESIGN/'payload-manifest.json').read_text())
        for k,m in pm.items():
            raw=(d.DESIGN/m['path']).read_bytes();self.assertEqual(d.sha(raw),m['sha256']);self.assertEqual(list(json.loads(raw)['questions']['decision']['criteria']),m['criteria_order'])
    def test_binary_confidence_and_labels(self):
        r={'model':d.MODEL,'answers':{'decision':{'type':'choice','choice':'HEADS','probabilities':{'HEADS':.6,'TAILS':.4},'confidence':.2}},'usage':{'input_tokens':200,'output_tokens':30}}
        x=d.extract(json.dumps(r),['HEADS','TAILS']);self.assertEqual(x['confidence_formula_from_reported'],D('.2'))
        with self.assertRaises(d.Stop):d.extract(json.dumps(r),['RED','GREEN','BLUE'])
    def test_collector_retains_contradiction_and_analyzer_sees_it(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            root=Path(td);payload=(d.DESIGN/'payloads/binary-1.json').read_bytes();raw=json.dumps({'model':d.MODEL,'answers':{'decision':{'type':'choice','choice':'HEADS','probabilities':{'HEADS':.49,'TAILS':.51},'confidence':.02}},'usage':{'input_tokens':200,'output_tokens':30}}).encode()
            def mock(b):self.assertEqual(b,payload);return 200,{'x-typesafe-request-id':'mock'},raw,False
            sc=[{'attempt':i,'arm':'binary','block':1,'payload':'x'} for i in (1,2)]
            x=d.collect(mock,root/'live-run-001',sc,{'x':payload});self.assertTrue(x['complete']);a=analyze.analyze(root);self.assertEqual(len(a['contradictions']),2);self.assertEqual((root/'live-run-001/0001/response.body').read_bytes(),raw)
    def test_budget_and_unknown_usage_stop(self):
        with tempfile.TemporaryDirectory(dir=d.OUT/'work') as td:
            def forbidden(b):self.fail('over budget')
            x=d.collect(forbidden,Path(td)/'budget',[{'attempt':1,'payload':'x'}],{'x':b'{}'},ceiling=d.PRIOR);self.assertEqual(x['attempts'],0)
            calls=[]
            def bad(b):calls.append(b);return 200,{},b'{}',False
            payload=(d.DESIGN/'payloads/binary-1.json').read_bytes();x=d.collect(bad,Path(td)/'unknown',[{'attempt':i,'payload':'x'} for i in (1,2)],{'x':payload});self.assertEqual(len(calls),1);self.assertEqual(x['guard_accounted_gbp_including_prior'],str(d.PRIOR+d.RESERVE))
if __name__=='__main__':unittest.main()
