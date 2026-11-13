# 06: The week footer

**What to build:** A league member at the end of the weekly report sees a footer row: the prior week on the left and the next week on the right, each as the week number with its dates, in the home row style with the press feedback. A missing side leaves its slot empty, so week 7 shows week 6 on the left and nothing on the right until week 8 publishes. The page reads the published week summaries at build time, so no code change is needed per week. Every link is a plain anchor with the base path.

**Blocked by:** 05 The chapter rail

**Status:** done

- [ ] After the next week chapter, a footer row shows the prior week on the left and the next week on the right, each with the week number as the lead and the dates under it.
- [ ] A missing prior or next week leaves its slot empty and the other link keeps its side.
- [ ] Each link is a plain anchor with the base path, in the home row style with the press feedback, at least 44px tall.
- [ ] The footer reveals as the chapters do, and with motion off it shows at rest.
- [ ] The week page test covers: week 7 links week 6 on the left with an empty right slot; week 6 links week 5 on the left and week 7 on the right; each link shows the number and the dates; every link has the base path.
- [ ] The tests pass. The typecheck, the build, and the export check pass.
- [ ] Checked with agent-browser on the week 7 and week 6 reports at 390 by 844 and 1280 by 800 with reduced motion on. Screenshots as `06-footer-week<N>-<width>.png` in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 52763926.
Proof: The commit "Add the week footer with links to the prior and the next week" merged in 49c735f9 and 95d57c8d.
Read 1 file: .scratch/todoist-queue/audit.md.
