# Jev Choice/Probability Consistency Experiments

**Publication draft for owner review — prepared 16 October 2026. Not an official TypeSafe project.**

We ran small, frozen experiments using TypeSafe's typed Choice API with `jev-1.14.0`. The original question was whether several calls with different analytical perspectives, followed by synthesis, would outperform one call or a sequential controller. During repeatability testing, we found responses where `choice` differed from the option with the highest reported probability.

This repository preserves the results, failures and follow-up diagnostics. **The internal cause remains unconfirmed. We have not established swarm superiority.** The latest 100-call rounding experiment was inconclusive.

## The finding in one response

The stopped repeat returned this genuine response:

```json
{"model":"jev-1.14.0","answers":{"decision":{"type":"choice","choice":"ALLOW","confidence":0.04,"probabilities":{"ABSTAIN":0.36,"ALLOW":0.35,"DENY":0.29}}},"usage":{"input_tokens":2409,"output_tokens":41}}
```

The selected option is ALLOW, while ABSTAIN has the highest reported probability. The frozen checker rejected it and stopped the repeat batch. The [exact saved response](evidence/Jev-Live-JL-002-Repeat5/evidence/live-batch/repeat-01/response-0456.json) and request in the adjoining ledger are retained. Its SHA-256 is `2533dd81a40a8a01e9e224cb498737e587cc79b536323bbac133d1e8006211fd`.

This is a disagreement between returned fields. It does **not** establish that the chosen option was below an internal, unrounded maximum. Nor does it establish a safety failure in a deployed application: these were fictional policy cases.

## Every live experiment, including unfinished ones

All calls below were made on 15 October 2026. Counts are API requests, not independent questions.

| Experiment | New live calls | Outcome |
|---|---:|---|
| [JL-001, 24 cases](evidence/Jev-Live-JL-001-live/RESULTS.md) | 217 | Single 18/24; swarm 24/24; sequential 24/24. Swarm and sequential tied. |
| [JL-002 original](evidence/Jev-Live-JL-002/RESULTS.md) | 221 | Stopped when probabilities summed to 0.99. Original failure preserved. |
| [JL-002 R1 continuation](evidence/Jev-Live-JL-002-R1/RESULTS.md) | 644 | Reused the original 221 responses. Across all 96 cases: single 48, swarm 45, sequential 43 correct. Primary clean 64: 33, 30, 29. Frozen favorable-swarm criterion failed; controls degraded. |
| [Five-repeat attempt](evidence/Jev-Live-JL-002-Repeat5/RESULTS.md) | 456 | Stopped at the mismatch above. **0/5 repetitions completed**. First repeat completed 50 whole cases; repeats 2–5 never started. |
| [ABSTAIN diagnostic](evidence/Jev-Choice-Diagnostic-Run-v1/RESULTS.md) | 240 | One mismatch; all 60 simple controls correct. |
| [IGNORE rename diagnostic](evidence/Jev-Choice-IGNORE-Run-v1/RESULTS.md) | 240 | Zero mismatches; all 60 simple controls correct. This did not establish a fix. |
| [Mixed ABSTAIN/IGNORE diagnostic](evidence/Jev-Choice-Mixed420-Run-v1/RESULTS.md) | 420 | Two mismatches, one in each label arm; all 60 simple controls correct. |
| [Corrected rounding challenge](evidence/Jev-Rounding100-Run-v1/RESULTS.md) | 100 | Zero mismatches. Near ties: coin 0/40, spinner 13/60, below frozen minima of 10 and 15. **Inconclusive**. |
| **Total, without counting reused responses twice** | **2,538** | **Four choice/maximum disagreements. All failures retained.** |

The offline [residual-correction audit](evidence/Jev-Residual-Correction-Audit-v1/RESULTS.md) examined the first 2,438 distinct responses before the final 100-call test. It made no new API calls. Its historical wording that the 100-call test had not run was correct when written; the later report supersedes that status.

## What the evidence supports

- Ordinary monotone rounding alone cannot reverse an ordering. **Rounding followed by a correction to the selected option can.** That distinction corrected the earlier interpretation; see [interpretation history](INTERPRETATION_HISTORY.md).
- Across the full 2,538-call record, 47 responses have long numeric tails, all on the selected label. All four displayed ranking discrepancies are approximately 0.01. This is consistent with selected-option arithmetic, but does not identify the server implementation.
- Five earlier responses total 0.99 on the hundredth grid. An unconditional explanation that the service always forces the probabilities to sum to one does not cover the whole record.
- Identical requests sometimes returned different answers. In the partial repeat, 20 of 257 valid requests identical to their earlier counterparts changed selected choice. Those calls include intermediate judgments; they are not 257 independent benchmark cases.
- Replacing ABSTAIN with IGNORE changed output distributions in the mixed test, but did not eliminate mismatches. Both labels still represented insufficient evidence, rather than an instruction to discard evidence.
- Every output in the final 100-call test was compatible with both plain rounding and the specified residual-correction hypothesis. Compatibility is not confirmation.

## What this does not establish

These are exploratory, author-visible fictional fixtures, with correlated templates and repeated requests. They are not a blind benchmark, an independent population sample or evidence of statistical significance, general intelligence, intentional behaviour or deployment safety.

“Swarm” means separate calls to the **same model** with deliberately different prompts and transparent synthesis. “Sequential” means successive typed judgments with prior judgments available. These are not separately trained models or generated prose reasoning traces. The API supplied choices, probabilities and confidence.

Swarm and sequential used equal request counts, but unequal actual token and cost totals. Single used fewer requests. Consequently the original question under exactly matched realized request/token/cost budgets remains unanswered. The harder set also had 32 correlated injection twins of 64 clean cases. No superior result is claimed by pooling them as 96 independent problems.

The four discrepancies occurred across different experiments and were not independently sampled events with a known common rate. Do not read 4/2,538 as a general service failure-rate estimate. The later near-tie analysis of older calls was post hoc. Easy 1/0/0 controls did not exercise the suspected rounding mechanism. The coin/spinner test had no observed physical outcomes to score for correctness.

The returned model string was pinned, but a separate server build/postprocessing fingerprint was not supplied. We cannot determine the sampling, cache, internal probability or correction pipeline from these observations. Historic checks and reported documentation are evidence as of the experiment date, not a guarantee of today's service behaviour.

## What we need TypeSafe to clarify

1. Is `choice` selected from an unrounded distribution, and should it always maximize the **reported** probabilities?
2. Are probabilities rounded separately, then adjusted on the selected option to restore unit sum? Can that invert the displayed ranking?
3. Which field should clients treat as authoritative, including ties and low confidence? How is `confidence` calculated?
4. Why do five earlier outputs sum to 0.99 if normalization is intended, and can server processing vary under a pinned model ID?

No authoritative provider explanation is included in this record. Private request IDs remain available to the owner for a provider trace; public metadata uses consistent aliases.

## Reproduce the analysis without spending anything

Use Python 3.10 or newer, from this repository directory:

```text
python -B verify_publication.py
```

This uses only the Python standard library. It makes no network requests, reads no credential store and does not import the historical live runners. It verifies publication hashes, exact live response preservation, the reused prefix, score totals from saved predictions and answer keys, mismatch counts and the final near-tie counts. See [reproduction details](REPRODUCING.md).

Archived source and snapshots document how the experiments were run. They are **not a turnkey live runner**: local paths have been replaced, credential access is disabled in the copied credential modules, and original freeze hashes are preserved rather than recalculated to conceal edits. Do not treat a publication hash as an original preregistration seal.

## Cost and contents

Total reported usage across 2,538 distinct calls gives **USD 0.222573120** at the experiment-date listed rate of USD 0.042 per million input tokens, with free output. This includes rejected responses and counts the reused prefix only once. It is calculated usage-based cost, not a verified invoice. Final conservative shared budget accounting, including the retained reserve, was **GBP 0.450448908**, below GBP 5. Publication preparation made no paid calls.

- [`RESULTS_SUMMARY.json`](RESULTS_SUMMARY.json): recalculated totals and scores.
- [`LIVE_RESPONSE_INDEX.json`](LIVE_RESPONSE_INDEX.json): every distinct live response, including failures.
- `source/`: privacy-reviewed source revisions, prompts, cases, answer keys and scoring.
- `evidence/`: reports, raw responses, requests/ledgers, intermediate judgments, failures, freezes and analyses.
- `archive-snapshots/`: unpacked historical snapshots, including versions not identical to the loose files.
- [`PUBLICATION_PROVENANCE.json`](PUBLICATION_PROVENANCE.json): original and public hashes, changes and omissions.
- [`PRIVACY_REVIEW.md`](PRIVACY_REVIEW.md): publication edits and checks.
- [`SHA256_MANIFEST.json`](SHA256_MANIFEST.json): integrity manifest for this publication copy.

The earlier JL-001 preparation and mock runs are retained in their original named folders for completeness, but are excluded from the live-response index and all live totals. JS-001/JS-002/JS-003 were synthetic predecessors, are outside this real-model publication scope and have not been modified or re-audited.

No software/data license has been selected for this draft. Inclusion does not grant a new license to third-party material. Full third-party documentation captures and private Discord correspondence are excluded; relevant public documentation is linked below.

## Documentation referenced during the experiments

- [TypeSafe Choice primitive](https://docs.typesafe.ai/primitives/choice)
- [TypeSafe response schema](https://docs.typesafe.ai/sdk/python/api/types/responses)
- [TypeSafe confidence](https://docs.typesafe.ai/confidence)
- [TypeSafe models and pricing](https://docs.typesafe.ai/models)

Historical reports contain the exact interpretations and limitations recorded at each checkpoint. Read this README and the interpretation history first: earlier reports intentionally retain conclusions that later evidence narrowed.
