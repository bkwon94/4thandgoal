# Evidence stage capture

Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Execution checkout HEAD: `85d54d463a6bb111bb37c58bd810c24d1d9f4131`.
Background full check start: `2026-11-12T20:54:16.841501+00:00`.
Static recapture time: `2026-11-12T20:55:02.451097+00:00`.
The static collector runs after the full background check starts.
The full check command and launch metadata appear in `background-check-start.json`.
The full-check process ends with exit 2; the repository check remains incomplete.
Its full log and completion metadata appear under `infrastructure/`.
This worker runs pure Python and read-only Git commands only.
The exact README-rule reruns finish before this recapture; their raw logs appear under `AT-4/`.
No dependency command starts in this worker while the full check owns the shared environment.
Preparation before the background check supplies no separate acceptance result.
The fixed implementation diff excludes later evidence formats and ticket status updates.
No cold task trial runs; the infrastructure record remains separate from task evidence.
