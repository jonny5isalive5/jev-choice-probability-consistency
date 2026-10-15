import contextlib,copy,hashlib,io,json,tempfile,unittest
from decimal import Decimal
from pathlib import Path
from budget import SharedBudget,BudgetTransport
from jev import Client,MockTransport,Stop,CALL_RESERVE,RATE_USD,canonical,validate,strict_json,probability_mass_policy
from pilot import make_request
from repeat import run_one

ROOT=Path(__file__).parent
OLD=Path('source/Jev-Live-JL-002-R1')
BASE=Path('evidence/Jev-Live-JL-002-Repeat5')


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=BASE/'work');self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)
        prompts=json.loads((ROOT/'prompts.json').read_text())
        self.request=make_request({'fixture':True},'Decide.',[],prompts)

    def test_identical_adapter_inputs_arm_execution_and_scorer(self):
        for name in ('jev.py','pilot.py','score.py','secure_credential.py','cases.json','answer_key.json','prompts.json','protocol.json','dataset.py','verify_cases.py'):
            self.assertEqual((ROOT/name).read_bytes(),(OLD/name).read_bytes(),name)

    def test_rounded_probabilities_preserved_and_outside_envelope_rejected(self):
        for p in ({'a':.17,'b':.02,'c':.8},{'a':.18,'b':.02,'c':.81}):
            before=canonical(p);self.assertIn('hundredth',probability_mass_policy(p));self.assertEqual(canonical(p),before)
        for p in ({'a':.16,'b':.02,'c':.8},{'a':.19,'b':.02,'c':.81},{'a':.171,'b':.021,'c':.8}):
            with self.assertRaises(Stop):probability_mass_policy(p)

    def test_shared_budget_across_distinct_clients_and_ceiling_before_dispatch(self):
        budget=SharedBudget(self.path/'budget',0,ceiling=CALL_RESERVE)
        first=Client(BudgetTransport(MockTransport(),budget,1),self.path/'first')
        first.call(self.request,'one','single',0)
        self.assertGreater(budget.accounted_gbp,0);self.assertLess(budget.accounted_gbp,CALL_RESERVE)
        class Never:
            genuine=False;calls=0
            def __call__(self,payload):self.calls+=1;raise AssertionError('dispatched past ceiling')
        inner=Never();second=Client(BudgetTransport(inner,budget,2),self.path/'second')
        with self.assertRaises(Stop):second.call(self.request,'two','single',0)
        self.assertEqual(inner.calls,0);self.assertEqual(budget.calls,1)

    def test_settlement_and_maximum_context_boundary(self):
        budget=SharedBudget(self.path/'budget',0,ceiling=CALL_RESERVE)
        budget.reserve(1)
        budget.settle({'usage':{'input_tokens':65536}},1)
        self.assertEqual(budget.accounted_gbp,CALL_RESERVE)
        with self.assertRaises(Stop):budget.reserve(2)

    def test_uncertain_call_halts_and_retains_full_reservation(self):
        class Timeout:
            genuine=False;calls=0
            def __call__(self,payload):self.calls+=1;raise TimeoutError()
        budget=SharedBudget(self.path/'budget',0);inner=Timeout()
        client=Client(BudgetTransport(inner,budget,1),self.path/'run')
        with self.assertRaises(Stop):client.call(self.request,'one','single',0)
        with self.assertRaises(Stop):client.call(self.request,'one','single',0)
        self.assertEqual(budget.accounted_gbp,CALL_RESERVE);self.assertTrue(budget.halted);self.assertEqual(inner.calls,1)

    def test_invalid_response_raw_is_retained_and_budget_not_released(self):
        class Invalid:
            genuine=False
            def __call__(self,payload):return 200,b'{"model":"wrong"}'
        budget=SharedBudget(self.path/'budget',0);client=Client(BudgetTransport(Invalid(),budget,1),self.path/'run')
        with self.assertRaises(Stop):client.call(self.request,'one','single',0)
        self.assertEqual((client.directory/'response-0001.json').read_bytes(),b'{"model":"wrong"}')
        self.assertEqual(budget.accounted_gbp,CALL_RESERVE);self.assertTrue(budget.pending)

    def test_call_limit_historical_carry_and_exclusive_journal(self):
        budget=SharedBudget(self.path/'budget','0.097394136',max_calls=1)
        self.assertEqual(budget.accounted_gbp,Decimal('0.194788272'))
        budget.reserve(1);budget.settle({'usage':{'input_tokens':1}},1)
        with self.assertRaises(Stop):budget.reserve(2)
        with self.assertRaises(FileExistsError):SharedBudget(self.path/'budget',0)

    def test_exact_865_request_replay_without_network(self):
        original=Path('evidence/Jev-Live-JL-002-R1/evidence/continued-run-001')
        events=[json.loads(x) for x in (original/'ledger.jsonl').read_text().splitlines()]
        reservations=[e for e in events if e['event']=='reserved']
        test=self
        class Replay:
            genuine=False;calls=0
            def __call__(self,payload):
                expected=reservations[self.calls]
                test.assertEqual(payload,canonical(expected['request']))
                self.calls+=1
                return 200,(original/f'response-{self.calls:04}.json').read_bytes()
        transport=Replay()
        with contextlib.redirect_stdout(io.StringIO()):result=run_one(1,self.path/'replay',transport)
        self.assertIsNone(result['stop']);self.assertEqual(transport.calls,865)
        actual=[json.loads(x) for x in (self.path/'replay/predictions.jsonl').read_text().splitlines()]
        expected=[json.loads(x) for x in (original/'predictions.jsonl').read_text().splitlines()]
        for row in actual:row['genuine']=True
        self.assertEqual(actual,expected)


if __name__=='__main__':unittest.main(verbosity=2)
