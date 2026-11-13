Brian, the owner is [apps/api/src/cornerstone_api/caps.py](/tmp/readme-navigation-trial-root/apps/api/src/cornerstone_api/caps.py:103). `answers_today()` filters records by team and calendar date. This gives each team a separate daily allowance.

The relevant test is [apps/api/tests/test_caps.py](/tmp/readme-navigation-trial-root/apps/api/tests/test_caps.py:90). `test_the_team_cap_is_per_team_and_starts_again_the_next_day` covers both requirements. One team has 25 answers yesterday; another has 25 today. Assertions expect the first team’s route to return `free` and the second team’s route to return `cap`.

The ordered file-read log follows. Paths start at the repository root unless absolute.

| Order | File | Result |
|---|---|---|
| 1 | `AGENTS.md` | Instructions supplied in the prompt |
| 2 | `/Users/brian.kwon/.Codex/output-styles/ste.md` | Read attempt; file absent |
| 3 | `/Users/brian.kwon/.Codex/rules/communication/simplified-technical-english.md` | Read attempt; file absent |
| 4 | `CLAUDE.md` | Read |
| 5 | `apps/api/README.md` | Read |
| 6 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Read |
| 7 | `apps/api/src/cornerstone_api/README.md` | Read |
| 8 | `apps/api/src/cornerstone_api/caps.py` | Read |
| 9 | `apps/api/tests/test_caps.py` | Read |

Total: seven distinct files read, plus two absent-file attempts. Even with both attempts counted, the total is nine.

No content searches occurred. I did not read `.scratch/` or `docs/agents/state.md`. Evidence comes from source inspection; I ran no tests and give no test verdict.
