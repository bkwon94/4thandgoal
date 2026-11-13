# 08: The scoring component fact names the component

Spec: `.scratch/week-8-fixes/PRD.md`, part 5. The rankings fallback in the third build of ticket 05.

**What to build:** The power rankings fact `PR.<n>` says "1st in scoring" for the scoring component, which
averages points for, the all-play rate, and the mean margin. The writer reads it as most points, and the
verifier rejects the claim against `S.<n>`. Rename the component in the fact text to "the scoring component",
so the writer cannot read it as a points rank.

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] `power_rankings.py` or the fact builder: "in scoring" becomes "in the scoring component" in the `PR.<n>` text. Name the module in the close comment.
- [ ] The writer prompt example for the rankings chapter, if it quotes the old text, changes with it.
- [ ] A test shows the fact text.
- [ ] `make golden` ran, and the golden diff is named in the close comment.
- [ ] `make check` passes.

## Comments

Stays open in the audit of `todoist-queue` on 2026-11-12, as ready-for-agent. Brian kept it, because it fixes a real bug or changes what a manager sees.
Proof: `COMPONENT_WORDS` in `packages/rankings/python/src/rankings/chapter.py` still maps `scoring` to "scoring", and `tests/test_sheet.py` still expects "5th in scoring".
Read 1 file: .scratch/todoist-queue/audit.md.
