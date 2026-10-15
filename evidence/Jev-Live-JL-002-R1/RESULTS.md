# JL-002-R1: completed continuation, no favorable swarm result

15 October 2026. All 96 cases now have genuine Jev responses for all three arms.
The separate R1 continuation sent 644 new inference requests and reused the
original 221 responses locally. No inference request was retried or repeated.
The original JL-002 remains a frozen, stopped run; this report describes the
explicitly authorized, separately frozen continuation combining its saved prefix
with the newly completed suffix.

**Result: swarm has a small descriptive accuracy lead over sequential, but fails
the frozen favorable-result criteria and has more false authorizations. Single
scores highest. STOP at this completed checkpoint.**

## Final comparison

The primary comparison is the 64 distinct clean base scenarios. The 32 additional
cases are correlated note-only injection twins, not 32 independent base problems.

| Arm | Primary correct / 64 | Accuracy | All cases correct / 96 | False authorizations, clean / all |
|---|---:|---:|---:|---:|
| Single real Jev answer | 33 | 51.56% | 48 | 1 / 2 |
| Swarm plus synthesis | 30 | 46.88% | 45 | 2 / 3 |
| Sequential critique | 29 | 45.31% | 43 | 1 / 2 |

On the 64 primary cases, swarm wins 4 and loses 3 against sequential: net **+1**,
with 56 identical final answers. The frozen descriptive threshold required at
least +4 and no control degradation. Neither requirement is met: swarm has two
clean-case false authorizations versus sequential's one. On all 96, swarm wins 5
and loses 3 against sequential (net +2), but wins only 1 and loses 4 against single
(net -3). These are observed case counts, not significance or superiority claims.

| Control or secondary measure | Single | Swarm | Sequential |
|---|---:|---:|---:|
| Injected-case correct / 32 | 15 | 15 | 14 |
| Injected-case false authorizations | 1 | 1 | 1 |
| Clean-case wrong abstentions | 5 | 3 | 3 |
| All-case abstentions | 14 | 10 | 8 |
| All-case wrong abstentions | 7 | 5 | 5 |
| Paired injection correct-to-wrong / 32 pairs | 2 | 2 | 2 |
| Paired injection wrong-to-correct / 32 pairs | 1 | 2 | 0 |
| Nominal easy controls correct / 12 | 6 | 5 | 6 |

Low false-authorization counts do not establish reliability. All arms frequently
deny cases whose correct answer is ALLOW or ABSTAIN. Among the 32 true-ABSTAIN
cases, single correctly abstains on 7, swarm on 5, sequential on 3. The easy-control
failures are retained; "easy" describes their authored structure, not empirically
verified Jev difficulty. The detailed confusion tables and every wrong answer are
included in the machine-readable audit and score files.

| Clean family, 16 cases each | Single | Swarm | Sequential |
|---|---:|---:|---:|
| Linked dependencies | 9 | 8 | 7 |
| Scoped exceptions | 6 | 7 | 6 |
| Temporal authority | 10 | 9 | 8 |
| Threshold exclusions | 8 | 6 | 8 |

## Probability contract and isolated correction

The official [TypeSafe SDK response schema](https://docs.typesafe.ai/sdk/python/api/types/responses)
states that Choice probabilities sum to approximately 1. The vendor documentation
does not specify an exact rounding algorithm. Saved probabilities are consistent
with hundredth rounding, including small binary floating-point artifacts.

The original response 221 reported ABSTAIN 0.17, ALLOW 0.02, DENY 0.80, total 0.99.
Its original strict-validation failure remains unchanged. R1 preserves the original
unit-mass tolerance of 0.001; outside that tolerance, it accepts only probabilities
on the observed hundredth grid whose rounding intervals can contain a unit-mass
distribution. For these three-option responses, 0.99 and 1.01 can pass; 0.98 and
1.02 cannot. All other model, usage, option, range, finite-number, confidence and
argmax checks remain. Values, confidence and choices are never normalized or
replaced. This is a bounded compatibility policy, not a vendor guarantee.

Exactly three responses needed this new allowance: sequences 221, 229 and 294,
all totaling 0.99. Response 221 was accepted locally under a labelled R1 receipt;
the new paid calls began at sequence 222, the pending swarm synthesis. The
derived ledger retains the original stopped event followed by this receipt.
There were **zero new failures** and zero retries. The historical failure remains
one; the original run is not rewritten as successful.

## Exact requests, usage and published-price cost

Every one of the 865 responses reports `jev-1.14.0`. The API response includes
model, answers and usage; no separate server fingerprint was supplied. Requests
pin that model and use the direct TypeSafe Choice interface with three output
labels. Intermediate judgments contain choices, confidence and probabilities;
this is not a free-form text reasoning or prose-critique API. The analytical
perspectives and synthesis instructions are the genuine frozen request prompts.

| Allocation | Calls | Input tokens | Output tokens | Listed USD cost |
|---|---:|---:|---:|---:|
| Original smoke | 1 | 390 | 41 | 0.000016380 |
| Single | 96 | 237,044 | 4,034 | 0.009955848 |
| Swarm | 384 | 944,198 | 16,118 | 0.039656316 |
| Sequential | 384 | 979,913 | 16,123 | 0.041156346 |
| Total | **865** | **2,161,545** | **36,316** | **0.090784890** |

Original 221-call cost, including the rejected response: **USD 0.023237424**.
New 644-call continuation: **USD 0.067547466**. Combined: **USD 0.090784890**, about
**GBP 0.06904 (6.9 pence)** using the previously recorded reference conversion of
GBP 0.7604301892533474 per USD. This is usage times published pricing, not an
inspected settled invoice. [TypeSafe model pricing](https://docs.typesafe.ai/models)
is USD 0.042 per million input tokens with free output. Currency reference:
[XE USD table](https://www.xe.com/en-us/currencytables/?from=USD), recorded for
14 October 2026 16:00 UTC; the GBP estimate is not a live settlement quote.

All original reservations were carried forward. The conservative maximum-context
reservation across all 865 attempts is **GBP 4.761845760**, below the combined
GBP 5 ceiling. It reserves 65,536 input tokens per call at GBP 2 per USD; that
allowance is a cap calculation, not the actual exchange rate or actual spend.
No other paid service, top-up or purchase was used.

Swarm and sequential each use four requests per case, identical original evidence,
the same three checklists and the same synthesis. Their only planned difference is
visibility of preceding judgments. Sequential consumed 35,715 more input tokens;
actual token and cost matching is therefore **not exact**. Single uses one call
containing all checklists and is a lower-cost reference. This does not fully settle
the original question under exactly matched realized token/cost budgets.

## Verification, preservation and reproducibility

All 13 engineering checks passed before the continuation. They covered visible-input
answer verification, rounding acceptance and rejection boundaries, preservation of
response values, other contract guards, request isolation, the final budget boundary,
and exact local replay of all 73 existing completed predictions. Replay stopped at
the expected first unmade request in the offline check. Cases, answer key, protocol,
prompts, generator and verifier are byte-identical to the original; arm execution
and scoring functions are unchanged. The new source was frozen before further
live inference at **2026-10-15 19:28:12 UTC**.

The post-seal scorer found no request schedule, prompt, evidence, history isolation,
response hash, prediction seal or budget-reservation discrepancies. All 288 arm
predictions are complete. The original ledger and predictions are exact byte
prefixes of the derived files; all 221 copied raw responses are byte-identical.
The protected-file check confirmed **2,198 original files unchanged**, covering
the existing JS and JL baselines, original JL-002 source and its stopped evidence.
The named Credential Manager key was used only in memory; the new source and
evidence scan found no plaintext secret.

R1 source freeze SHA-256:
`b746eaf2fef340a3851fba94e8580831252388d822e469d7e22cbe4e995f6b23`.

R1 source archive SHA-256:
`bebf1b37d7a8c1ab57f41bf418f3de813996d556f272e0ddbd566f2a42ef15ca`.

Original source freeze remains:
`1a7a569758323d295c12ac5d6172139de91b3f2427be717c3a1646a509ada8ab`.

Source: `source/Jev-Live-JL-002-R1`.
Evidence and delivery: `evidence/Jev-Live-JL-002-R1`.
Key files: `source-before-continuation.zip`, `evidence/continuation-audit.json`,
`evidence/continued-run-001/score.json`, `execution.json`, `ledger.jsonl`,
`predictions.jsonl`, `prediction-seal.json`, all raw `response-*.json` files,
the protection manifests, readiness record and verification console.
The source archive contains the adapter, continuation runner, frozen inputs,
scorer, tests and parent hash manifest. Offline re-scoring uses `python -B score.py`
from the R1 source directory; do not launch further live inference.

This was a non-blind exploratory pilot with author-visible synthetic tasks, four
shared policy families and correlated twins. The engineering correction followed
inspection of partial results and execution was interrupted. The fixed model
string is not a separate backend fingerprint. No statistical significance,
general safety, deployment readiness or emergent intelligence is established.

**Recommendation: STOP.** Preserve this completed negative result. It does not
support a claim that swarm beats sequential without degrading controls, and both
multi-call workflows trail single overall. Any later study requires a separately
authorized, newly frozen task-fit/design check; do not tune or rerun this set.
