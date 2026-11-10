# 02: The league Topic Answers and the Suggestions

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-4, AT-5, AT-7, AT-23, AT-51, AT-56.

**App:** both

**What to build:** The weekly build writes the Answers of the 7 league Topics for each team into the published week, from the blurbs and data that exist now, with the fact of each Suggestion. The front door shows 3 Suggestions for Your team, each with its Topic name and one fact, plus "More" with all 13 Topics. The day of the week sets the order. A tap on a league Topic shows its Answer in the Thread with "Read the full report" to its page. An opened Topic drops off the Suggestions until its fact changes or the week turns.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The build of CPC 2026 week 8 writes an Answer of each of the 7 league Topics for each of the 12 teams (AT-51).
- [ ] The `page.json` of week 8 is the same as on `main` (AT-56).
- [ ] 3 Suggestions show, each with a number, and "More" lists 13 Topics (AT-4).
- [ ] On Tuesday of week 9, with no urgent Topic, the week recap is first (AT-5).
- [ ] An opened Topic is gone from the 3 Suggestions after a reload, and stays in "More" (AT-7).
- [ ] "Read the full report" of the power rankings Answer opens `/rankings/` (AT-23). Each Topic links to the page in the table of the spec.
