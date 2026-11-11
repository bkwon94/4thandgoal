# 01: The live API rewrites the history of a patched week

**App:** api

**What to build:** Each live snapshot of the API fetches the latest week from Sleeper again and rewrites its history files, such as `clients/cpc/data/2026/history/week-09/matchups.json`. Week 9 of cpc holds hand-patched scores of rosters 5 and 10, for a rescinded trade. A refetch writes the unpatched scores back. In a worktree, `git checkout` puts the files back. On Fly, the API rewrites them inside its container and then reads the unpatched scores. So the trade analyzer, the free answer, and the personal Topics can read wrong week 9 scores. Make a patched week safe from the refetch, for example with a patch file that each history write applies, or with no rewrite of a week that the publish already holds.

**Blocked by:** none. Found 2026-11-10 in the live runs of the front-door review fixes. The behavior is older than front-door: the trade analyzer takes the same snapshot.

**Status:** needs-triage

- [ ] A live snapshot leaves the patched scores of cpc week 9 rosters 5 and 10 as they are.
- [ ] A free answer about week 9 on the deployed API gives the patched scores.
