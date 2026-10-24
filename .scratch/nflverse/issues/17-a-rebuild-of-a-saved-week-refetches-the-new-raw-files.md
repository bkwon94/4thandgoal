# 17 — A rebuild of a saved week refetches the new raw files

Spec: `.scratch/nflverse/PRD.md`, "Further Notes". Found in the ticket 10 review on 2026-10-24.

**What to build:** The saved week 6 extract in `data/2026/week-06/raw/nflverse.json` holds `sources`, `gsis`,
`drops`, and `injuries` only. It lacks the usage, the expected points, and the next games, so a rebuild of week 6
makes none of the new facts and gives no error. The build gains one rule: when a saved raw file lacks a key the
extract needs, the build fetches that source again and rewrites the file. The build logs each refetch.

**Why:** A rebuild should give the page the build of today would give, or say why it cannot.

**Blocked by:** None. Week 7 and later build fresh and do not need this.

**Status:** open

- [ ] A rebuild of a saved week whose extract lacks `usage` fetches the player weeks file and writes the key.
- [ ] A rebuild of a saved week with every key fetches nothing.
- [ ] A refetch that fails leaves the file as it was and the build continues with the facts it can make.
- [ ] Every existing build test passes unchanged.
