# 09: The Announcement and the Sim tile

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-49 and AT-50.

**App:** site

**What to build:** The general Announcement introduces The Race once in each browser, for 1 week after the release: "New: The Race", "The Race is on", "See what you need each week, and who to root for.", "Open The Race", and "Not now", with the board rows around Your team as art. The Sim tile of each week page reads "The Race" and links to the page.

**Blocked by:** 02

**Status:** ready-for-agent

- [x] A fresh browser with Your team set sees the Announcement on the first load and not after a dismiss.
- [x] The Sim tile reads "The Race" and links to `/sim/2026/`.
- [x] The Announcement passes the WebKit overlap check at the 4 sizes, in light and dark mode.
- [x] `make check-fast` passes.
