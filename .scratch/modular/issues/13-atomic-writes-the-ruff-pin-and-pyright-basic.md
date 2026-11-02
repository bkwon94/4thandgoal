# 13: Atomic writes, the `ruff` pin, and `pyright` basic

**What to build:** The history module and the render module write through the atomic write helper, so a killed build leaves no half file. `ruff` is pinned in the development dependencies. `pyright` runs in basic mode through a `make typecheck` target. Only the modules a ticket touches must pass, and this ticket makes the config, numbers, paths, and provider modules pass.

**Blocked by:** 01

**Status:** done

- [ ] A grep for the plain text write in history and render finds nothing.
- [ ] `uv run ruff --version` prints the pinned version from the lock file.
- [ ] `make typecheck` runs `pyright` in basic mode and passes on the named modules.
- [ ] The four golden tests pass with no golden change.

## Comments

- 2026-10-31: merged into `modular` from branch `modular-13-cheap-wins`, commits 325df68 and 3f94ff6. 1,459 tests collected. Two deviations, both recorded in ticket 14: `ruff` is pinned at 0.0.272, the version lint ran before, because the current release reports 57 errors; `history.py` is not in the `pyright` include list for three errors that predate the change. Each later ticket adds the modules it makes to the include list. The atomic helper writes files with mode 0600; git stores 644 and the chart writer already works this way, so no change. Two reviewers passed it after one fix pass.
