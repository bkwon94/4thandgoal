# 02: The destinations and the menu sheet

**What to build:** A league member on any page taps a menu button at the right end of the brand line and a sheet drops from under the masthead over a dimmed page. The sheet lists Home, the current week's report with its number, Power rankings, Trade analyzer, then Past weeks newest first under a heading. The item for the open page carries the red accent and the current-page state. A tap on an item opens that page. Escape, a tap outside, or the button closes the sheet, and focus returns to the button. The waiver item shows only with the waiver flag on, and the masthead's "Waiver wire" link is gone. The masthead reads the published weeks at build time and passes the list to the menu, a client island, so the masthead stays a server component. Each page passes its own href to the masthead. In this ticket the button shows at every tier. Ticket 03 hides it on a desktop.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The masthead takes the weeks and the open page's href as props. A test passes its own values.
- [ ] One destination list: Home, Week N, Power rankings, Trade analyzer, then the past weeks newest first. Every link is a plain anchor with the base path.
- [ ] The menu button is 44px tall at the right end of the brand line, has a name, carries the expanded state, and names the list it controls.
- [ ] The sheet builds on the site's dialog primitive: focus stays inside, Escape closes, a tap outside closes, focus returns to the button.
- [ ] The list is a navigation landmark with a label. The past weeks sit under a Past weeks heading.
- [ ] The item whose href matches the open page carries the current-page state and the red accent.
- [ ] The waiver item shows with the flag on and not with the flag off. The masthead's "Waiver wire" link is gone.
- [ ] The sheet drops and fades in at the collapse timing with the house ease-out, exits faster along the same path, and the items stagger at the site's step. The icon morphs from three lines to a cross. Only transform and opacity animate.
- [ ] The button and every item take the press token on pointer down.
- [ ] With motion off, the sheet cross-fades and the icon switches with no morph.
- [ ] The timings join the shared motion module as named entries.
- [ ] Every page renders with scripts off and every menu link still navigates.
- [ ] Tests at the masthead seam cover the items in order, the current-page state, Escape, the tap outside, focus return, the waiver flag, and motion off. The existing tests pass.
- [ ] Checked with agent-browser at 390 by 844 with reduced motion on. Screenshots of the closed and the open menu in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in f1c3f09e.
Proof: The commit "Add the menu button and the menu sheet to the masthead" merged in 6a480aec and a5559600.
Read 1 file: .scratch/todoist-queue/audit.md.
