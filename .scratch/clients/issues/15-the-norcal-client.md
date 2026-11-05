# 15: The NorCal client

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-9 to AT-16, AT-24, AT-27, and AT-33.

**App:** both

**What to build:** NorCal Apex 6 builds its own site from the same code, with its own values, brand, and menu, and serves at `norcal.4thandgoal.app`.

**Blocked by:** 14

**Needs Brian:** manual step 3 of the spec for `norcal.4thandgoal.app`. `cpc:implement` stops here and gives Brian the dashboard page, each value, and the check.

**Status:** in-review

- [x] The NorCal client folder holds the `client.toml`, `brand.toml`, and `copy.toml` of the spec, and its data.
- [x] The pipeline builds 2026 week 8 for `norcal`, with no Median Game chapter, one game a week, no DEF, and full PPR (AT-11 to AT-14).
- [x] The site shows "NorCal Apex 6", the dark brand, no theme button, the finder, and the menu bar (AT-9, AT-10, AT-15, AT-16).
- [x] The full check builds `cpc` and `norcal` (AT-24).
- [ ] `api.4thandgoal.app/clients/norcal/teams` lists each NorCal team (AT-27).
- [x] The client folders hold no code file (AT-33).

## Comments
- 2026-11-04: The proof from the real `norcal` build of 2026 week 8 (`cornerstone build --client norcal --season 2026 --week 8`):
  - AT-11: `page.json` has `median: null`, and the week page has no Median Game chapter.
  - AT-12: the wins and the losses of each of the 12 teams add up to 8, in `page.json` and in the last week of `rankings.json`. Each managers week has `median: null`.
  - AT-13: no `"DEF"` and no `"K"` in `page.json`, `rankings.json`, `managers.json`, or `waiver.json`. The leaders are QB, RB, WR, and TE.
  - AT-14: Tee Higgins, WR, player `6801`, has the projection 15.97 in `page.json`. His raw Sleeper `pts_ppr` for week 8 is 15.97. His `pts_half_ppr` is 13.67.
- 2026-11-04: The proof from `CLIENT=norcal pnpm build` and `check:export`. The export check now checks the masthead text, the theme button, and the finder of each client.
  - AT-9: each title ends in "NorCal Apex 6", and the masthead shows "NorCal Apex 6" as text with no image.
  - AT-10: the root has the class `dark`, and no page holds a theme button.
  - AT-15: the analyzer page sets `finderOn` to `true`.
  - AT-16: the masthead holds a row of links in this order: Home, Week 8, Power Rankings, Managers, Trade Analyzer. It has no menu button.
  - The screenshots of AT-9 to AT-16 and the API call of AT-27 need the live deploy. The evidence stage records them.

