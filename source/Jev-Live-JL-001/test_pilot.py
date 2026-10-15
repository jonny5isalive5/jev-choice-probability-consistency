import copy
import itertools
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from jev import Client, MockTransport, HTTPTransport, MODEL, Stop, canonical, strict_json, validate, CALL_RESERVE
from pilot import request, run_arm


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir='evidence/Jev-Live-JL-001/evidence')
        self.addCleanup(self.temp.cleanup)
        self.req = request({'records': []}, 'Decide.')

    def client(self, transport=None, cap=217):
        return Client(transport or MockTransport(), Path(self.temp.name) / 'run', cap)

    def response(self):
        return strict_json(MockTransport()(canonical(self.req))[1])

    def test_current_documented_contract(self):
        r = self.response()
        self.assertEqual(validate(r, self.req)['model'], MODEL)

    def test_model_usage_probability_and_answer_fail_closed(self):
        mutations = [lambda r: r.update(model='jev-latest'),
                     lambda r: r.pop('usage'),
                     lambda r: r['usage'].update(input_tokens=65537),
                     lambda r: r['usage'].update(input_tokens=True),
                     lambda r: r['answers']['decision'].update(choice='invented'),
                     lambda r: r['answers']['decision'].update(confidence=float('nan')),
                     lambda r: r['answers']['decision']['probabilities'].update(ALLOW=0.5),
                     lambda r: r['answers'].update(extra={})]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                r = self.response(); mutate(r)
                with self.assertRaises(Stop):
                    validate(r, self.req)

    def test_duplicate_and_nonfinite_json(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}'):
            with self.assertRaises(Stop):
                strict_json(raw)

    def test_http_error_preserved_no_retry(self):
        class Error:
            genuine = False
            calls = 0
            def __call__(self, payload):
                self.calls += 1
                return 429, b'{"error":"test rate limit"}'
        transport = Error(); c = self.client(transport)
        with self.assertRaises(Stop): c.call(self.req, 'x', 'single', 0)
        with self.assertRaises(Stop): c.call(self.req, 'x', 'single', 0)
        self.assertEqual(transport.calls, 1)
        self.assertEqual(c.reserved, CALL_RESERVE)
        self.assertTrue((c.directory/'response-0001.json').exists())

    def test_timeout_keeps_reservation(self):
        class Error:
            genuine = False
            def __call__(self, payload): raise TimeoutError()
        c = self.client(Error())
        with self.assertRaises(Stop): c.call(self.req, 'x', 'single', 0)
        self.assertEqual(c.reserved, CALL_RESERVE)
        self.assertTrue(c.halted)

    def test_budget_refused_before_transport(self):
        c = self.client(cap=1)
        c.call(self.req, 'x', 'single', 0)
        with self.assertRaises(Stop): c.call(self.req, 'y', 'single', 0)
        self.assertEqual(c.calls, 1)
        from decimal import Decimal
        self.assertLess(CALL_RESERVE * 217, Decimal(5))

    def test_reopen_evidence_directory_rejected(self):
        c = self.client()
        with self.assertRaises(FileExistsError): Client(MockTransport(), c.directory)

    def test_no_redirect_and_secret_redaction(self):
        from jev import NoRedirect
        self.assertIsNone(NoRedirect().redirect_request(None,None,302,'',{},'https://invalid.example'))
        transport = HTTPTransport('dummy-test-token')
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self,*a): pass
            def read(self,n): return b'{"error":"dummy-test-token"}'
        with patch.object(transport._opener, 'open', return_value=Response()):
            status, raw = transport(canonical(self.req))
        self.assertNotIn(b'dummy-test-token', raw)

    def test_authority_and_source_data_never_sent(self):
        case = {'id':'private-id','expected':'hidden-truth','input':{'records':[]}}
        c = self.client()
        for arm in ('single','swarm','sequential'):
            run_arm(c, case, arm)
        events = [json.loads(x) for x in c.ledger.read_text().splitlines()]
        requests = [e['request'] for e in events if e['event']=='reserved']
        self.assertEqual(len(requests),9)
        for req in requests:
            self.assertNotIn('private-id', json.dumps(req))
            self.assertNotIn('hidden-truth', json.dumps(req))
        # Three independent perspectives have no prior judgments.
        self.assertTrue(all(r['state'] == case['input'] for r in requests[1:4]))
        self.assertEqual(len(requests[4]['state']['judgments']),3)
        self.assertEqual([len(r['state'].get('judgments',[])) for r in requests[5:]], [0,1,2,3])

    def test_case_key_verified_from_actual_input(self):
        root = Path(__file__).parent
        cases = json.loads((root/'cases.json').read_text())
        key = json.loads((root/'answer_key.json').read_text())
        self.assertEqual(len(cases),24)
        for case in cases:
            state = case['input']; policy = state['policy']
            facts = policy['requirements'] + [policy['veto']]
            possibilities = []
            for fact in facts:
                claims = {r['asserted'] for r in state['records'] if r['claim']==fact}
                possibilities.append(claims if len(claims)==1 else {True,False})
            outcomes = set()
            for values in itertools.product(*possibilities):
                outcomes.add(all(values[:2]) and values[2] is False)
            expected = {frozenset({True}):'ALLOW',frozenset({False}):'DENY',
                        frozenset({True,False}):'ABSTAIN'}[frozenset(outcomes)]
            self.assertEqual(key[case['id']]['expected'],expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
