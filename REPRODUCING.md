# Offline reproduction

Run `python -B verify_publication.py` with Python 3.10+ from the repository root. No installation, credentials, API access, model calls or payment are required. The verifier only reads files and prints its result.

The verifier independently recalculates live call counts, usage-based costs, choice-versus-reported-maximum discrepancies, numeric-tail counts, non-unit grid totals, headline accuracy from saved predictions and answer keys, and binary/ternary near-tie exposure. It checks the 221 byte-identical reused responses separately and excludes them from distinct-call totals. It checks that all 2,538 indexed live response bodies retain their original SHA-256 hashes, including rejected responses. Current diagnostic request bodies must also be unchanged.

Original JL calls store requests in `ledger.jsonl`; later diagnostics additionally store exact wire bodies as `request.json`. Predicted choices and intermediate judgments remain in predictions, ledgers and response bodies. The frozen scorers, independent case verifiers, hypothesis solver and tests are included under `source/`. Historical mock runs are explicitly named and never included in the live index.

The verifier does not independently establish the truth of provider implementation claims, rerun the model, re-prove every authored gold answer, or reproduce every historical engineering audit. It recomputes the public headline results and validates the packaged evidence. Original gold-generation and independent-verification code and their recorded outcomes remain available for inspection. Repeated calls are observations from the same authored problems, not newly sampled independent cases.

## Three different kinds of hashes

1. Historical freeze and seal hashes identify the original files before publication edits. They have intentionally not been rewritten.
2. `PUBLICATION_PROVENANCE.json` records both original and publication SHA-256 hashes for each copied file, plus whether bytes changed. Its locations are public relative aliases, not private machine paths. Archive origins use `!/` to identify members.
3. `SHA256_MANIFEST.json` records every file in this public copy except itself. It validates the package you received; it is not a signature or independent proof of the experiment date.

Privacy changes can invalidate historical hash references for a modified metadata or source file. Use provenance to understand that difference rather than attempting to repair an original seal. The raw live responses are all unchanged. Original preservation checks are recorded separately; their cross-project path inventories are kept private.

## Archived source is historical

Historical collectors used local source/evidence paths, Windows Credential Manager and a direct TypeSafe API transport. The public copy anonymizes those paths and replaces credential modules with a stub that refuses access. Other transport code is retained for review, not enabled by the public verifier. Do not execute archived live entry points as a reproduction shortcut. A future live experiment would need explicit authorization, fresh pricing/interface checks, a new budget and a separate frozen design.

No GitHub Action, background job, scheduled task or automatic live replay is included. The owner has not approved publication of this draft or chosen a distribution license.
