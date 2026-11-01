# 05: One `paths` module

**What to build:** One module in the model layer builds every directory and label from the config and the repo root: the week label, the week directory, the raw directory, the history directory, the site week directory, the season directory, and the chart paths. The nine inline week labels and the two twin directory functions call it. The nflverse cache directory leaves the orchestrator.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] A grep for the week label format string finds the paths module and nothing else.
- [ ] The orchestrator and the history module share one week directory function.
- [ ] The directory layout on disk is unchanged. The four golden tests pass with no golden change.
