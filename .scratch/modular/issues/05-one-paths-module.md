# 05: One `paths` module

**What to build:** One module in the model layer builds every directory and label from the config and the repo root: the week label, the week directory, the raw directory, the history directory, the site week directory, the season directory, and the chart paths. The nine inline week labels and the two twin directory functions call it. The nflverse cache directory leaves the orchestrator.

**Blocked by:** 02

**Status:** done

- [ ] A grep for the week label format string finds the paths module and nothing else.
- [ ] The orchestrator and the history module share one week directory function.
- [ ] The directory layout on disk is unchanged. The four golden tests pass with no golden change.
- [ ] The module this ticket makes is in the `pyright` include list, and `make typecheck` passes.

## Comments

- 2026-10-31: merged into `modular` from branch `modular-05-paths`, commits 69bd87d and e0f39dc. 1,488 tests collected. The functions take the repo root and no config, because no layout names the league in this feature; the module docstring says so. `history_week_dir(root, week)` serves the readers that hold only a history root. The chart helpers take the repo. Two reviewers passed it after one fix pass.
