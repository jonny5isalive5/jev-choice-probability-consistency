TypeSafe Jev Choice mismatch: observed response and exact request

Purpose: clarification of selected choice versus reported probabilities.
No message has been sent or posted by Codex. This package is prepared for the
user to share with TypeSafe through Discord.

request.json: exact canonical JSON request body sent to the direct TypeSafe API.
response.json: byte-identical HTTP 200 response body containing the mismatch.
prior-response-same-request.json: earlier raw response to the identical payload.
metadata.json: model, endpoint, client-side UTC timestamps and SHA-256 hashes.
Discord-message.txt: suggested accompanying message.
MANIFEST.json: file hashes for this package.

No API key, Authorization header, credential-store data, account ID or local
filesystem path is included. The request contains one fictional policy/evidence
case, not customer records. No live call was made while preparing this package.

The mismatch was observed at approximately 2026-10-15 19:45:11 UTC. The request
ID/response headers were not captured by the original adapter. Client reservation
and response-processing timestamps are included; they are not server timestamps.

This is an observed example, not a guarantee of deterministic reproduction.
The returned choice was ALLOW at reported probability 0.35, while ABSTAIN was
reported at 0.36. Confidence was 0.04 and the probabilities sum to exactly 1.

Expected relationship according to current documentation: choice is the option
with the highest probability. Please clarify whether choice and probabilities
can legitimately use different internal estimates, how rounding/ties are handled,
and which field is authoritative when they disagree.

Documentation checked on 15 October 2026:
https://docs.typesafe.ai/primitives/choice
https://docs.typesafe.ai/sdk/python/api/types/responses
https://docs.typesafe.ai/confidence

The research run was paused, its raw evidence retained, and no new choice
tolerance or substitution was applied. All original experimental files remain
untouched. The experiment comparison itself is not part of this support request.
