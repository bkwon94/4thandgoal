# 02: The superstar step

Spec: `.scratch/uneven-trade/PRD.md`. Acceptance tests AT-5, AT-6, AT-7, and AT-15.

**App:** pipeline

**What to build:** A new Superstar adjuster, after Upside in rubric order. A side that gets a superstar, a player in the top 8 trade values of the week, gets one step up. Two superstars to one side give one step. The giver gets no step. A trade with the 1.25 margin gets no superstar step. Each side that gets a superstar gets the step.

**Blocked by:** 01

**Status:** in-review

- [x] A rubric test grades trade W first, test-first, and shows Teehee's row: "Kenneth Walker III is a superstar, a top 8 player this week." Bo Girds' row reads "No player it gets is a superstar."
- [x] The tunables hold the rank as `SUPERSTAR_RANK = 8`. A tie at rank 8 makes every tied player a superstar.
- [x] A rubric test of the AT-3 trade shows no step, with "Kenneth Walker III is a superstar, but the one-for-many margin already counts him."
- [x] Rubric tests cover two superstars to one side, a superstar to each side, and a superstar out for the season.
- [x] The rubric prompt has a Superstar section. The word rule of the analyzer passes on the new reason text.
- [ ] The finder speed test passes under its 5 s bound on the Mac and in CI.
