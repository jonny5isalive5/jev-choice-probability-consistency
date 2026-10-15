# Mixed ABSTAIN versus IGNORE: completed, mismatch observed with both labels

All 420 genuine calls completed against jev-1.14.0 using the prospectively frozen mixed schedule. The choice/maximum-probability mismatch occurred once under ABSTAIN and once under IGNORE. Renaming the option did not eliminate the issue in this test. Both new failures are preserved with server request IDs.

## Main results

| Measure | ABSTAIN | IGNORE |
|---|---:|---:|
| Total calls | 210 | 210 |
| Complex-case calls | 180 | 180 |
| Mismatches, all calls | 1/210 | 1/210 |
| Mismatches, complex calls | 1/180 | 1/180 |
| Correct simple controls | 30/30 | 30/30 |
| Complex-case ALLOW choices | 77 | 54 |
| Complex-case cannot-decide choices | 85 | 126 |
| Complex-case DENY choices | 18 | 0 |
| Complex-case mean cannot-decide probability | 0.367222 | 0.399556 |
| Complex-case maximum-probability ties | 7 | 7 |

Both mismatch gaps are approximately 0.01, above the predeclared 0.000001 tolerance; they are not merely tiny binary floating-point residuals. The 14 tied maxima are separately retained and treated as consistent. All 60 simple controls were correct, with no mismatch. All calls returned HTTP200, all 210 pairs completed, and there were no retries or extra smoke calls.

The complex-case cannot-decide selection rate was 47.22% with ABSTAIN versus 70.00% with IGNORE. Mean probability assigned to that meaning increased by 3.233 percentage points. This is descriptive within this one case/configuration, not a claim that IGNORE is better or more correct. There was no prespecified accuracy endpoint for the complex case.

## Traceable mismatches

1. Attempt 67, pair 34, block 5, ABSTAIN arm, order ABSTAIN / DENY / ALLOW, first in pair.
   - Sent 2026-10-15 21:32:43.676086 UTC; captured 21:32:44.004137 UTC.
   - Choice DENY; probabilities ABSTAIN 0.35, DENY 0.33999999999999997, ALLOW 0.31; confidence 0.02.
   - Request ID: trace_606cef358f57ea21
   - Response SHA-256: 5e7d9cb7f4e57c8c8bc6ed018f035329d40a2021346c7be173ea27e4bd8b34a9
2. Attempt 180, pair 90, block 13, IGNORE arm, order IGNORE / ALLOW / DENY, second in pair.
   - Sent 2026-10-15 21:33:36.683878 UTC; captured 21:33:36.983731 UTC.
   - Choice ALLOW; probabilities IGNORE 0.38, ALLOW 0.37, DENY 0.25; confidence 0.07.
   - Request ID: trace_dca45bd815f27e8c
   - Response SHA-256: 683e36d9f4e97b6b5cc4025c9a245182f3f5672b33badb149f39407ae530278b

The symptom therefore is neither confined to the literal label ABSTAIN nor exclusively a selection of ALLOW. Ordinary consistent monotone rounding cannot explain the selected option ranking below another reported probability. These data do not identify sampling, separate calculations, label mapping or another server mechanism. TypeSafe's internal request trace is still needed.

## Balanced option-order results

Each row contains 30 matched pairs. Choice counts are ALLOW / cannot-decide / DENY; IGNORE is mapped to the cannot-decide meaning only in this derived table. Raw responses remain unchanged.

| ABSTAIN option order | ABSTAIN counts | IGNORE counts | Mean cannot-decide probability change (percentage points) | ABSTAIN / IGNORE mismatches |
|---|---|---|---:|---|
| ABSTAIN / ALLOW / DENY | 24/5/1 | 22/8/0 | +1.467 | 0 / 1 |
| ABSTAIN / DENY / ALLOW | 23/5/2 | 15/15/0 | +3.967 | 1 / 0 |
| ALLOW / ABSTAIN / DENY | 6/20/4 | 1/29/0 | +4.633 | 0 / 0 |
| ALLOW / DENY / ABSTAIN | 4/17/9 | 3/27/0 | +2.700 | 0 / 0 |
| DENY / ABSTAIN / ALLOW | 16/12/2 | 10/20/0 | +3.533 | 0 / 0 |
| DENY / ALLOW / ABSTAIN | 4/26/0 | 3/27/0 | +3.100 | 0 / 0 |

Mean cannot-decide probability was higher under IGNORE in all six option orders. It was higher by 3.000 percentage points in the 90 complex pairs where ABSTAIN came first, and by 3.467 points in the 90 where IGNORE came first. This direction is therefore not confined to one option position or which variant was sent first.

Of the 180 complex pairs, 72 selected different normalized choices. ABSTAIN-to-IGNORE transitions (with meanings normalized) were: cannot-decide to cannot-decide 71; ALLOW to cannot-decide 40; ALLOW to ALLOW 37; cannot-decide to ALLOW 14; DENY to cannot-decide 15; DENY to ALLOW 3. All controls had unchanged correct meanings. Full block, first-arm, order and paired probability results are in analysis.json; all call observations are also exported to observations.csv.

## What the experiment supports and does not establish

Interleaving variants and balancing their first/second positions reduces the separate-run timing explanation. The consistent direction across all six orders and both first-arm groups supports sensitivity to the label-and-reference wording for this case. It does not establish a general effect across tasks, human-like understanding, a significance result, or exact backend invariance. All repetitions reuse one complex case, so 180 pairs are not 180 independent tasks.

Two mismatches establish that the IGNORE rename is not a complete remedy. The earlier zero-in-240 IGNORE result remains valid as a bounded non-observation, not proof of a fix. Equal observed mismatch counts here do not establish equal underlying failure rates. The low event count cannot establish reliability or the internal mechanism.

This diagnostic is not a swarm-versus-sequential comparison, and it does not justify reopening or changing any frozen benchmark.

## Cost and preservation

Input tokens: 892,830. Output tokens: 17,028. At the rechecked published USD0.042/M input price and free output, usage-based cost is USD0.037498860. Conservative GBP2/USD allowance for this run: GBP0.074997720. Carried guard accounting, including prior spend allowances and the earlier unresolved reserve, is GBP0.447300588, below the GBP5 cap. This is calculated from reported usage, not a verified billing invoice.

All 6,101 protected files match their pre-run hashes. The new design and source freezes also remain unchanged. All 420 exact request bytes match the frozen schedule, and each matched pair differs only by ABSTAIN-to-IGNORE replacement. Independent extraction from raw response bodies agrees with the collector. Request IDs are captured for all 420 calls; all responses name jev-1.14.0. No additional provider model-build fingerprint was supplied in the captured metadata.

The separate source-snapshot.zip, design-snapshot, raw live-run-001, analysis.json, observations.csv, verification.json and evidence-pack.zip preserve the implementation and result. TypeSafe-mixed-mismatches.zip contains just the two traceable mismatch requests/responses and relevant metadata for manual sharing. No secrets or authorization headers are saved. Nothing has been posted externally.

## Checkpoint

STOP here with all results retained. Ask TypeSafe to inspect the two request IDs, confirm the canonical field and explain the divergence between selected option and reported distribution. Do not deploy IGNORE as a proven fix or add a threshold to the old benchmarks. No further live calls are part of this completed run.

Sources rechecked before execution:
- https://docs.typesafe.ai/models
- The original documented Choice contract: https://docs.typesafe.ai/primitives/choice
