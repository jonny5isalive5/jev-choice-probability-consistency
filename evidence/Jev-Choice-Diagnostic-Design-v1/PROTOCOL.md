# Jev choice disagreement: diagnostic design v1

Status: DESIGN ONLY. No live calls made. Existing studies and failures are paused and preserved pending TypeSafe clarification. This protocol does not authorize execution or resume the five-repeat benchmark. Freeze an implemented collector and offline checks separately before any authorized live run. Any provider clarification that changes this design requires a new version; retain this one.

## Question and known observation

Why did the server return choice ALLOW while its probabilities ranked ABSTAIN highest?

The retained response says ALLOW, confidence 0.04, probabilities ABSTAIN 0.36 / ALLOW 0.35 / DENY 0.29. The earlier identical request returned ABSTAIN, confidence 0.06, probabilities 0.37 / 0.30 / 0.33 respectively. Raw response bytes already contain the disagreement: it is not introduced by the downstream scorer. Ordinary consistent monotone rounding cannot reverse the ordering. These observations do not identify sampling, separate estimates, a label mapping defect, or another server implementation issue.

This is a response-contract diagnostic, not a new swarm comparison or an evaluation of intelligence. Correctness of the fictional decision and consistency of the response fields are separate questions. Do not infer why the server chose ALLOW from whether ALLOW happens to be the policy-correct label.

## Fixed experiment: 240 requests

Ten blocks of 24 requests, in the committed schedule.json order. One Choice question per request, serial transport, fresh isolated state, model jev-1.14.0, original endpoint POST https://api.typesafe.ai/v1/systemone. No feedback, retries, repairs, batching, prior answers, or undocumented generation parameters.

| Module | Requests | Purpose |
|---|---:|---|
| Exact replay | 120 | Reuse original request bytes, including the original fictional evidence. Establish whether the same disagreement recurs. |
| Option order | 60 | All six orders of the same three criteria, ten calls each. Change only criteria object member order; preserve labels, meanings and evidence. Look for position-related disagreement. |
| Simple controls | 60 | Twenty each with one known true, known false, or unknown eligibility fact. Checked answers are ALLOW, DENY and ABSTAIN. Check that any issue also occurs on simple inputs. |

Each block has 12 exact replays, one of each option order, and two of each control. Fixed shuffle seed 20261015. Saved schedule is authoritative, not future regeneration. The identity order duplicates the original payload, so there are 130 identical original requests in total; these are 130 observations, never counted twice. Analyze the balanced 60-call order module separately when comparing positions. Within each control label, repeat the identical frozen payload.

Send saved bytes verbatim. Do not sort JSON keys in transport: doing so would erase the intended order manipulation. Save both exact wire hashes and a semantic canonical hash. JSON object order may be ignored by the server; no detected order effect is not proof that order never matters. No label renaming, extra NONE option, confidence gate or prompt repair in this design. ABSTAIN is an explicit option with a defined meaning; it is not an automatic API uncertainty fallback.

## Collection and checks

Before implementation is sealed, test the new collector locally against saved responses and mocked transport. Confirm raw bytes are captured before parsing or validation; a recorded mismatch does not get rewritten. Verify all payload hashes, ordering and schedule counts. Do not edit or import code in a way that writes to original source trees.

For each attempt record attempt/block/module, exact request hash and bytes, UTC start/end, endpoint, client revision, non-secret transport configuration, HTTP status, raw response body, and an allowlist of diagnostic response headers. Capture x-typesafe-request-id, model name, any provider-exposed build/fingerprint, actual usage, latency and billed/estimated cost. Record missing fields as missing. Never save authorization headers, credentials, cookies, or unreviewed full headers. Avoid enabling server caching or new features; document observed cache metadata if available. Do not invent a fingerprint or determinism setting.

Parse response numbers as decimals. Independently parse archived bytes to verify extraction. For each structurally usable response record choice, all probabilities, confidence, the set of maximum-probability labels, and gap = maximum probability minus probability assigned to choice. Ties count as consistent if choice is in the maximum set. Record exact positive gaps, plus whether they exceed the original checker's 0.000001 tolerance. Never normalize probabilities or replace choice with argmax.

Record probability mass and confidence-formula discrepancies separately, with explicit rounding intervals. The documented three-option confidence formula is 1.5*p_max - 0.5. Its agreement with a reported distribution does not identify how choice was generated. Keep rounding assumptions visible and do not reinterpret reported confidence as a calibrated probability of correctness.

Record control correctness separately from field consistency. A wrong control answer can have mutually consistent response fields; a correct answer can have inconsistent fields.

Unlike the frozen benchmark, this separate diagnostic deliberately records a choice/argmax mismatch and continues the fixed schedule: observing such mismatches is its purpose. This never relaxes the original benchmark checker. Stop on unknown billing, authorization failure, transport uncertainty, malformed/unusable response or unexpected model version. Preserve all attempts and partial results. No automatic retry, correction or discretionary extension after inspecting outcomes.

## Interpretation fixed in advance

| Observation | What it supports | What it cannot establish alone |
|---|---|---|
| Mismatch present in raw HTTP body | Disagreement originates upstream of our decision extraction | Which internal server stage caused it |
| Exact request yields varying fields or choices | Observable response variability | Sampling versus changing backend, nondeterministic computation or separate estimates |
| Mismatch/choice tracks option position in balanced order module | Sensitivity associated with option order | A mapping defect versus ordinary order-sensitive inference |
| Mismatch also occurs on simple controls | The issue is not confined to the complex original fixture | A general rate across tasks or all Jev versions |
| Mismatches cluster at small margins | Association with near ties | That ordinary rounding caused a reversed order, or that a threshold fixes the API |
| No mismatch observed | Failure not reproduced in this bounded run | That the original failure is invalid or the contract is reliable |

Report every attempt, usable response, error, choice, tie, mismatch and reversal. Show denominators, mismatch counts by module/order/control/block, gap values and response variability for byte-identical requests. Include the full original failure next to new observations. Use descriptive counts only; no significance, independence or population reliability claims. This small sample may miss rare failures. A non-reproduction ends the run rather than triggering more calls.

## Decisive provider-side check

Ask TypeSafe which field is canonical and whether the documented highest-probability choice rule applies to this exact API/version. For an identified mismatch request, ask them to inspect the full-precision vector used for selection, the vector used for reported probabilities/confidence, the selected internal index and its label mapping, the rounding/serialization path, and any sampling draw, fallback, cache or routing step. Ask whether choice and probabilities came from the same computation and actual backend build. Their trace can distinguish competing internal explanations; client repetition cannot do so conclusively.

The original response had no captured request ID. Supply its UTC window (2026-10-15 around 19:45:11 UTC), model, exact request SHA-256 and original response hash. Future captured request IDs should make new incidents directly traceable. Do not post private account details or secrets. No message has been sent as part of this design.

Success means a trace-supported explanation of where the fields diverged, or an explicitly unresolved finding with reproducible evidence. An unsupported story such as 'it took a risk because the data was fictional' is not an explanation established by this test.

## Budget and execution gate

No spend is authorized by this design request and no live calls have been made. Before any later authorized run, recheck model availability, exact price, context/token accounting, billing permissions and any minimum charges. Use only the existing authorized secure credential store. If cost cannot be bounded confidently, stop before sending.

At the reviewed published price of USD 0.042 per million input tokens and free output, a conservative 65,536-token reserve per request is USD 0.002752512. With an intentionally conservative conversion ceiling of GBP 2 per USD, 240 calls reserve GBP 1.321205760. This is a conditional planning bound, not a billing guarantee. The retained repeat-batch guard balance is GBP 0.295095108, including earlier costs and the unresolved failed-call reserve. If all these assumptions remain valid, combining it with this entire diagnostic reserve gives GBP 1.616300868, below GBP 5. Keep that earlier reserve held; never reset the budget to hide previous spend. If other spend has occurred, reconcile it before execution. No other paid services.

## Sources reviewed for the design

- Choice contract: https://docs.typesafe.ai/primitives/choice
- Confidence formula: https://docs.typesafe.ai/confidence
- Model pin, context and pricing: https://docs.typesafe.ai/models
- Request ID and raw response access: https://docs.typesafe.ai/sdk/python/api/types/responses

## Preservation

protected-files.json records hashes of existing source/evidence and the Discord report package without modifying them. This design and its frozen offline payloads live separately on E:. Original JS-001/002/003, JL-001, JL-002, R1, Repeat5 and ChoiceCheck are not edited or rerun. No five-repeat benchmark continuation is implied. The pause is a recorded checkpoint, not a claim that filesystem permissions have been changed.
