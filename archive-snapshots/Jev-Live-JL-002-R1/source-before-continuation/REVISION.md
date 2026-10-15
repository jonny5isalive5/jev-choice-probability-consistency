# JL-002-R1: authorized adapter correction and suffix continuation

[REDACTED_PERSON] authorized checking rounded probabilities, a separate adapter revision,
and completing the remaining cases within the original combined GBP 5 cap.

The official TypeSafe Python SDK ChoiceAnswer schema documents probability values
that sum to approximately 1: https://docs.typesafe.ai/sdk/python/api/types/responses
The generic Choice documentation says sum to 1. Neither specifies the rounding
algorithm. Saved JL-001 and JL-002 values lie on a hundredth grid, apart from tiny
binary floating-point artifacts. Original response 221 sums to 0.99. We therefore
describe hundredth-rounding compatibility, not proven vendor internals.

R1 preserves the old <=0.001 unit-mass acceptance. For larger discrepancies only,
every probability must be within 1e-12 of a hundredth value and the sum of the
clipped [value-0.005, value+0.005] intervals must contain 1. With three options,
this permits reported totals 0.99 and 1.01 but rejects 0.98 and 1.02. All original
range, finite-number, option, argmax, model, confidence and usage checks remain.
No probability, confidence or selected choice is normalized or replaced.

The original source, failed run and raw response remain untouched. parent.json
seals their hashes. The derived continuation copies the old ledger verbatim,
including its stopped event, then appends a labelled local R1 revalidation of
response 221. It copies the 73 existing predictions byte-for-byte. Existing
requests and prediction histories must replay identically in memory. Only the
unmade suffix starts network requests: sequence 222, JL2-015 swarm synthesis.
No paid call is repeated, no retry or new smoke is added. A maximum of 644 new
calls plus the original 221 gives the unchanged 865-attempt ceiling. Prior spend
and all 221 conservative reservations are carried forward. Maximum combined
reserve GBP 4.761845760, using USD 0.042/M input tokens, free output, 65536 reserved
input tokens per attempt and a conservative GBP 2 per USD allowance.

Cases, truth, protocol, prompts, arm execution functions and scoring functions
are unchanged. Only the scorer CLI output path and the unit-test temporary path
move into R1. The old pilot CLI is retained as historical source but is not the
continuation entry point; use resume.py exclusively. The adapter was amended
after seeing the partial results; this is a disclosed engineering correction,
not a fresh blind trial or independent replication. No result-dependent prompt,
case, scoring, decision-threshold or synthesis changes are made. The interruption
and later suffix execution limit interpretation even with a pinned model name.

Freeze every R1 source file before continuation. Preserve successful responses,
errors, negative findings and ties. Stop on any subsequent contract or transport
failure without automatic correction. Record original and incremental costs
separately, including response 221 exactly once. No other paid service is used.
