# 10: The analyzer scene

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-20, AT-21, and AT-42.

**App:** site

**What to build:** A manager opens `/analyze/`, and the lights of the scene drift while no trade is graded. The manager grades grade-clarity trade A, and when the verdict "Yes" arrives, the lights settle into two groups, one per side, with the bigger group on the side of behold the lamb. This is the last ticket of the spec. If it cannot ship, the analyzer form keeps the drift of the 404 and the rest of the spec still ships.

**Blocked by:** 04 and 07

**Status:** in-review

- [x] Before a grade the lights move for 6 s and do not settle (AT-20).
- [ ] After the verdict of trade A the lights settle into two groups, with the bigger group on the side of behold the lamb, from a run on the real API (AT-21).
- [x] No file under `apps/pipeline/` and no published file under `clients/` changes against `main` (AT-42).
- [ ] `pnpm check:floor` passes for `cpc` and `norcal`.

## Comments

- Revision of 2026-11-08, Brian: the analyzer scenes leave, so the form hero and the verdict hero keep the static grid (AT-35, AT-44), and `analyzer-scene.ts` and `firstHero` leave with them. Option 2 below no longer applies.

**Where the settled scene sits: option 2.** The fold of site-redesign hides `TitleHero` while a grade runs and under a result. So the form hero is not on the page when the verdict arrives. The coordinator chose option 2 while Brian was offline. Brian can override it with a FAIL in the PR.

- `TitleHero` draws the drift scene while idle and after Edit (AT-20).
- `GradingHero` draws no scene.
- The verdict hero of `AnalyzeResult` draws a `settle` scene of one group per side, from the answer of the API.
- Reason: the PRD says the page sets `scene` on its first hero only. After the verdict the verdict hero is the first hero. Option 2 also keeps the fold and its tests.
- This differs from the PRD row "Analyzer result: no scene". Decision 07 gave the result no scene because "the scene of the form covers it". The fold unmounts the form hero, so that premise does not hold.
- After Edit, the title hero is the first hero again. The verdict hero then keeps the static grid, so the page has one scene (story 41).
- The canvas mounts again with the verdict, so the settle starts from a fresh scatter. The canvas code does not change.

**The groups.** Each group holds the light of the team and one light per factor that leans "for" that side. In a lopsided trade, each side but `gives_more` flares. A `fair` or `win_win` trade has no flare. With the recorded answer to trade A, behold the lamb gets 5 lights, all flared: the team, deal, roster fit, standing, and schedule. Bo Girds gets 1 light. A fair trade can still have groups of different sizes, because the size comes from the factors.

**The eyebrow.** The eyebrow of `TitleHero` is "Trade Analyzer", the name of the tool, as the PRD table says. The PRD gives no other text for the title, so the eyebrow and the title read the same. Brian can decide in the PR.

**Open boxes.**

- AT-21 needs a run on the live API, so the evidence stage records it. The fixture `analyze-response-trade-a.json` is the recorded answer to trade A, and the Vitest tests use it.
- `check:floor` passes for `cpc` with 114 tests. For `norcal`, 108 tests pass, and the 4 known failures on the midseason takeover remain. Ticket 09 fixes them.
