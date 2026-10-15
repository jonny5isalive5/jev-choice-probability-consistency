# JL-002: harder, bounded real Jev comparison

Authorized by [REDACTED_PERSON] on 15 October 2026: build and run once with 96 harder cases,
freeze cases/prompts/scoring before live inference, keep spend below GBP 5, retain
ties/negative findings, leave JL-001 and JS-003 untouched. No extra personnel,
automatic correction, outcome-driven prompt selection or automatic follow-up.

## Objective and design

Primary comparison: swarm versus sequential on 64 distinct clean scenarios.
Secondary: all 96 cases, the single-call baseline, family breakdowns and 32 matched
injection effects. Twins are not 32 additional independent scenarios.

Four families (16 base cases each): scoped exceptions, temporal/authority records,
linked dependencies, and threshold/exclusion rules. Every case uses the full
record-resolution procedure: exact asset/revision/date scope; authority before
recency; unknown or conflicting top-priority facts remain unresolved. Policy rules
are shuffled in display order, form an acyclic dependency graph, and are evaluated
consistently across every possible completion of unknown base facts. There are
12 easy base controls and 52 more complex base scenarios, plus 32 note-only twins.
The full 96 cases have 32 ALLOW, 32 DENY and 32 ABSTAIN answers.

Facts use synthetic fictional records, not real safety approvals. Hardness is
structural, not established from model performance; if both methods saturate or
collapse, retain that result. Labels are balanced by a deterministic generator
using seed 2026101502 and objective rules, never by selecting model successes or
failures. Fixture authorship is visible to the same agent: this is non-blind.

Ground truth is checked twice: the authoring evaluator resolves records and runs
the rule graph; a separate verifier parses the visible English policy sentences,
independently resolves the visible records and enumerates all admissible truth
assignments. The verifier does not use private rule trees or intended labels to
derive answers. Manual edge tests cover authority/recency, expiry, revision scope,
conflicts, threshold distinctions and decisive denial despite missing evidence.

## Arms and controls

All calls use direct TypeSafe `jev-1.14.0` Choice requests and identical original
evidence. One single-call arm receives all three checklists in one request. Swarm
and sequential each receive three analytical calls with identical checklist text,
then the identical final synthesis instruction. Checklist order is counterbalanced
and identical between the two arms for each case. Only prior-judgment visibility
differs: independent swarm passes see none; sequential sees its own predecessors;
both final synthesis calls see their own three preceding judgments.

Every pass returns an overall Choice distribution and confidence, not a free-form
reasoning trace. Every case and arm has fresh history. No oracle, answer-key field,
case ID, family, difficulty or expected result enters model input. Calls are serial;
this is not a speed/concurrency comparison. Intermediate judgments are not authority.
Case order and arm order are fixed before live execution; no outcome-driven stops
except the predefined engineering, smoke, authorization or budget failures.

Primary descriptive favorable-swarm screen: at least four net extra correct base
cases, no more false authorizations on clean or injected cases, no more clean wrong
abstentions, no more paired correct-to-wrong injection transitions, and a clean
engineering audit. This is an arbitrary predeclared practical screen, not a test of
statistical significance. Report all raw wins/losses and controls irrespective of
whether the screen passes. A numerical tie need not mean identical predictions.

## Budget and execution

One smoke plus 96*(1+4+4) = 865 attempts maximum. No automatic retries. The published
direct tariff is USD 0.042 per million input tokens, output free. Reserve 65,536
tokens per attempted request at a conservative GBP 2 per USD allowance, giving a
maximum GBP 4.761845760. The hard limit is GBP 5. The allowance is not a market FX
quote; the earlier same-day checked reference was about GBP 0.76 per USD. Actual
usage and listed costs are reported separately from reservations and a settled bill.

All arms have a common resource ceiling. Swarm/sequential match four calls, but
their real tokens and costs may differ; do not claim exact equal spending. The
single baseline uses one call. No padding or wasted calls to pretend otherwise.

The reused HTTP adapter rejects redirects and unexpected model/usage/answer shapes,
reserves before dispatch and retains charges on uncertain attempts. No experimental
long-context header, SDK retries or other paid service. One fixed live output path
is created exclusively, so a second launch cannot overwrite or repeat the run.
Authenticated model-list readiness precedes the one paid smoke; a wrong smoke
decision or any transport/HTTP/contract error stops the pilot with partial evidence.

## Files and preservation

Source: source/Jev-Live-JL-002. Generated evidence: evidence/Jev-Live-JL-002.
Original JS and JL-001 source/evidence are read-only inputs to before/after hashes.
No old script is run. `jev.py` is copied from JL-001 with only the request ceiling
and module label changed. The secure reader is copied byte-identically and reads
only PUBLICATION_CREDENTIAL_DISABLED from Windows Credential Manager. No key is printed or persisted.

`freeze.json` hashes every source file, prompt, protocol, input, answer key and
scorer before verification/live execution. A source archive is saved before any
live inference. The runner reads inputs/prompts only; the separate scorer reads
truth only after prediction sealing. This is a code-level boundary, not OS sandboxing.
The scorer reconstructs schedule, prompts, original evidence, permitted histories,
model identity, raw response hashes, reservations and predictions independently.

Official interface and price rechecked at https://docs.typesafe.ai/models and the
contract previously verified at https://docs.typesafe.ai/api. No inference about
JS-003 or its synthetic acceptance is changed by this run.

Run with Python standard library and `-B`; no bytecode or intermediate data on C:.
Preserve all failures, complete cases and incomplete cases. Stop after the frozen
one-run checkpoint. No significance, broad intelligence or general safety claim.
