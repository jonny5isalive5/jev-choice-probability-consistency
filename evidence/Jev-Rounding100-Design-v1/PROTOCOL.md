# Rounding-residual challenge: 100 calls, v1

Authorized 100-call follow-up, shared GBP5 cap, all old evidence unchanged. Freeze exact requests, schedule, protocol, collector, mathematical compatibility checker and analyzer before execution. No extra calls, retries or outcome-driven extensions.

## Requests

40 binary fair-coin calls, HEADS/TAILS, 20 per option order. 60 ternary equal-sector-spinner calls, RED/GREEN/BLUE, 10 per each of six orders. Ten randomized blocks contain two of each binary order and one of each ternary order. Fixed seed 20261015100; saved schedule is authoritative. One Choice question per serial request, independent state, jev-1.14.0, existing endpoint and secure credential. The described outcome is unseen; no actual outcome is generated or known and no answer-accuracy score is possible. The prompts aim to elicit uncertainty, but do not guarantee the model will output fair-event probabilities. Do not instruct the model to produce a target vector or adjust its own probabilities.

## Precise candidate algorithms

H_residual: an unobserved vector u is nonnegative and sums to one; selected c is one of its maxima. Each component is rounded to the nearest hundredth to q, using a common monotone rounding convention. Then only q_c is changed by delta=1-sum(q); the returned probabilities are p_i=q_i for i!=c and p_c=q_c+delta. Selection is unchanged. Reporting may have floating representation error <=1e-12. This is an unconditional algorithm for this analysis, already contradicted as a universal account of history by five saved 0.99 responses; the new test cannot erase those exceptions.

H_plain: same latent-vector selection and nearest-hundredth rounding, without a residual adjustment. Neither model assumes sampling. Passing either model's compatibility check does not identify the server implementation. The reported confidence formula and selected-option float-tail pattern are separate descriptive checks, not assumed proofs of an execution order.

## Compatibility computation

Parse raw numbers as Decimal. Keep raw response untouched. For analysis only, map numbers to nearest hundredth if each is within 1e-12 of that grid. Otherwise report incompatible with these hundredth-based algorithms, not malformed API data. For H_residual require unit sum to 1e-12, then enumerate deltas -0.01, 0, +0.01 (the complete possible hundredth residual set for 2 or 3 normalized components rounded to nearest). Reconstruct q_c=p_c-delta and q_i=p_i otherwise. Require q_c at least every q_i, bounds [0,1], and delta=1-sum(q).

For each candidate, solve for a latent normalized vector within nearest-rounding intervals [q_i-0.005,q_i+0.005] clipped to [0,1], with selected u_c >= all u_i. Compute an exact rational witness. Try intervals shrunk by 1e-9 away from rounding boundaries first. A strict interior witness proves existence under any ordinary nearest tie convention. If only the closed intervals are feasible, record boundary-ambiguous, not refuted or verified, because an unknown common tie convention might disallow it. Enumerate and save all feasible candidates; do not claim to recover actual latent values. Test H_plain with the same feasibility check on the reported grid and no adjustment. A mismatch that has a strict H_residual witness but no H_plain candidate supports residual correction over plain rounding as an explanation of that observation; it does not exclude other mechanisms.

A reported 0.34/0.33/0.33 with a nonchosen 0.34 is NOT a refuter: latent 0.3351/0.3352/0.3297, selection of the second option, rounding to 0.34/0.34/0.33 and subtracting 0.01 from the selected option produce exactly that output. Regression-test this example. Never infer that all pre-correction entries were 0.33 from that observed output. There is no justified universal one-third matching prediction for a separately computed choice.

## Frozen outcomes and opportunity thresholds

Report all attempts, usable replies, request IDs, labels, probabilities, confidence, exact gaps and >0.000001 mismatch flags, ties, hundredth-grid mass, float tails and whether tails belong to the chosen label. Show counts per arm/order/block. Record all H_residual/H_plain compatibility and boundary-only counts and witnesses. Explicitly report model contradictions even if near ties are scarce; do not choose a favorable subset. No statistical significance or population reliability claims.

Observable near tie: top-two margin on the reported hundredth grid <=0.01. Define adequate challenge exposure as at least 15 such ternary calls and at least 10 such binary calls. Also count reported ternary vectors with max-minus-min <=0.02, without inferring hidden rounded vectors. If exposure is below threshold and no contradiction appears, verdict is insufficient near-tie exposure. If exposure is adequate and all are compatible, verdict is compatible in this bounded challenge, NOT confirmed. Any proven no-candidate output contradicts the specified algorithm as an unconditional account of that output. Boundary-only outputs are unresolved. Count cases requiring a nonzero correction among all feasible candidates as stronger discriminating observations; an identity-compatible answer is not evidence that a correction was applied. Descriptive float tails can support an implementation fingerprint, but their absence is not a falsifier and alternative serialization is possible.

## Collection, stops, budget and preservation

Retain every raw response before structural validation. Validate labels per request. Continue on model-hypothesis contradictions and choice/max mismatches: they are study outcomes. Stop on unknown billing, HTTP/transport failure, malformed/unusable response, unexpected model or response-label set; no retry and retain a full-call reserve on uncertainty. Use corrected n-option confidence arithmetic in the copied collector (n=2 or3), rather than the previous ternary-only formula. No old adapter changes.

Published price rechecked: USD0.042 per million input tokens, output free, default64k context; https://docs.typesafe.ai/models. Reserve 65,536 input tokens times GBP2/USD per call = GBP0.005505024. Carry guard GBP0.447300588. Maximum 100-call reserve GBP0.550502400; combined maximum GBP0.997802988 < GBP5. Settle only to valid reported usage. No other paid services. This is conservative usage accounting, not invoice verification.

Preserve source and evidence snapshots separately. Verify old file hashes before/after, including the free audit. Keep failures and all previous totals. No public messaging, no new swarm conclusions, no reopening synthetic JS-003. Stop after the fixed checkpoint.
