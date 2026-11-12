# 05: Rebuild week 6

**What to build:** Week 6 is rebuilt with v3 grades from the week 6 chart, dated 2026-10-13. Every trade chapter has a grade. The page holds at 390 pixels. Brian reviews the page and publishes it.

**Blocked by:** 03 (Pipeline wiring), 04 (The grade uses the values and the page shows none)

**Status:** wontfix

- [ ] `cornerstone chart --season 2026 --week 6` fetches the chart dated 2026-10-13, passes every guard, and matches every traded player of week 6 or lists which ones did not match.
- [ ] The live read test passes on the real week 6 image.
- [ ] A smoke render from disk with no Claude call shows no opinion note and unchanged cards.
- [ ] `cornerstone build --week 6 --season 2026` runs. The verify file has `chart` true. Every trade chapter has a grade; a fallback is fixed with `rewrite`.
- [ ] No trade blurb holds a trade value, a sum, the chart name, or a tier.
- [ ] The page scroll width at a 390 pixel viewport is 390.
- [ ] Brian reviews the page and publishes it with `cornerstone publish`. Nothing else pushes the site.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12.
Proof: Commit 011f46d0 made the trade chapter a recap with no grade and stopped the chart fetch in the weekly build. No published page of weeks 6 to 9 holds a grade.
Read 1 file: .scratch/todoist-queue/audit.md.
