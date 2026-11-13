Brian, the owner is [apps/pipeline/src/cornerstone/publish.py](/tmp/readme-navigation-trial-root/apps/pipeline/src/cornerstone/publish.py:66).

`run_publish` copies the selected week. It limits staging to the client’s season folders. `_commit_if_staged` also limits each commit through explicit paths.

The relevant test is [apps/pipeline/tests/test_rule_publish.py](/tmp/readme-navigation-trial-root/apps/pipeline/tests/test_rule_publish.py:70).

It uses real temporary Git repositories. It checks commit paths, stray files, another season, and client files outside season folders.

The ordered file-read log contains **eight distinct files**, including the supplied instructions:

| Order | File |
|---|---|
| 1 | `/tmp/readme-navigation-trial-root/AGENTS.md` — instructions supplied in the conversation |
| 2 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` |
| 3 | `CLAUDE.md` |
| 4 | `apps/pipeline/README.md` |
| 5 | `apps/pipeline/CLAUDE.md` |
| 6 | `apps/pipeline/src/cornerstone/README.md` |
| 7 | `apps/pipeline/src/cornerstone/publish.py` |
| 8 | `apps/pipeline/tests/test_rule_publish.py` |

These attempted reads returned “No such file or directory” and exposed no file contents:

- `/tmp/readme-navigation-trial-root/AGENTS.md`
- `/Users/brian.kwon/.Codex/output-styles/ste.md`
- `/Users/brian.kwon/.Codex/rules/communication/simplified-technical-english.md`

I read neither `.scratch/` nor `docs/agents/state.md`. I used no content search.

This evidence comes from source inspection. I ran no tests or publish command and made no commits. I assign no Test verdict.
