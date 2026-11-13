Brian, the chosen paths are:

- Module: [packages/week/python/src/week/sheet/base.py](/tmp/readme-navigation-trial-root/packages/week/python/src/week/sheet/base.py:86). `projected_totals` uses `week.rosters` to select current players for future totals.
- Test: [apps/pipeline/tests/test_sheet.py](/tmp/readme-navigation-trial-root/apps/pipeline/tests/test_sheet.py:700). The test adds a player after lineup lock and removes another. It expects the added player’s 30 points only.

The app map links directly to the sheet owner README, which names both files.

Ordered file-read log: **9 distinct files**, including the supplied instructions.

| Order | File | Read type |
|---|---|---|
| 1 | `/tmp/readme-navigation-trial-root/AGENTS.md` | Supplied instructions |
| 2 | `CLAUDE.md` | Full |
| 3 | `apps/pipeline/README.md` | Full |
| 4 | `apps/pipeline/CLAUDE.md` | Full |
| 5 | `/Users/brian.kwon/.codex/memories/MEMORY.md` | Content search |
| 6 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Full |
| 7 | `packages/week/python/src/week/sheet/README.md` | Full |
| 8 | `packages/week/python/src/week/sheet/base.py` | Content search |
| 9 | `apps/pipeline/tests/test_sheet.py` | Content search |

Two external read attempts returned “No such file or directory” before item 2:

- `~/.Codex/output-styles/ste.md`
- `~/.Codex/rules/communication/simplified-technical-english.md`

Neither attempt exposed file content. Repeated searches exposed only files 8 and 9.

The subagent launch failed before any read. I completed the inspection directly.

No `.scratch/` or state file reads occurred. No code changed. No tests ran. This records source evidence without a test verdict.


