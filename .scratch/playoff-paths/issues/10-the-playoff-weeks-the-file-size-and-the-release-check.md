# 10: The playoff weeks, the file size, and the release check

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-19, AT-23, AT-51, and AT-55.

**App:** both

**What to build:** In the playoff weeks the page shows the bracket view of the season sim, with no Goal switch and no board. `sim.json` stays at 50 KB gzip or less. The site holds no push notification. After the merge, 10 real What-if calls on Fly at `cpc` week 11 stay at a median of 2.5 s or less; if not, the fallbacks of decision 03 apply.

**Blocked by:** 05, 06, 07, 08, 09

**Status:** done

- [x] The playoff fixture shows the bracket view with no Goal switch and no board.
- [x] `sim.json` of `cpc` week 11, the latest week, is 50 KB gzip or less, and the size of week 10 is recorded.
- [x] A search finds no service worker, `Notification`, or `PushManager`.
- [ ] After the merge, the median of 10 What-if calls on Fly is 2.5 s or less.
- [ ] `make check-fast` passes.

## Comments

- 2026-11-25: Brian chose option D. The bar applies to the latest week only. AT-19 changed to match. Also drop the unread week-switch data from the week file.
- 2026-11-25: blocked. cpc week-10/sim.json is 55,431 B gzip, over the 50 KB bar of AT-19. Week 11 is 47,429 B and passes. No drop of unread fields alone fits week 10 (best 51,536 B). Brian chooses: fewer replay runs in the week file, a short form of the sample scores, or the bar on the latest week only.
- Merged into `playoff-paths` as d88f2c2d, 2026-11-25. Closes with the squash merge of the spec PR.
- Proof: `make check-fast` passed at each merge, and the Judge gave PASS to each test of this ticket in `VERDICTS.md`.
