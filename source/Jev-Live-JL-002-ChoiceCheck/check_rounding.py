"""Offline diagnosis only. No credential reader, network transport or mutation of originals."""
import hashlib
import json
from decimal import Decimal,ROUND_HALF_UP,ROUND_HALF_DOWN,ROUND_HALF_EVEN,ROUND_DOWN,ROUND_UP
from fractions import Fraction
from pathlib import Path

SOURCE=Path('evidence/Jev-Live-JL-002-Repeat5/evidence/live-batch/repeat-01/response-0456.json')
EXPECTED_SHA256='2533dd81a40a8a01e9e224cb498737e587cc79b536323bbac133d1e8006211fd'


def diagnose():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA256:raise RuntimeError('original response changed')
    response=json.loads(raw);answer=response['answers']['decision']
    p={k:Fraction(str(v)) for k,v in answer['probabilities'].items()}
    selected=answer['choice'];leader=max(p,key=p.get)
    half_cent=Fraction(1,200)
    selected_upper=p[selected]+half_cent
    leader_lower=p[leader]-half_cent
    # Deliberately inclusive intervals are the most permissive boundary model.
    overlap=selected_upper>=leader_lower
    boundary_tie=selected_upper==leader_lower
    confidence_lower=Fraction(str(answer['confidence']))-half_cent
    n=len(p)
    maximum_confidence_if_selected_is_max=(selected_upper-Fraction(1,n))/(1-Fraction(1,n))
    confidence_compatible=maximum_confidence_if_selected_is_max>=confidence_lower
    tie_rounding={mode:str(Decimal('0.355').quantize(Decimal('0.01'),rounding=mode))
        for mode in (ROUND_HALF_UP,ROUND_HALF_DOWN,ROUND_HALF_EVEN,ROUND_DOWN,ROUND_UP)}
    return {'original_response_sha256':EXPECTED_SHA256,'selected':selected,'reported_leader':leader,
            'reported_selected_probability':str(p[selected]),'reported_leader_probability':str(p[leader]),
            'probability_sum':str(sum(p.values())),
            'consistent_monotone_rounding_can_reverse_order':False,
            'permissive_selected_upper':str(selected_upper),'permissive_leader_lower':str(leader_lower),
            'permissive_intervals_overlap':overlap,'overlap_is_only_exact_boundary_tie':boundary_tie,
            'boundary_tie_value':'0.355','same_exact_tie_rounds_identically_for_both_options':tie_rounding,
            'confidence_reported':str(answer['confidence']),
            'nearest_hundredth_confidence_lower':str(confidence_lower),
            'maximum_confidence_with_selected_max':str(maximum_confidence_if_selected_is_max),
            'nearest_hundredth_probability_and_confidence_compatible':confidence_compatible,
            'formula':'confidence = (p_max - 1/n) / (1 - 1/n)',
            'judgment':'A rounding-based relaxation of the selected-choice guard is not justified by current evidence.',
            'limits':'This excludes ordinary consistent monotone rounding and the tested nearest-hundredth interval explanation under documented semantics. It does not identify the vendor internal cause.',
            'live_calls':0,'new_spend_usd':'0','adapter_modified':False,'remaining_repeats_executed':False}


if __name__=='__main__':print(json.dumps(diagnose(),indent=2))
