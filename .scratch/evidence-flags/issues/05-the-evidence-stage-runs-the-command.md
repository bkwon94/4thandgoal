# 05: The evidence stage runs the command, and the ADR records the data

Spec: `.scratch/evidence-flags/PRD.md`. Acceptance tests AT-15 to AT-21, and Implementation Decisions "The workflow skills", "FLAGS.md", and "The record".

**App:** pipeline.

**What to build:** The evidence stage of `cpc:implement` runs `evidence-flags` on every site test after the runner round, and on each pipeline test after its output is saved. The agent takes one action for each flag: a new recording for an evidence gap, a fix group for a product defect, or one disagreement line for a false flag. It never stops to ask Brian, and it gets one loop per test. `FLAGS.md` goes into the evidence commit, and the PR body gives one line of counts. The Judge brief does not change. A new ADR records that the evidence and its shots go to TypeSafe, and that an Evidence flag is never a Test verdict.

**Blocked by:** 02.

**Status:** in-review

- [x] The diff of `evidence.md` shows when to run the command, and the commit of `FLAGS.md` with the evidence (AT-15).
- [x] The diff of `evidence.md` shows the three actions, and no entry at `open` at the evidence commit (AT-16).
- [x] The diff of `evidence.md` shows no stop on a flag, one loop per test, and the rule for a product defect (AT-17).
- [x] The diff of `pr.md` shows the line of counts (AT-18).
- [x] `git diff main -- .claude/plugin/skills/implement/judge.md` is empty (AT-19).
- [x] The new ADR names the data that goes to TypeSafe, the names of managers in the shots, and the rule that a flag is never a Test verdict (AT-20).
- [x] `rg -il 'jev|evidence-flags' .claude/plugin/skills` lists only `implement/evidence.md` and `implement/pr.md` (AT-21).
