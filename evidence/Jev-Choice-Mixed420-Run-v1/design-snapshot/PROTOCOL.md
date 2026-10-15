# Mixed ABSTAIN versus IGNORE, 420-call protocol v1

Authorized to run 420 calls under GBP5 total, preserving every result and all earlier studies. Freeze this protocol, exact payloads, schedule, collector, tests and independent analyzer before any live call.

## Design

Thirty blocks of fourteen serial calls. Each block contains one adjacent pair for each of six criteria orders of the original complex case, plus one adjacent pair for a simple control. In each pair, one ABSTAIN request and one IGNORE request use identical evidence, definitions and option positions. IGNORE differs only by the exact uppercase ABSTAIN-to-IGNORE substitution everywhere in that request. This changes the label and its references together; it does not change the definition to mean disregarding evidence.

There are 180 complex pairs (30 per order) and 30 control pairs (10 per known outcome). Total 210 calls per label, each with 180 complex calls and 30 controls. All simple-control options remain in the original fixed order; the six-order balance applies to the complex case. First label is randomized subject to exact counterbalance: 15 ABSTAIN-first and 15 IGNORE-first pairs per complex order, and 5/5 per control type. Pair order within each block and placement of control types are shuffled using seed 20261015420. The saved schedule is authoritative. Send saved bytes without sorting JSON keys. No batching or simultaneous calls, prior judgments, feedback, retries or extra smoke calls.

The study uses existing fixed payloads from the completed ABSTAIN and IGNORE diagnostics, with no new case selection. All calls use POST https://api.typesafe.ai/v1/systemone, jev-1.14.0 and one Choice question. Per-question state is isolated. Pairing puts the two labels close in time; randomizing and balancing which comes first reduces systematic time/order confounding but does not prove backend invariance or independence.

## Prespecified analysis

Two separate descriptive endpoints: (1) choice versus reported maximum probability mismatch rate per label, and (2) difference in choice frequencies and reported probabilities after mapping IGNORE to ABSTAIN only in derived analysis. Never rewrite raw responses. Compute Decimal gaps, record all exact positive gaps, and separately count those exceeding the previous checker's 0.000001 tolerance. Tied maxima are consistent when the selected label is among them.

Report all attempts, usable replies, failures, ties, mismatches, confidence and probability mass/rounding diagnostics, usage and request IDs. Show complex cases separately from controls. For each label and complex option order, report choice frequencies and mean normalized probabilities. For each complete pair, report normalized choice transition and IGNORE-minus-ABSTAIN probability changes, including mean change for the cannot-decide option. Report control correctness for each label and each control. Break descriptive results down by block and which label went first. Incomplete pairs stay in individual-call accounting and are excluded only from paired comparisons with explicit counts.

No significance threshold, population reliability claim, answer repair, confidence gate, auto-extension, or 'fixed' verdict based on zero mismatches. Report magnitude and direction without selecting favorable subsets. A persistent difference would support wording sensitivity for this one case and configuration; it would not prove language understanding, general model behavior, or the internal cause of a contract mismatch. If both labels show mismatches, the issue is not confined to ABSTAIN. This does not evaluate swarm superiority.

## Collector and stopping

Reuse a separately copied revision of the verified collector: capture raw response before parsing, exact request/response hashes, timestamps, model and allowlisted diagnostic headers, especially x-typesafe-request-id. Validate the response labels against that individual request. No secrets, authorization headers or unreviewed complete headers are saved. Record missing fingerprint as missing. Mismatches are observed and retained without halting. Stop on authorization/billing uncertainty, transport uncertainty, malformed/unusable response, wrong response-label set or unexpected model version, and retain any uncertain full-call reserve. No automatic repair or retry. Preserve partial pairs if halted.

## Budget

Current published price rechecked at https://docs.typesafe.ai/models: USD0.042/M input tokens, output free, default64k context without the long-context header. Reserve 65,536 input tokens per call at GBP2/USD: GBP0.005505024 per call. Carry previous guard GBP0.372302868 including earlier held reserve. Maximum new reserve for 420 calls GBP2.312110080; combined maximum GBP2.684412948, below GBP5. Settle only to validated reported usage. No other paid services. Usage-based cost is not an account-invoice verification.

## Preservation and completion

Old JS/JL studies, failures, both 240-call diagnostics and their designs remain unchanged. New artifacts are separate. Before and after, verify hashes of protected files. Preserve source and evidence archives. Stop after the fixed 420 calls regardless of outcome. No external posting or messaging.
