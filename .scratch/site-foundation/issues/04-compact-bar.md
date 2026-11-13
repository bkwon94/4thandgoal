# 04: The compact bar

**What to build:** A league member scrolls past the masthead on a long page and a 44px black bar slides in at the top of the viewport. On a phone and a tablet the bar shows the brand mark as a home link and the menu button, which opens the same sheet. On a desktop the bar shows the brand mark and the same row, with the same Past weeks popover. The bar leaves once the masthead returns. An observer on the masthead drives it. The bar is fixed, so it takes no space in the page flow. The bar lives in the masthead's client island, so the menu stays one component with two places to show.

**Blocked by:** 02 The destinations and the menu sheet, 03 The desktop row and the Past weeks popover

**Status:** done

- [ ] Once the masthead leaves the viewport the bar slides in with the house ease-out at the press timing. Once the masthead returns the bar leaves along the same path.
- [ ] The bar is 44px tall, takes the masthead's black, spans the viewport, and aligns its content to the page column.
- [ ] Under 1024px the bar shows the brand mark as a home link and the menu button. The button opens the same sheet with the same items.
- [ ] From 1024px the bar shows the brand mark and the same row with the same popover.
- [ ] The bar is fixed and takes no space in the page flow. The page under it does not jump when the bar shows.
- [ ] With motion off the bar shows and hides with a cross-fade.
- [ ] Tests at the masthead seam stub the observer: a report of the masthead out of view shows the bar, a report back in view hides it, and the bar's button opens the sheet. The existing tests pass.
- [ ] Checked with agent-browser at 390 by 844 and 1280 by 800, scrolled past the masthead on the week 7 report, with reduced motion on. Screenshots in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 911899bf.
Proof: The commit "Add the compact bar to the menu" merged in a5559600; the redesign 0a8b8868 changed the menu later.
Read 1 file: .scratch/todoist-queue/audit.md.
