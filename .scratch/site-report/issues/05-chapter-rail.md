# 05: The chapter rail

**What to build:** A league member on a laptop sees a chapter rail left of the page column that lists the nine chapters in the report's order. The chapter in view is red; the rest are muted ink. A tap on a label scrolls to that chapter, and the rail stays in view under the compact bar as the reader scrolls. The rail is a labeled navigation landmark, each label a plain anchor to the chapter's id, and the in-view label carries the current state. With reduced motion a tap jumps with no smooth scroll. On a tablet and a phone there is no rail. The rail is a client island in the server page and takes the chapter list from the page at build time. This ticket starts the week page test file.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] From the rail tier at 1152px the rail shows left of the page column, outside it, at a token width of about 180px, sticky under the compact bar. The column keeps its width.
- [ ] Under the rail tier at 1152px the rail is hidden and the page is one column.
- [ ] The rail is a navigation landmark with a label. It lists nine plain anchors in the report's order, each to a chapter id the chapter parts set.
- [ ] An observer marks the chapter nearest the top of the viewport as in view: red, with the current state. The mark moves as the reader scrolls.
- [ ] A tap scrolls to the chapter, clear of the compact bar. With reduced motion the jump is instant.
- [ ] The week page stays a server component. The rail is the client island.
- [ ] A new week page test, rendered with the real published data as the home page test is, covers: the nine chapters in order with their ids, the rail landmark and its nine links, the current state through a stubbed observer, and motion off at rest.
- [ ] The tests pass. The typecheck, the build, and the export check pass.
- [ ] Checked with agent-browser on the week 7 report at 1280 by 800 with reduced motion on, at the top and after a scroll to the standings, and at 768 by 1024 to show no rail. Screenshots as `05-rail-<state>-<width>.png` in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 04f80802.
Proof: The commit "Add the chapter rail to the week page on a desktop" merged in b799b889 and 95d57c8d.
Read 1 file: .scratch/todoist-queue/audit.md.
