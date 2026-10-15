# JL-002 Repeat5

Five new serial executions of the same frozen 96-case experiment, authorized by
[REDACTED_PERSON] on 15 October 2026. Retain every tie, reversal, control failure and error.
Read repeat_protocol.json for the frozen prospective analysis and spending rules.

The ten inherited files are byte-identical to JL-002-R1. Use repeat.py and
analyze.py as the entry points. The inherited pilot.py and score.py CLI paths are
historical and must not be used; their imported functions provide unchanged arm
execution and scoring. No old project or evidence file is written by this runner.

Run tests with python -B -m unittest test_repeat -v after the source freeze.
Run the complete offline dummy campaign with python -B repeat.py. This is transport
verification only: its dummy answers are not intelligence evidence. Live execution
uses python -B repeat.py --live and requires authenticated readiness plus the
existing named Windows credential. Each batch directory is exclusive; no automatic
retry, replacement, overwrite, resume or further campaign is permitted.

After the whole live batch is sealed, python -B analyze.py scores every repeat
without modifying the originals. The same 64 base questions repeated five times
are not 320 independent questions. The original completed run is shown separately.
Actual request counts are equal for swarm and sequential; realized tokens/costs
can differ. Repetition measures stability of this fixed workflow, not general
intelligence or population-level superiority. Backend sampling, service caching
and hardware are not controlled by this client. No random seed is invented.

Spending: one global journal reserves the documented full-context maximum before
each network call. Only a validated response releases the excess reservation.
An error retains its full reservation and stops all remaining work. Use reported
input usage at USD 0.042/M and a conservative GBP 2/USD allowance; outputs are free.
The shared GBP 5 cap also includes the prior JL-001 and complete JL-002 cost once.
Predicted cost is not a guarantee of completion: the guard stops before any call
whose worst-case charge would cross the cap. No other paid service is used.

Source: source/Jev-Live-JL-002-Repeat5
Evidence: evidence/Jev-Live-JL-002-Repeat5
