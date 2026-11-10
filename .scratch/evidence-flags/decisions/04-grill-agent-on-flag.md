# 04: What does the evidence agent do on a flag, and what is the loop limit?

Map: `.scratch/evidence-flags/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

On an Evidence flag, the agent can record the evidence again, record why it disagrees, or stop and ask Brian. The spec needs the rule for each case, and a limit on the loops for each test. It also needs to say if the flags and the disagreements go into `EVIDENCE.md`. The Judge reads that file, and a flag there can bias the Judge.

## Decision

Brian decided on 2026-11-10, in a grill of three questions.

1. The agent takes one action for each Evidence flag:
   - A real evidence gap: change `steps.json` or the command, then record that test again.
   - A real product defect: hand it to the orchestrator as a fix group before the Judge runs, then record the test again.
   - A false flag: write one line about why the agent disagrees, then go on.
2. The agent never stops to ask Brian about a flag. A flag is advice, and the Judge is still the gate. A stop for each flag brings back the waits that this spec removes.
3. The limit is one loop per test. After one new recording, Jev runs once more. If the flag stays, the agent writes its disagreement line and goes on. A product defect is outside the limit, and the limit starts again after its fix merges.
4. The flags and the disagreement lines go into `.scratch/<slug>/FLAGS.md`, never into `EVIDENCE.md` or `evidence/`. The Judge reads neither `FLAGS.md` nor any flag, so the Judge stays fresh. Each entry gives the test, the question, the probability, the reason, and the action. `FLAGS.md` is committed with the evidence. The PR body gives one line of counts.

Reason: a flag in a file that the Judge reads tells the Judge where to look. One loop caps the cost of a false flag that stays. `FLAGS.md` also gives the data to tune the cuts after a few specs.
