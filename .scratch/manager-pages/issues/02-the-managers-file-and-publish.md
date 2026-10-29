# 02: The managers file and publish

**What to build:** the build writes one managers file per season after the rankings file, with the schema version, the season, the week it was built through, and one entry per roster with the roster id, the team, and the record. Publish copies it next to the rankings file. The rankings command rebuilds it too. Pipeline repo.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The build on the week 6 fixture writes the managers file with twelve entries and the schema version.
- [ ] Under two saved weeks the build writes no file and logs one line. Nothing raises.
- [ ] Publish copies the managers file to the site's public folder. A missing file warns and does not fail.
- [ ] The managers module holds one pure function from the history and the snapshot to the entries. The render module writes the file.
- [ ] The file shape is the base every later ticket extends. A later ticket adds fields and never changes what exists.
- [ ] Every existing test passes. `ruff` is clean.
