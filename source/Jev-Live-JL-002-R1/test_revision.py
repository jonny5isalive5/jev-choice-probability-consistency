import ast
import copy
import itertools
import json
import unittest
from pathlib import Path
from jev import Stop, canonical, probability_mass_policy, validate
from pilot import run_arm
from resume import ContinueClient, read_parent

ROOT=Path(__file__).parent
ORIGINAL=Path('source/Jev-Live-JL-002')


class RevisionTests(unittest.TestCase):
    def test_rounding_boundary_and_no_mutation(self):
        for p in ({'a':.17,'b':.02,'c':.80}, {'a':.18,'b':.02,'c':.81},
                  {'a':.17,'b':.02,'c':.7999999999999999}):
            before=canonical(p)
            self.assertEqual(probability_mass_policy(p),'hundredth_rounding_compatible_values_unchanged')
            self.assertEqual(canonical(p),before)
        for p in ({'a':.16,'b':.02,'c':.8}, {'a':.19,'b':.02,'c':.81},
                  {'a':.171,'b':.021,'c':.8}, {'a':float('nan')},
                  {'a':1.01,'b':-.01}, {'a':True}):
            with self.assertRaises(Stop):probability_mass_policy(p)
        self.assertEqual(probability_mass_policy({'a':.12345,'b':.87655}),'strict_unit_mass')

    def test_saved_failure_revalidates_without_change_or_relaxing_other_checks(self):
        old,ledger,reserved,cache,responses,cost,preds=read_parent()
        raw=(old/'response-0221.json').read_bytes()
        response=json.loads(raw);before=canonical(response)
        self.assertIs(validate(response,reserved[221]['request']),response)
        self.assertEqual(before,canonical(response))
        self.assertEqual((old/'response-0221.json').read_bytes(),raw)
        mutations=[lambda r:r.update(model='jev-latest'),
                   lambda r:r['answers']['decision'].update(choice='ALLOW'),
                   lambda r:r['answers']['decision']['probabilities'].pop('ABSTAIN'),
                   lambda r:r['answers']['decision'].update(confidence=2),
                   lambda r:r['usage'].update(input_tokens=-1)]
        for mutation in mutations:
            r=copy.deepcopy(response);mutation(r)
            with self.assertRaises(Stop):validate(r,reserved[221]['request'])
        self.assertEqual(str(cost),'0.023237424')

    def test_every_saved_prediction_replays_identically_and_next_call_is_222(self):
        old,ledger,reserved,cache,responses,cost,preds=read_parent()
        cases=json.loads((ROOT/'cases.json').read_text())
        prompts=json.loads((ROOT/'prompts.json').read_text())
        arms=list(itertools.permutations(('single','swarm','sequential')))
        perspectives=list(itertools.permutations(range(3)))
        schedule=[('SMOKE','smoke',0)]
        for i,case in enumerate(cases):
            for arm in arms[i%6]:
                schedule.extend((case['id'],arm,s) for s in range(1 if arm=='single' else 4))
        class NoNetwork:
            calls=221
            requested=[]
            def call(self,request,cid,arm,stage):
                self.requested.append((cid,arm,stage))
                raise Stop('dry checkpoint before dispatch')
        client=NoNetwork();replay=ContinueClient(client,cache,schedule)
        by_id={(p['case_id'],p['arm']):p for p in preds}
        checkpoint=False
        for i,case in enumerate(cases):
            for arm in arms[i%6]:
                try:
                    choice,history=run_arm(replay,case,arm,perspectives[(i//6+i)%6],prompts)
                except Stop as exc:
                    self.assertEqual(str(exc),'dry checkpoint before dispatch')
                    checkpoint=True;break
                p=by_id.pop((case['id'],arm))
                self.assertEqual(choice,p['choice']);self.assertEqual(history,p['history'])
            if checkpoint:break
        self.assertEqual(by_id,{})
        self.assertEqual(sorted(replay.replayed),list(range(2,222)))
        self.assertEqual(client.requested,[schedule[221]])
        self.assertEqual(schedule[221],('JL2-015','swarm',3))
        self.assertEqual(len(schedule)-221,644)
        with self.assertRaises(Stop):replay.call({},'JL2-015','swarm',0)
        with self.assertRaises(Stop):replay.call({},'wrong','swarm',3)

    def test_scientific_inputs_and_scoring_functions_unchanged(self):
        for name in ('cases.json','answer_key.json','prompts.json','protocol.json','dataset.py','verify_cases.py'):
            self.assertEqual((ROOT/name).read_bytes(),(ORIGINAL/name).read_bytes(),name)
        for name in ('score.py','pilot.py'):
            def functions(path):
                return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body
                        if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
            self.assertEqual(functions(ROOT/name),functions(ORIGINAL/name))


if __name__=='__main__':unittest.main(verbosity=2)
