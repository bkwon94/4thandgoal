# 07: The full path and the floor

Spec: `.scratch/egg-polish/PRD.md`. Acceptance tests AT-31 to AT-37.

**App:** site

**What to build:** The e2e test of the eggs runs the whole path of a manager on the served CPC build with the local API: it finds T1, cracks the egg, tears the stub, and sees the claim on the egg board. The floor check covers the find card, the claim sheet, and the egg board. The out-of-scope tests prove that the egg button, the egg banner, the latest claims, how the hunt works, the API, and the dependencies did not change.

**Blocked by:** 01, 03, 06

**Status:** done

- [x] The e2e test of the eggs passes at 375 and 1280 px with the crack and the tear.
- [x] The floor check finds 0 violations and 0 incomplete items on the three parts, and prints the two counts apart.
- [x] A page script finds no page and no target of a test egg in the HTML of the egg board.
- [x] The diff against `main` holds no change to the API, no new dependency, and no Scrolltide source.

## Comments
- Closed by the merge of PR #23.
