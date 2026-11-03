# 03: The writer rule and the proof on week 8

Spec: `.scratch/matchup-impact/PRD.md`. Acceptance tests AT-9, AT-10, AT-11, AT-12, and AT-13.

**App:** pipeline

**What to build:** A new rule in the writer prompt asks each Matchup of the Week and recap blurb to say the impact of the week for both teams. The writer chooses the parts. The six recaps say the impact in different ways. The Matchup of the Week blurb names the upset once. A real build of week 8 shows that all 7 blurbs say the impact. The build is for proof only and is not published.

**Blocked by:** 01, 02

**Status:** in-review

- [x] The writer prompt has the rule. It names the impact fact as the source of an odds number in a matchup blurb, and keeps rule 23 for the other prose blocks.
- [x] The rule asks for a different shape in each recap, and for the upset in one sentence only.
- [x] The verifier has no new code check. A later ticket adds one only if AT-9 shows a miss.
- [ ] A build of `2026` week 8 records the 7 blurbs, each sentence with its fact IDs, as the evidence of AT-9 to AT-12 in `EVIDENCE.md`.
- [ ] `git diff main -- apps/site` is empty, as the evidence of AT-13. Nothing is published.
- [x] `make check` passes.

## Comments
