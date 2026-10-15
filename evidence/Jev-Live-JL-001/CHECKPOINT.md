# JL-001 checkpoint — 15 October 2026

**Implementation and mock verification complete. STOP: authorized TypeSafe credential unavailable.**

Genuine Jev pilot executed: **NO**. Live smoke executed: **NO**. Inference requests:
**0**. Actual live spend: **GBP 0 / USD 0**. No other paid service was used.
Actual responding model version and vendor fingerprint: **not observed**.

## Delivered

- Active Windows source: `source/Jev-Live-JL-001`.
- Frozen source snapshot: `evidence/Jev-Live-JL-001/source-frozen.zip`.
- Documentation, evidence and this checkpoint: `evidence/Jev-Live-JL-001`.
- Pinned requested model: `jev-1.14.0`, direct documented `/v1/systemone` endpoint.
- 24 frozen objective cases, separate answer key, genuine Choice prompts, isolated
  arm histories, typed intermediate judgments and explicit synthesis.
- One careful single answer; three distinct evidence perspectives plus synthesis;
  four-stage sequential critique/revision. All are calls to the same model.
- Strict response/usage validation, pre-dispatch spend reservation, no automatic
  retries, redirect refusal, error preservation, separate scoring and prediction seal.

The source and scorer were frozen before testing. Ten unit tests passed in one pass.
One mock integration run completed 217 simulated exchanges: one smoke and 216
evaluation exchanges, producing 72 complete arm predictions. The post-seal scorer
reported zero evidence/history audit findings. This is engineering verification,
not scientific acceptance or authentication of the real API contract.

MockTransport deliberately always abstains. Its 8/24 arithmetic per arm is retained
in the raw scorer evidence solely to verify accounting; it is not a Jev result.
Its usage numbers are synthetic and are not real tokens or charges.

## Genuine comparison

| Arm | Genuine completed cases | Genuine requests | Accuracy | Real cost |
|---|---:|---:|---|---:|
| Single | 0 | 0 | Not measured | 0 |
| Swarm with synthesis | 0 | 0 | Not measured | 0 |
| Sequential/self-critique | 0 | 0 | Not measured | 0 |

No inference can be made about whether swarm helps, hurts, matches sequential, or
preserves model-level controls. No significance, emergence or intelligence claim.

## Credential readiness

Checked process, Windows user and Windows machine environment variable names for
TypeSafe/Jev/OpenRouter, plus matching Windows Credential Manager target names.
No matching credential was available. Existing project trees had no discovered
credential/environment file to designate for this pilot. No secret value was
printed, persisted, embedded in source, or transmitted. No broad personal-file
secret search, new account, top-up or purchase was performed.

The live preflight returned exit code 2 with the single readiness blocker before
creating a live-run directory or opening an inference connection. The live gate is
closed in the frozen configuration. This checkpoint does not silently resume when
a credential later appears.

## Pricing and limits

Official TypeSafe documentation read on 15 October 2026 lists Jev 1.14.0 at
USD 0.042 per million input tokens, free output, default 64k per-request and 32k
per-question context. Source URLs and a web-tool capture are retained in `docs`.
Each attempt reserves 65,536 tokens at that tariff and a conservative allowance of
2 GBP per USD. The full 217-attempt allocation is GBP 1.194590208; the absolute
guard is GBP 5. This is a reservation calculation, not an actual FX quote or bill.
Tariff/currency/tax coverage must be reconfirmed at a future live readiness check.

The raw Python documentation download failed with a certificate-expired error.
That error is retained. Official pages were read through the web tool; TLS checks
were not disabled. The authenticated inference transport remains untested.

## Fairness and limits

The three arms have equal original evidence and common request/token/cost ceilings.
Swarm and sequential each use four requests; single uses one. Actual token use is
not exactly equal, and the mock audit correctly flags it. A literal one-call arm
cannot consume four actual requests without becoming a different baseline or
wasting calls. This implementation provides a common-budget exploratory comparison,
NOT proof under exactly equal realized requests/tokens/cost. Exact matching remains
a limitation of the requested interpretation and must not be represented as solved.

The sequential critique is typed re-evaluation, not generated reasoning. There is
no documented free-text answer, seed or temperature control in the used interface.
The 24 cases share templates; they include author-visible ground truth, eight each
ALLOW/DENY/ABSTAIN and twelve untrusted-note controls. The design is small, narrow,
non-blind and not a representative general-intelligence or real-world benchmark.
Source boundaries are audited code paths, not OS isolation. No external reviewer
or additional personnel were used.

## Preservation and recommendation

All 586 files in the seven protected D:/E: trees matched their pre-work SHA-256
hashes. This was preservation checking only. JS-001, JS-002 and JS-003 were not
edited or rerun; the JS-003 acceptance audit was not reopened. Its accepted status
remains non-blind descriptive adaptive-workflow evidence: primary 882/960,
transfer 876/960, F=S=H=HS, distributed superiority withdrawn, real Jev untested.

**STOP live work at credential readiness.** Once an authorized TypeSafe credential
is available through local environment or a designated secure store, the next
bounded action is to verify account/tariff readiness and perform one contract smoke
under the existing GBP 5 authorization. Any continuation must preserve this frozen
checkpoint and errors; there is no automatic rerun, correction cycle or spending.

Main evidence: `evidence/unit-tests.txt`, `evidence/readiness.json`,
`evidence/live-readiness-check.txt`, `evidence/mock-run-001/ledger.jsonl`,
`evidence/mock-run-001/predictions.jsonl`, `evidence/mock-run-001/prediction-seal.json`,
`evidence/mock-run-001/score.json`, and `evidence/protected-after.json`.
