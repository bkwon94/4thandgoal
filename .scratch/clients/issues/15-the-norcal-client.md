# 15: The NorCal client

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-9 to AT-16, AT-24, AT-27, and AT-33.

**App:** both

**What to build:** NorCal Apex 6 builds its own site from the same code, with its own values, brand, and menu, and serves at `norcal.4thandgoal.app`.

**Blocked by:** 14

**Needs Brian:** manual step 3 of the spec for `norcal.4thandgoal.app`. `cpc:implement` stops here and gives Brian the dashboard page, each value, and the check.

**Status:** ready-for-agent

- [ ] The NorCal client folder holds the `client.toml`, `brand.toml`, and `copy.toml` of the spec, and its data.
- [ ] The pipeline builds 2026 week 8 for `norcal`, with no Median Game chapter, one game a week, no DEF, and full PPR (AT-11 to AT-14).
- [ ] The site shows "NorCal Apex 6", the dark brand, no theme button, the finder, and the menu bar (AT-9, AT-10, AT-15, AT-16).
- [ ] The full check builds `cpc` and `norcal` (AT-24).
- [ ] `api.4thandgoal.app/clients/norcal/teams` lists each NorCal team (AT-27).
- [ ] The client folders hold no code file (AT-33).
