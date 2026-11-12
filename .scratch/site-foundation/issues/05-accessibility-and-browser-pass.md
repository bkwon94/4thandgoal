# 05: The accessibility pass and the browser pass

**What to build:** The foundation is ready to merge. A review against the web interface guidelines finds no open issue in the masthead, the sheet, the row, the popover, or the compact bar. A browser pass at the three tiers with reduced motion on shows each page as the PRD describes it, with no sideways scroll. The build and the export check pass. The branch rebases onto main, which may have gained a week publish, and merges. GitHub Pages deploys on its own.

**Blocked by:** 01 Tiers and the page column, 02 The destinations and the menu sheet, 03 The desktop row and the Past weeks popover, 04 The compact bar

**Status:** done

- [x] The web interface guidelines review of the masthead, the sheet, the row, the popover, and the compact bar lists no open issue. Fixes land in this ticket.
- [x] Keyboard only: Tab reaches the menu button, Enter opens the sheet, Tab stays inside, Escape closes, focus returns. The same for the Past weeks trigger and its popover.
- [x] A screen reader hears the button's name and state, the navigation landmark's label, the Past weeks heading, and the current-page item.
- [x] Every tappable control is at least 44px tall on a phone.
- [x] The browser pass with agent-browser at 390 by 844, 768 by 1024, and 1280 by 800, with reduced motion on, covers the home page, the week 7 report, the rankings page, and the analyzer page. No sideways scroll on any page at any width.
- [x] A second browser pass with motion on, at 390 and 1280, records the sheet open and close and the compact bar as a GIF in the feature folder.
- [x] The tests pass, the typecheck passes, the build passes, and the export check passes.
- [x] The branch rebases onto main with no edit under the public folder, and merges. The deploy shows the menu on the live site.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 4e9c6b87.
Proof: The commit "Add the browser pass of the accessibility ticket" and the tick a98dd105 merged in a5559600.
Read 1 file: .scratch/todoist-queue/audit.md.
