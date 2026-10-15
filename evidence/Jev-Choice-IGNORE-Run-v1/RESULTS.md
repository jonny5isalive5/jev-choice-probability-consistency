# IGNORE label follow-up: completed; no mismatch observed

240 genuine requests completed against pinned jev-1.14.0, with no retries, transport failures or choice/probability mismatches. All 60 simple controls were correct. All 240 request IDs and raw responses are retained. Five tied maxima were preserved and treated as consistent.

The request-only intervention replaced every uppercase ABSTAIN label/reference with IGNORE, including references in instructions. The option's definition was not changed: it still means the evidence cannot decide. Every other request byte, including option position, remained unchanged. All 240 requests were independently checked against the corresponding earlier request with exactly that substitution. This tests the label and its references together, not the label key alone.

## Comparison with the previous ABSTAIN run

| Measure | ABSTAIN run | IGNORE run |
|---|---:|---:|
| Genuine calls | 240 | 240 |
| Choice/maximum-probability mismatches | 1 | 0 |
| Maximum-probability ties | 3 | 5 |
| Correct simple controls | 60/60 | 60/60 |
| Base request, including identity-order panel | 130 | 130 |
| Base request selected ALLOW | 113 | 85 |
| Base request selected ABSTAIN / IGNORE | 12 | 42 |
| Base request selected DENY | 5 | 3 |
| Distinct base-request full answer objects | 99 | 105 |

The 130 base calls comprise 120 dedicated repetitions plus ten identity-order calls. Do not double count them. Across the dedicated 120-call module, choice counts were ALLOW/ABSTAIN/DENY 106/10/4 versus ALLOW/IGNORE/DENY 78/40/2. Across the balanced 60-call order module they were 20/34/6 versus 21/35/4.

After mapping IGNORE to ABSTAIN only for comparison, 74 of 240 matching schedule positions changed choice: 46 in the repeated-base module, 28 in the order panel, zero in controls. These positions are separate stochastic calls, not deterministic before/after outcomes. The raw answer files were never relabelled.

## Balanced order panel

Ten calls per order. Columns give counts ALLOW / ABSTAIN-or-IGNORE / DENY. Positions are aligned through the rename.

| Renamed order | Earlier ABSTAIN counts | New IGNORE counts | Earlier/new mismatches |
|---|---|---|---|
| IGNORE / ALLOW / DENY | 7/2/1 | 7/2/1 | 0 / 0 |
| IGNORE / DENY / ALLOW | 4/6/0 | 5/4/1 | 0 / 0 |
| ALLOW / IGNORE / DENY | 2/7/1 | 2/8/0 | 1 / 0 |
| ALLOW / DENY / IGNORE | 1/5/4 | 0/8/2 | 0 / 0 |
| DENY / IGNORE / ALLOW | 4/6/0 | 3/7/0 | 0 / 0 |
| DENY / ALLOW / IGNORE | 2/8/0 | 4/6/0 | 0 / 0 |

The earlier mismatch was attempt 227. At the same schedule position in this run, Jev chose IGNORE with probabilities ALLOW 0.28 / IGNORE 0.45 / DENY 0.27, confidence 0.18. Its request ID is trace_ff7e9bdb50eb1fd9. This individual non-mismatch does not erase or repair the earlier incident (trace_33a3b1931e09deec).

## What the result establishes

No mismatch was observed in this renamed-label run. The output mix also differed, particularly in the repeated base request. This is compatible with wording sensitivity, but the runs occurred sequentially rather than interleaving labels, so time/backend variation and response variability remain alternative explanations. One earlier mismatch versus zero new mismatches does not establish that IGNORE fixes the contract issue. No significance, reliability or intelligence claim is made, and no further calls were added after seeing results.

Jev's decision interface does not make the option names opaque identifiers. TypeSafe's Choice documentation explicitly states that option names and their descriptions are both sent to the model. A model can process language for classification without generating conversational text. That documentation supports testing a rename, but does not establish how Jev internally represents these words or why the original response fields disagreed.

The original diagnostic's unresolved issue remains: why can choice disagree with the highest reported probability? TypeSafe must confirm the canonical field and trace the original/new mismatch. This label experiment does not supply that internal explanation.

## Cost, preservation and checkpoint

Reported usage: 459,120 input tokens and 9,386 output tokens. At the rechecked published USD0.042/M input price with output free, calculated cost is USD0.019283040. The conservative GBP2/USD allowance is GBP0.038566080 for this run. Both 240-call diagnostics together cost USD0.038603880 by reported usage. Including all carried earlier guard accounting and the unresolved held reserve, total guard balance is GBP0.372302868, below GBP5. This is usage-based accounting, not a verified invoice.

All 4,852 protected files, including the previous runs, failures and ABSTAIN diagnostic, retain their pre-run hashes. The new design and collector were separately frozen before execution after eight offline checks. Their hashes still match. All responses identify jev-1.14.0; no additional model build fingerprint was supplied in the captured fields. Full source, protocol, payloads, observations, schedule-position comparisons and raw bodies are retained in the evidence pack. No credentials or authorization headers are included. No messages were posted externally.

STOP at this completed checkpoint. Keep both runs, including the earlier mismatch. Do not deploy a label substitution as a proven fix. Await TypeSafe's contract clarification and request trace.

Sources checked:
- https://docs.typesafe.ai/models (price, model and context)
- https://docs.typesafe.ai/primitives/choice (option names and descriptions are model inputs)
