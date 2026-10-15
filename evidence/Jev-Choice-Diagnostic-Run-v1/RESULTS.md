# Jev choice diagnostic: completed, internal cause unresolved

All 240 genuine requests completed against jev-1.14.0. One response selected ALLOW while ABSTAIN had the highest reported probability. This reproduces the original symptom on a request that differs only in criteria ordering. It does not reproduce the mismatch in the 130 byte-identical original requests, and it does not establish the provider's internal cause.

| Module | Calls | Choice/probability mismatches |
|---|---:|---:|
| Exact original replay | 120 | 0 |
| Balanced option-order panel | 60 | 1 |
| Simple controls | 60 | 0 |

The order panel includes ten additional requests byte-identical to the original, giving 130 original-byte requests overall. Those 130 produced 113 ALLOW, 12 ABSTAIN and 5 DENY choices, with 99 distinct full answer objects. All 60 controls were correct and each control's answer object was identical across its 20 repetitions. Three maximum-probability ties were retained and treated as consistent. There were no HTTP or transport failures and no retries.

## New traceable mismatch

Attempt 227, block 10, order-3, criteria order ALLOW / ABSTAIN / DENY.

- UTC sent: 2026-10-15T21:16:08.893337+00:00; response captured: 21:16:09.274505 UTC.
- Request ID: trace_33a3b1931e09deec
- HTTP 200, returned model jev-1.14.0.
- Choice ALLOW; confidence 0.02.
- Raw probabilities: ALLOW 0.33999999999999997; ABSTAIN 0.35; DENY 0.31.
- Gap: 0.01000000000000003, exceeding the original checker's 0.000001 tolerance.
- Request SHA-256: 9f3cf33c46d7c2335d380278b6e2dcf6321fa08c281497556745488fe0cadf81
- Response SHA-256: 5800568c53b53b78859a8fe708422974d1484b07d005568851262a82d7221add
- Semantic canonical request SHA-256: 22f8df52d803fdfd13b0aafab16147664984443109813bbac5230d958f6b000d, matching the original request.

The approximately 0.01 reversal is present in the server body, not introduced by scoring or display rounding. Ordinary consistent monotone rounding cannot reverse the order. Floating-point representation of 0.34 does not explain why 0.35 ranks above the selected option. Sampling, separately computed estimates, label mapping and other server processing remain possible explanations requiring provider evidence.

## Balanced order panel: descriptive observations only

Ten calls per ordering; same semantic content. The large original replay module is not pooled into this balanced table.

| Criteria order | ALLOW | ABSTAIN | DENY | Mismatches |
|---|---:|---:|---:|---:|
| ABSTAIN / ALLOW / DENY | 7 | 2 | 1 | 0 |
| ABSTAIN / DENY / ALLOW | 4 | 6 | 0 | 0 |
| ALLOW / ABSTAIN / DENY | 2 | 7 | 1 | 1 |
| ALLOW / DENY / ABSTAIN | 1 | 5 | 4 | 0 |
| DENY / ABSTAIN / ALLOW | 4 | 6 | 0 | 0 |
| DENY / ALLOW / ABSTAIN | 2 | 8 | 0 | 0 |

Choice frequencies differed across orderings in this sample. With only ten calls per order and a single mismatch, this does not establish an ordering defect or explain the mismatch. No significance test, population reliability claim or swarm-superiority conclusion is made. No confidence gate, fourth option, answer replacement or scoring change was introduced.

## Cost and preservation

Reported usage: 460,020 input tokens and 9,998 output tokens. At the rechecked published rate of USD 0.042 per million input tokens with free output, calculated cost is USD 0.019320840. This is usage-based cost, not a verified account invoice. The conservative GBP 2 per USD accounting allowance is GBP 0.038641680 for this run. Including the earlier guard balance and its unresolved reserve, total guard accounting is GBP 0.333736788, below GBP 5.

All 3,630 protected files (including the original studies, failures and frozen design) still match their pre-run hashes. All 240 wire payloads match the scheduled files exactly. All responses and diagnostic headers are retained; request IDs were captured for every call. The independent analyzer agrees with the collector on every extracted choice and mismatch. All responses named jev-1.14.0. No additional provider build fingerprint was supplied in the captured fields. cf-cache-status was recorded; it does not establish anything about model-level caching.

The new collector and analyzer were frozen before live execution following seven successful offline tests. source-snapshot.zip preserves that implementation. Original benchmark adapters and evidence were not edited. No original benchmark continuation was attempted.

## Recommendation

STOP further calls at this completed checkpoint. Send TypeSafe the traceable mismatch packet when the user chooses to post it. Ask which field is canonical, whether the highest-probability contract applies, and for the full-precision selection vector, reported-probability vector, selected index/label mapping and any sampling, fallback or serialization steps for this request ID. A provider trace is needed to answer why the fields disagreed; this run supplies a new incident they can trace. No message has been posted automatically.

Sources rechecked before execution:
- https://docs.typesafe.ai/models
- https://docs.typesafe.ai/primitives/choice
- https://docs.typesafe.ai/sdk/python/api/types/responses
