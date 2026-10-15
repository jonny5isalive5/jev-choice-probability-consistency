# Independent check of the residual-correction hypothesis

Verdict: strong evidence for a chosen-option rounding adjustment, but the proposed always-normalizes mechanism is incomplete across the saved history. No new API calls or spend. The proposed 100-call experiment has not been run.

Opus identified an important mechanism missing from Codex's earlier investigation. Ordinary monotone rounding cannot reverse an ordering, but rounding followed by a selected-option sum correction can. The previous diagnostics establish disagreement between displayed fields; they do not establish that the internal choice was below the unrounded maximum. Treat selected-option residual correction as a leading, testable explanation of the four observed mismatches, not confirmed server behavior.

## Scope and independent verification

Read 2,438 distinct saved genuine live responses, all naming jev-1.14.0. Verified that the first 221 R1 responses are byte-identical reused copies and counted them only once. Included JL001, original JL002, the 644 newly executed R1 calls, the 456-call partial repeat, both 240-call diagnostics and the mixed 420-call diagnostic. Excluded mock runs and synthetic JS experiments; JS-003's scientific audit was not reopened. All 8,270 protected files still match their hashes. The read-only script and complete row-level extraction are preserved separately here.

| Run | Unique calls | Long numeric tails | Tails on nonchosen label | Grid total not 1 | Choice/max mismatches |
|---|---:|---:|---:|---:|---:|
| JL001 | 217 | 1 | 0 | 0 | 0 |
| JL002_original | 221 | 5 | 0 | 1 | 0 |
| JL002_R1_new | 644 | 10 | 0 | 2 | 0 |
| Repeat5_partial | 456 | 6 | 0 | 2 | 1 |
| ABSTAIN240 | 240 | 6 | 0 | 0 | 1 |
| IGNORE240 | 240 | 6 | 0 | 0 | 0 |
| Mixed420 | 420 | 10 | 0 | 0 | 2 |

Across all saved genuine calls: 44 long numeric tails, all on the selected option; four choice/max disagreements, all approximately 0.01; none above 0.01 allowing only floating-point epsilon. For the latest 420 calls, independently confirmed all ten tails reproduce a decimal-grid value plus/minus 0.01 in Python float arithmetic. This is strong diagnostic evidence of selected-field arithmetic, though the precise original code and intermediates are not observable.

## The free check found five counterexamples to ALWAYS forcing unit sum

Every one of these is 0.99 on the hundredth grid, far beyond a floating-point residue:

- Original JL002 call 221: ABSTAIN 0.17, ALLOW 0.02, DENY 0.80.
- New R1 call 229: ABSTAIN 0.28, ALLOW 0.04, DENY 0.67.
- New R1 call 294: ABSTAIN 0.28, ALLOW 0.05, DENY 0.66.
- Repeat5 call 204: ABSTAIN 0.54, ALLOW 0.05, DENY 0.40.
- Repeat5 call 293: ABSTAIN 0.23, ALLOW 0.08, DENY 0.68.

The first was already the reason for the preserved R1 mass-tolerance revision. None of the three recent diagnostics has a 0.99/1.01 grid total. This limits an unconditional universal normalizer claim; it does not disprove that residual correction caused the four mismatches. Conditional processing, an earlier implementation, caching or another path would need evidence from TypeSafe. The pinned model ID alone does not identify the server postprocessing implementation. Exact counterexample paths and hashes are in counterexamples.json.

## What Opus got right, and needed qualifications

1. The 420-call fingerprint is independently reproduced. All ten tails are on the chosen label. The two mismatches are algebraically compatible with subtracting 0.01 from a rounded tied winner. Call 230 is compatible with adding 0.01 to a rounded tied winner. These are reconstructed candidates, not observed pre-correction values. Several inverse candidates exist for many ordinary responses, so the original vector is not identified.

2. Confidence supports the reported-distribution calculation. In all 420 calls, reported confidence matches Python round((max(reported probabilities)-1/n)/(1-1/n),2). The analogous selected-probability calculation matches 418, missing exactly the two discrepancies. Confidence is therefore not independent evidence against the correction hypothesis. It does not by itself prove when in the pipeline confidence was calculated. Without rounding, 189 values do not equal the exact formula, so 'equals the formula' needs that reporting-rounding qualification.

3. The mixed-run near-tie count is 40 using a top-two margin <=0.01 on the hundredth grid. The conditional rate is 2/40; the overall rate remains 2/420, and each arm's overall rate remains 1/210. These answer different questions. The original denominator was not wrong. This near-tie definition is post hoc and uses reported outputs; do not retroactively make it the original endpoint.

4. The strict 0.000001 checker measures a real displayed-field discrepancy under the documented highest-probability contract. A one-cent reporting grid does not itself license rank inversion; the additional sum-adjustment mechanism can explain it. Do not silently relax frozen checks or assume which field is authoritative without the provider's contract. An eventual documented rounding-aware client policy would be a separate revision.

5. All 60 simple controls were deterministic 1/0/0 responses and cannot challenge the proposed near-tie correction mechanism. Their correctness still verifies basic handling of easy known outcomes. It is not evidence of safety or reliability near ties. Zero failures in a 240-call run does not establish a fix; the quoted roughly 30% zero-event probability is conditional on independent events with a fixed assumed 0.5% rate, not an established model of these calls.

6. The complex case's correct policy answer is ALLOW. Independent record resolution finds waiver_valid is the only unknown, while permit_valid is true. Both possible waiver completions authorize the operation. Thus post hoc correctness in the mixed study is 77/180 for ABSTAIN and 54/180 for IGNORE. The rename moved selections away from the correct answer in this one case. This does not change any frozen score or create a general accuracy claim; it was not a prespecified diagnostic endpoint. Details and both completions are in audit.json.

7. If the suspected correction is label-independent, that does not mean labels cannot affect the chance of encountering it. Labels changed reported distributions; that can change how often near ties and non-unit rounded totals arise. Wording sensitivity and label-independent postprocessing can coexist.

8. 'Choice is probably more faithful' is conditional on selection actually using the unrounded maximum. It does not make that choice policy-correct. Approximate +/-0.01 reporting error under a particular three-option correction algorithm concerns error relative to the hidden probability vector, not calibration or real-world accuracy. 'Fairly harmless' is not established by these data.

## Important flaw in the proposed spinner falsifier

A reported 0.34 / 0.33 / 0.33 vector with the 0.34 option NOT chosen does not refute the proposed correction mechanism. A concrete counterexample:

- True vector A=0.3351, B=0.3352, C=0.3297; total exactly 1; choose B, the true maximum.
- Round to hundredths: A=0.34, B=0.34, C=0.33; total 1.01.
- Subtract 0.01 from selected B: A=0.34, B=0.33, C=0.33.

The reported maximum is A despite selection of B, entirely under the proposed algorithm. We cannot observe that all three pre-correction values were 0.33 merely from a 0.34/0.33/0.33 output. Therefore that condition cannot be used as an observable entry criterion or an automatic refutation. Also, separate calculations need not be independent, so a universal one-third matching prediction for 'computed separately' is unjustified.

## Recommendation for the proposed 100 calls

Do not run the pasted protocol unchanged. Its binary/ternary comparison remains useful, but first specify the candidate correction algorithm precisely and freeze only predictions observable from returned fields. Test whether outputs are compatible with that algorithm; do not pretend the unobserved rounded vector is known. Record all possible inverse candidates and preserve ambiguity. Define near-tie opportunity and an inconclusive threshold using reported quantities, without interpreting the 0.34/0.33/0.33 pattern as proof of pre-correction 0.33/0.33/0.33. State that gross non-unit totals refute an ALWAYS-normalizes algorithm, which has already failed on five earlier calls; a conditional explanation remains unconfirmed.

The proposed 100-call reserve is correctly GBP0.550502400, taking the current carried guard GBP0.447300588 to at most GBP0.997802988 at the existing conservative assumptions. This audit spent zero and leaves that balance unchanged. No new protocol has been executed or approved by this audit.

The most direct provider question is: 'Do you round probabilities to two decimals and assign the rounding residual to the selected option? If so, can this move it below another reported probability, which field is canonical, and why do some earlier responses still sum to 0.99?'

Sources reviewed: https://docs.typesafe.ai/primitives/choice and https://docs.typesafe.ai/confidence. The public documentation still describes the highest-probability choice; it does not establish the hypothesized residual-correction implementation.
