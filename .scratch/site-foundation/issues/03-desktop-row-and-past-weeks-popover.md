# 03: The desktop row and the Past weeks popover

**What to build:** A league member on a laptop sees the destinations as a row at the right of the brand line: Home, Week N, Power rankings, Trade analyzer, and a Past weeks trigger. The week line sits under the brand. The menu button is hidden from the desktop tier up, and the row is hidden under it. The Past weeks trigger opens a popover that scales in from the trigger and lists the past weeks newest first. Escape and a click outside close it. A row link takes the red accent on hover, on a fine pointer only. The row renders the same list as the sheet, so an item lives in one place. The foundation adds the popover component from the site's component source.

**Blocked by:** 01 Tiers and the page column, 02 The destinations and the menu sheet

**Status:** done

- [ ] From 1024px the masthead shows the row and hides the menu button. Under 1024px it shows the button and hides the row.
- [ ] The row lists Home, Week N, Power rankings, Trade analyzer, and a Past weeks trigger, in that order, from the same list the sheet renders.
- [ ] On a desktop the brand sits left and the row sits right on one line, aligned to the page column. The week line sits under the brand.
- [ ] The Past weeks trigger opens a popover on the site's component source. It lists the past weeks newest first, scales in from the trigger at about 160ms with the house ease-out, and closes on Escape and on a click outside.
- [ ] The row link for the open page carries the current-page state and the red accent.
- [ ] A row link takes the red accent on hover only on a device with a fine pointer that can hover.
- [ ] With motion off the popover shows at rest.
- [ ] Tests at the masthead seam cover the row links in order, the trigger, the popover items, and the current-page state. The existing tests pass.
- [ ] Checked with agent-browser at 1280 by 800 and 768 by 1024 with reduced motion on. Screenshots of the row and the open popover in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in ed7c1d80.
Proof: The commit "Add the desktop row and the Past weeks popover to the menu" merged in a5559600; the redesign 0a8b8868 changed the menu later.
Read 1 file: .scratch/todoist-queue/audit.md.
