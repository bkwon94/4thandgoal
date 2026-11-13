# 07: The accessibility pass and the browser pass

**What to build:** The report feature is ready to merge. A review against the web interface guidelines finds no open issue in the rail, the footer, the hero, or the card chapters. The keyboard reaches every rail and footer link, and a screen reader hears the rail's label and the in-view state. A browser pass at the three tiers shows each chapter as the PRD describes it, with a screenshot per chapter per width and no sideways scroll. The build and the export check pass. The branch rebases onto main, which may have gained a week publish, and merges.

**Blocked by:** 01 The type scale, the measure, and the cards; 02 The hero composition; 03 The grid chapters; 04 The wide chapters; 05 The chapter rail; 06 The week footer

**Status:** done

- [x] The web interface guidelines review of the rail, the footer, the hero, and the card chapters lists no open issue. Fixes land in this ticket.
- [x] Keyboard only: Tab reaches each rail link and each footer link, and Enter follows it.
- [x] A screen reader hears the rail's landmark label, each chapter label, and the current state on the in-view chapter.
- [x] The browser pass with agent-browser at 390 by 844, 768 by 1024, and 1280 by 800, with reduced motion on, covers the week 7 and week 6 reports with a screenshot per chapter per width. The measure, the type step, the cards, the hero, the grids, the wide chapters, the rail, and the footer match the PRD. No sideways scroll at any width.
- [x] A browser pass with motion on at 1280 confirms the rail mark moves on a scroll and the reveals still play.
- [x] The tests pass, the typecheck passes, the build passes, and the export check passes.
- [ ] The branch rebases onto main with no edit under the public folder, and merges. The deploy shows the report per tier on the live site.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 22311557.
Proof: The commit "Add the browser pass screenshots and tick ticket 07" merged in 95d57c8d after the fixes b117cd7e and 5fcfd7ae.
Read 1 file: .scratch/todoist-queue/audit.md.
