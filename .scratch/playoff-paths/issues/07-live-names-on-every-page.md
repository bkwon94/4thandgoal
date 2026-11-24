# 07: Live names on every page

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-44 to AT-48 and AT-54.

**App:** site

**What to build:** Every page with a team name, except the midseason report, shows the Live name of each team. One shared part reads the Sleeper rosters and users of the league in the browser, swaps each renamed team in its name slots and on its full old name in the text of the build, and loads a changed avatar from Sleeper's CDN. The published names show first. The live names stay 5 minutes in `sessionStorage`. A failed call or a wait over 3 seconds keeps the published names (decision 07).

**Blocked by:** none

**Status:** in-review

- [ ] The week page and The Race of `cpc` week 11 show "Teez Nuts" in every slot and blurb, and "Puka Deez..." nowhere.
- [x] A test with a stubbed Sleeper answer shows a new avatar and keeps the local image until it loads.
- [x] With both calls blocked, the pages show the published names and no error.
- [x] A second page within 5 minutes makes no new Sleeper call.
- [x] The midseason report makes no Sleeper call.
- [x] `make check-fast` passes.
