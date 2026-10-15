# Choice mismatch investigation — no justified rounding fix

15 October 2026. The saved response is inconsistent with the documented Choice
semantics. Ordinary consistent rounding does not explain it. The exact vendor
cause is unknown. No adapter was changed, no new inference call was made, and
none of the remaining repeats was executed.

The user authorized a separate adapter fix only if justified. That condition is
not met by the currently available evidence. The five-repeat campaign remains
at its frozen partial checkpoint: repeat 1 has 50 whole completed cases and one
additional completed swarm arm; repeats 2–5 remain unstarted.

## What the response says

Repeat 1, request 456, case JL2-028, single arm, returned model jev-1.14.0:

| Field | Value |
|---|---|
| Selected choice | ALLOW |
| ALLOW probability | 0.35 |
| ABSTAIN probability | 0.36 |
| DENY probability | 0.29 |
| Confidence | 0.04 |

The values sum to exactly 1.00. The earlier approximate-mass correction is not
relevant to this failure. The [Choice documentation](https://docs.typesafe.ai/primitives/choice)
and [official SDK response schema](https://docs.typesafe.ai/sdk/python/api/types/responses)
identify the selected choice as the highest-probability option. The response does
not satisfy that relationship on its reported values.

## Why an extra rounding tolerance is not justified

For one consistent nondecreasing rounding function R, x >= y implies R(x) >= R(y).
Ordinary nearest rounding, truncation, floor and ceiling preserve this order.
They can turn a strict lead into a tie, but cannot turn the highest probability
into a strictly lower reported value. The earlier 0.99 probability sum involved
accumulated rounding error in a sum; that is a different mathematical property.

Even a permissive independent closed-interval interpretation, allowing each
reported value an error of +/-0.005, only lets ALLOW be at least ABSTAIN at one
boundary point: both underlying values would have to be exactly 0.355. A single
consistent rounding rule maps both equal inputs to the same output, not 0.35 for
one and 0.36 for the other. Merely overlapping closed uncertainty intervals is
therefore insufficient evidence for a rounding-based adapter change.

The [documented confidence formula](https://docs.typesafe.ai/confidence) provides
an additional check. For three options, confidence = 1.5 * p_max - 0.5. With ALLOW
at most 0.355 and assumed to be a maximum, confidence is at most 0.0325. A value
reported as 0.04 under nearest-hundredth rounding must be at least 0.035 before
rounding. These ranges do not overlap. This calculation is conditional on the
documented formula and the nearest-hundredth rounding hypothesis; it does not
establish the service's actual internal computations.

Different internal estimates, stochastic rounding, a reporting defect, a choice
selection defect or undocumented semantics cannot be ruled in or out from this
one response. None has been established as the correct explanation. It would be
misleading to call a relaxed choice check a verified rounding repair.

## Verification and preservation

Five offline checks passed: exact saved-response identity and unit mass;
order-preserving standard rounding near the boundary; the sole closed-interval
tie; the incompatible confidence bounds using exact rational arithmetic; and
confirmation that the unchanged frozen adapter still rejects this response.

The mathematical monotonicity argument is the basis of the ordering conclusion.
The finite boundary checks illustrate it; they are not presented as exhaustive
evidence about the vendor's implementation.

No credential was retrieved for this investigation, no live inference was sent,
and additional spend is USD 0. The five-repeat attempt's all-received cost remains
USD 0.047502084, approximately GBP 0.03612 using the previously recorded reference
conversion. Its shared guard remains at GBP 0.295095108 including prior runs and
the retained full reservation for the rejected call. The GBP 5 cap is not the
blocking condition.

All 3,594 protected original files were hash-checked before and after this
investigation. All remained unchanged. The original failure, partial results,
source freezes, raw response and every earlier frozen run remain intact.

Original response SHA-256:
2533dd81a40a8a01e9e224cb498737e587cc79b536323bbac133d1e8006211fd

Diagnostic code: source/Jev-Live-JL-002-ChoiceCheck.
Evidence: evidence/Jev-Live-JL-002-ChoiceCheck.
The diagnostic contains no transport or credential reader. It only reads the
saved failure. Reproduce locally with python -B -m unittest test_rounding -v and
python -B check_rounding.py from the diagnostic source directory.

## Decision

**No rounding-based adapter revision is justified. STOP at the preserved
checkpoint.** The five repeats have not been finished. To continue under the
original contract requires clarification of which response field is authoritative
and why the reported relationship can differ. A separate protocol that records
such responses as contract failures while continuing other cases is another
possible research policy, but it would be an explicit protocol change, not a
rounding correction or an unchanged continuation.
