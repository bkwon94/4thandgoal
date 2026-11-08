# 10: Floor, scope checks, and glossary

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-27, AT-28, AT-29, AT-31, and AT-32.

**App:** site

**What to build:** The floor check covers the new open states: an open game card, an open ladder card, an open Index list row, the stage, and the Season So Far dial. Both clients pass it. The out-of-scope checks prove the manager hero, the pipeline, and the repo stay clean. `GLOSSARY.md` gains Open card, Grade dial, Trend tile, Ready halo, Index list, and the race groups In, Bubble, and Out.

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08, and 09

**Status:** ready-for-agent

- [ ] `CLIENT=cpc pnpm check:floor` and `CLIENT=norcal pnpm check:floor` pass with the new open states.
- [x] No page scrolls sideways at 390 px, and each new control is 44 px or more.
- [x] The manager hero diff against `main` is empty.
- [x] `git diff main --stat -- apps/pipeline packages/*/python` is empty.
- [ ] The Scrolltide copy search over the diff finds no match.
- [x] `GLOSSARY.md` holds the new terms, each with one meaning.
- [x] `make check-fast` passes.

## Comments

- 2026-11-08, cpc:implement: Brian chose to build this ticket before 09. The floor check covers every open state except the stage, which waits for ticket 09.
- 2026-11-08, ticket 10 build: The first box stays unticked, because the stage of ticket 09 does not exist yet. The floor covers each other open state: the open game card, the open ladder card, the open first row of the Index list, the open strip of weeks, and the Season So Far dial on the manager page. `CLIENT=cpc pnpm check:floor` passes 105 tests and `CLIENT=norcal pnpm check:floor` passes 103. Ticket 09 adds the stage to `FULL_FLOOR_PAGES` and to the count test.
- 2026-11-08, ticket 10 build: The floor found failures that tickets 01 to 08 left. The chip counts of the Index list had a height of 0, so axe gave no verdict. The rank text of each Grade dial arc sat over an SVG node, so axe gave no verdict. The Open card overview and the grade read of an open row were 14 px prose on a phone. The ladder tap matched two buttons. The fix gives the count `leading-none`, draws the blades as HTML boxes with the same geometry, moves both prose lines to `text-lead`, and names the head in the ladder selector.
- 2026-11-08, ticket 10 build: The Scrolltide box stays unticked. The search of eight-line runs finds no match, but only the Team Roster excerpt, the Health Tracker notes, and the item notes are on disk. The prompts of Showcase Card, Lime Metrics, and Send Halo are not saved, and a fetch can count against the daily limit. AT-32 needs all five prompts.
- 2026-11-08, ticket 10 build: Per Brian, the award and trade cards keep their plain look, so the floor adds no open award or trade card. The Open card entry of `GLOSSARY.md` names GameCard, LadderCard, and the rows of the Index list only.
- 2026-11-08, ticket 10 build: The race group Out also holds each team under 25% odds, so it is wider than the term Out of the pipeline. `GLOSSARY.md` defines In, Bubble, and Out inside one Race group entry, so each term keeps one meaning.
