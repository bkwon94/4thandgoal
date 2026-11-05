# 11: The report page and Act I

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-8, AT-11, AT-26, AT-27, and AT-28.

**App:** site

**What to build:** A manager opens `/midseason/2026` and reads the opener, then three acts with dark title pages, with the chapter rail at the top. Act I renders in full: the state of the league, arcs, Schedule luck with the swap, the injury toll, and Position top 10 with its position switch. This ticket waits for the merge of `site-redesign` into `main`, because it uses the redesign's parts and look.

**Blocked by:** 04, 05, 06.

**Status:** ready-for-agent

- [ ] The Zod schema parses the real `midseason.json` of CPC.
- [ ] The three acts render in order, each with a dark title page.
- [ ] A tap in the chapter rail moves to Act III, and the rail stays at the top.
- [ ] Position top 10 opens on RB and shows one position.
- [ ] One plain sentence explains the All-play record.
- [ ] The floor tests pass at 375, 768, and 1280 px, in the light and the dark theme.
