# 03: What hit rate and what false-flag rate let Jev into the flow?

Map: `.scratch/evidence-flags/MAP.md`.

**Kind:** grill

**Blocked by:** 02, 06

**Status:** done

## Question

The spec needs a bar for the replay that Jev must meet before `evidence.md` runs it. A miss costs what it costs now, because the Judge still catches the gap. A false flag costs the agent about 1 min of one more look. Brian decides the hit rate and the false-flag rate from the numbers of ticket 02. He also decides what happens to the spec if Jev fails the bar.

## Decision

Brian decided on 2026-11-10, in a grill of two questions.

1. A question enters the flow if, on the replay at its cut, it catches at least half of the past gaps of its kind and flags 10% or fewer of the PASS tests.
2. On the replays of tickets 02 and 06, (a) the facts, (b) motion, and (d) the Observation per sentence meet the bar. (c) cut-off text does not, at 14% false flags. The build gives (c) one more draft, scoped to the text that the Then line names. It enters the flow only if it meets the bar on the replay again. Otherwise it leaves the spec.
3. The replay becomes the command `cornerstone evidence-flags-eval`, in the shape of `advisor_eval`. It runs the final question module on the past rounds. An acceptance test records its output, so the Judge sees the rates of the final questions, not of the drafts.
4. A question that misses the bar on that run is not asked by `evidence.md`. If no question meets the bar, the spec ships the command and the eval only, and the flow stays as it is.
5. Each new spec adds labels: each flag in `FLAGS.md` and the Test verdict of the Judge. The eval reads them too. A cut changes only through a later ticket, never in the middle of a spec.

Reason: a miss costs what it costs now, and a false flag costs about 1 to 3 min and can never cause a FAIL. So the bar is loose on false flags. The drafts of (b) and (d) were tuned on the cases that scored them, so the final module must prove its rates again in the build, with no wait for later specs.
