import hashlib,json,sys,unittest
from decimal import Decimal,ROUND_HALF_UP,ROUND_HALF_DOWN,ROUND_HALF_EVEN,ROUND_DOWN,ROUND_UP
from fractions import Fraction
from pathlib import Path
from check_rounding import diagnose,SOURCE,EXPECTED_SHA256


class Checks(unittest.TestCase):
    def test_exact_failed_response_and_sum(self):
        result=diagnose()
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),EXPECTED_SHA256)
        self.assertEqual(result['selected'],'ALLOW');self.assertEqual(result['reported_leader'],'ABSTAIN')
        self.assertEqual(result['probability_sum'],'1')

    def test_standard_rounding_preserves_order_near_boundary(self):
        values=[Decimal('0.345')+Decimal(i)/100000 for i in range(2001)]
        for mode in (ROUND_HALF_UP,ROUND_HALF_DOWN,ROUND_HALF_EVEN,ROUND_DOWN,ROUND_UP):
            rounded=[v.quantize(Decimal('0.01'),rounding=mode) for v in values]
            self.assertTrue(all(a<=b for a,b in zip(rounded,rounded[1:])))
            tie=Decimal('0.355')
            self.assertEqual(tie.quantize(Decimal('.01'),rounding=mode),tie.quantize(Decimal('.01'),rounding=mode))

    def test_independent_closed_intervals_only_touch_at_tie(self):
        result=diagnose()
        self.assertTrue(result['permissive_intervals_overlap'])
        self.assertTrue(result['overlap_is_only_exact_boundary_tie'])
        self.assertEqual(Fraction(result['permissive_selected_upper']),Fraction(71,200))
        # An interval-overlap-only guard would be insufficient evidence of a
        # consistent rounding process. Equal exact inputs cannot round differently.

    def test_documented_confidence_excludes_even_permissive_tie(self):
        result=diagnose()
        self.assertEqual(Fraction(result['maximum_confidence_with_selected_max']),Fraction(13,400))
        self.assertEqual(Fraction(result['nearest_hundredth_confidence_lower']),Fraction(7,200))
        self.assertLess(Fraction(13,400),Fraction(7,200))
        self.assertFalse(result['nearest_hundredth_probability_and_confidence_compatible'])

    def test_unchanged_adapter_still_rejects_saved_failure(self):
        sys.path.insert(0,'source/Jev-Live-JL-002-Repeat5')
        from jev import validate,Stop
        ledger=SOURCE.parent/'ledger.jsonl'
        request=next(r['request'] for r in [json.loads(x) for x in ledger.read_text().splitlines()]
                     if r['event']=='reserved' and r['sequence']==456)
        response=json.loads(SOURCE.read_bytes())
        with self.assertRaisesRegex(Stop,'choice is not a probability maximum'):validate(response,request)


if __name__=='__main__':unittest.main(verbosity=2)
