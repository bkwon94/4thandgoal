# 13: Atomic writes, the `ruff` pin, and `pyright` basic

**What to build:** The history module and the render module write through the atomic write helper, so a killed build leaves no half file. `ruff` is pinned in the development dependencies. `pyright` runs in basic mode through a `make typecheck` target. Only the modules a ticket touches must pass, and this ticket makes the config, numbers, paths, and provider modules pass.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] A grep for the plain text write in history and render finds nothing.
- [ ] `uv run ruff --version` prints the pinned version from the lock file.
- [ ] `make typecheck` runs `pyright` in basic mode and passes on the named modules.
- [ ] The four golden tests pass with no golden change.
