# 06: Check a real build of week 6 from saved raw data

**What to build:** One real build of week 6 from the saved raw data proves the new writer call, the four tiles, the boards, and the brand link work together before the Tuesday job. Nothing publishes. The week 6 data files on disk go back to their committed state after the check.

**Blocked by:** 01, 02, 03, 04, 05

**Status:** ready-for-agent

- [ ] Run `uv run pytest -q` first. Stop if it fails.
- [ ] Build week 6 from the saved raw data with the build command. Do not run `cornerstone publish`.
- [ ] The build log shows a `position_leaders` blurb that passed the verifier, with a `rewrite` for that chapter if it fell back.
- [ ] The rendered week 6 page shows four award tiles, no drop note, five boards with 15 rows, a blurb under the boards, and a brand link to the index.
- [ ] The page says "lucky" at most once.
- [ ] Check the page at a 390 by 844 viewport with `agent-browser` and save a screenshot for Brian.
- [ ] Restore the week 6 data files and the site directory with `git checkout` and `git clean` on those paths, so the tree matches the last commit.
