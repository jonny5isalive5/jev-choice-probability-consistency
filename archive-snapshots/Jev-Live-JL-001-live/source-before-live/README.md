# JL-001: bounded TypeSafe Jev 1.14 decision pilot

Prepared on 15 October 2026 under [REDACTED_PERSON]'s live-Jev directive. This is a separate
project beside frozen JS-001/002/003. No old experiment is rerun or patched.

This checkpoint is MOCK VERIFIED / LIVE BLOCKED pending an authorized TypeSafe
credential. Do not interpret any mock response, mock score, or mock usage as Jev
performance. MockTransport always selects ABSTAIN and does not solve cases.

## Actual interface

Direct POST https://api.typesafe.ai/v1/systemone with Bearer authorization held
only in memory. Explicit model `jev-1.14.0`. State and questions use the official
Choice schema. The response must identify that exact model, contain all requested
answers and their full probabilities/confidence, and report input/output usage.
No chat endpoint, generated rationale, temperature, seed, hidden reasoning or
undocumented system fingerprint is invented. The vendor model ID and local
source/config/request/response SHA-256 hashes are recorded; vendor weight identity
and determinism cannot be independently established from this interface.

Official references read on 2026-10-15:
- https://docs.typesafe.ai/models
- https://docs.typesafe.ai/api
- https://docs.typesafe.ai/primitives/choice
- https://docs.typesafe.ai/concepts/state

The documentation capture is in evidence/Jev-Live-JL-001/docs. A failed local
documentation fetch is preserved separately; TLS validation was never disabled.

## Frozen evaluation and arms

24 small fictional policy decisions across eight domains: eight ALLOW, eight DENY,
eight ABSTAIN. Twelve contain untrusted instruction-injection notes. Missing facts,
equal-authority contradictions, known disqualifiers and vetoes are explicit.
Hand-assigned answers are checked by enumerating possible worlds from actual
input records. This is an author-visible exploratory set, not a blind benchmark.
Templates and domains are correlated; 24 cases do not establish significance.

Each arm gets exactly the same original policy and evidence. Case IDs, labels,
rationales and control classification are never transmitted. State resets between
cases and arms. Execution rotates through all six arm orders. No outcome-driven
case removal, prompt tuning, retries, repair or review cycle is permitted.

- Single: one careful Jev overall decision, checking all rules.
- Swarm: three distinct calls on affirmative evidence, disqualifiers and evidence
  sufficiency, followed by a fourth Jev call that synthesizes their typed judgments
  against the original evidence. Same model weights in every call. These calls
  are independent in information flow; dispatched serially to reduce operational
  complexity, so this does not measure a concurrency latency advantage.
- Sequential: four calls by the same model: initial decision, strongest
  counterexample, full ambiguity/precedence recheck, final evidence-based revision.
  Each call can inspect preceding typed judgments, never another arm's results.

There is no free-form self-critique in Jev. The critique consists of instructed
re-evaluation with logged revised Choice distributions. Synthesis is transparent
through logged inputs, prompts and outputs; it is not an explanation of internal
reasoning. All arms can abstain. Outputs cannot execute actions or grant authority.

## Resource fairness and spend

All arms have the same maximum allowance: four requests per case and the default
context limit per request. Swarm and sequential use exactly four; single uses one.
Equal ceilings do NOT mean equal realized usage. A literal one-call baseline cannot
also use four requests. The one-call result is a resource/accuracy reference. The
primary swarm/sequential comparison matches requests but its actual tokens may
differ due to prompt/history length. The scorer reports this explicitly. No padding,
extra wasted calls, or false exact-budget claim is allowed. An exact-token-matched
causal claim remains unavailable from this preparation.

Published price: USD 0.042 per million input tokens; output free. Each attempt reserves
65,536 tokens (conservatively covering the documented 64k default), at an intentionally
conservative 2 GBP per USD including overhead allowance. This is NOT a quoted FX rate.
217 attempts (one smoke plus 24 x nine) reserve GBP 1.194590208; absolute ceiling GBP 5.
Zero automatic retries, redirects or experimental long-context headers. Reserve
before dispatch; retain reservations on error/timeout; stop on any HTTP, contract,
model-version or usage error. A future live launch must reconfirm tariff and that
the reserve covers currency/taxes/account terms. No top-up, purchase or other paid
service is authorized by this preparation.

At this checkpoint live_gate_open is false. Credentials alone cannot silently open
the frozen gate. The next operator must resolve the recorded credential blocker,
verify the authenticated contract with one affordable smoke call, and record an
explicit new freeze if changing readiness. Existing authorization does not need to
be requested again merely to perform that bounded readiness work.

## Files and verification

`jev.py`: strict adapter, credential lookup, reservation ledger, transports.
`pilot.py`: prompts, arm isolation, one-shot run and prediction seal.
`build_cases.py`: fixture authorship and independent world enumeration.
`cases.json` / `answer_key.json`: separate input/key; no runtime oracle import.
`score.py`: separate post-seal scoring plus evidence/history/usage audits.
`test_pilot.py`: negative contract, cost, error, credential-redaction and isolation tests.
`freeze.json`: exact code, prompt, data, key and scorer hashes before verification.

Use Python 3 standard library. Set TEMP/TMP to [LOCAL_PATH_REMOVED]
Run only with `python -B` to avoid generated bytecode. Outputs belong under
evidence/Jev-Live-JL-001, outside the clean D: source. Output directories are exclusive:
the runner will not overwrite an earlier run. After a failure, preserve evidence and
stop; this checkpoint does not authorize an automatic rerun.

Separate scoring happens only after predictions are sealed. The scoring process can
read the answer key; the runner does not. This is a code-level boundary, not an OS
sandbox or an independent human custodian. Expected metrics are accuracy, paired
wins/losses, abstentions, false authorizations, injection-control errors, real request
counts, input tokens and listed usage cost. No p-values or general-intelligence claims.

Reuse is limited to canonical JSON/SHA-256 and the preservation/seal pattern from
the audited harness. Synthetic oracles, frame padding, policies and runtime patching
do not fit the real API and are not imported. JS-003 acceptance remains non-blind,
descriptive adaptive-workflow evidence; F=S=H=HS, primary 882/960, transfer 876/960.
Distributed superiority remains withdrawn; real Jev was not tested there.
