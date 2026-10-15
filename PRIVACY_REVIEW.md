# Publication privacy and integrity review

This is a separately prepared publication copy. The original source, design freezes, runs, failures and evidence archives remain private and unchanged. No experiment was rerun and no original score or response was corrected for publication.

## Publication edits

- Personal names and local machine paths were replaced with neutral placeholders or repository-relative aliases.
- The credential-store locator was removed; copied credential-reader modules were replaced with a stub that refuses access. No credential value is included.
- Exactly 1,000 captured provider request IDs were replaced consistently with stable `trace_` aliases. Aliases preserve cross-file joins but cannot be used for a vendor trace. The private ID mapping remains with the owner and is outside the repository.
- Private Discord links and the posting draft were removed. No Discord screenshots, usernames or private third-party correspondence were added.
- Cross-project preservation inventories, selected account-setup metadata and full third-party documentation captures were omitted. A reason and original hash are retained in provenance. Public documentation links replace the copied documentation.
- Original zip containers were not copied blindly. Their contents were inspected and are represented by loose files or unpacked historical snapshots. Duplicate archived copies are not counted as additional live observations.

Every copied artifact has original/public hashes and a modification flag in `PUBLICATION_PROVENANCE.json`. Original freeze manifests are historical records; privacy edits can make their references differ from this publication copy. They were not resealed.

All 2,538 indexed genuine live response bodies retain their original bytes. Cases, prompts, answer keys, predictions and captured request bodies also retain their bytes. The originally rejected responses, partial-repeat predictions, mock records and later counterevidence are included. Mock records and the 221 reused responses are excluded from distinct live-call totals.

## Checks performed

The local review compares the publication copy with the existing API credential in memory, including common encodings; it does not print, save or submit that credential. It scans every public file for common API/token/private-key formats, literal credentials, personal identifiers, local paths, private trace IDs, emails, IP-address patterns and credential-bearing URLs. It also checks candidate high-entropy strings. All bundled text is readable; original archives are unpacked rather than left as unexamined payloads.

The public offline verifier checks the complete publication manifest, provenance hashes, unchanged live responses, reused-prefix identity, headline scores, usage totals, mismatch totals and near-tie counts. All included Python sources parse; archived collectors are not executed. Documentation links inside the new overview are checked against the package.

The dated review outcome and counts are recorded in `PUBLICATION_REVIEW.json`. The publication directory contains no Git history, remote configuration, automatic workflow or credential file. No GitHub repository, release or upload has been created by this preparation.

## Scope and limits

Experimental timestamps, fictional cases, option labels, returned model IDs, public API URLs, token counts, costs and technical hashes are intentionally retained. These are relevant research metadata. A stable trace alias does not anonymize the content of a fictional request, and hashes are integrity identifiers, not signatures.

Automated scanning and manual inspection cannot prove the absence of every unknown secret or identifying inference. The exact stored-key comparison covers the currently configured experiment key, not all credentials that could ever have existed. The owner should review this copy before publication. The review does not grant a software/data license or imply TypeSafe endorsement.

Only this `repository/` directory, or its separately checked publication zip, is intended for public release. Private preparation files in the parent review directory must not be uploaded.
