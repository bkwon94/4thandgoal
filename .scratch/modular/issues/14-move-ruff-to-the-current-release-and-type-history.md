# 14: Move `ruff` to the current release, and type `history.py`

**What to build:** Lint runs on the current `ruff` release, and `history.py` passes `pyright` in basic mode. Ticket 13 pinned `ruff` at 0.0.272, the version lint ran before, because the current release reports 57 errors, most of them import order. Ticket 13 also left `history.py` out of the `pyright` include list for three errors that predate it.

**Blocked by:** 04, 13

**Status:** ready-for-agent

- [ ] `ruff` is pinned at the current release. `uv run ruff check src tests` is clean, with `--fix` for the mechanical rules and a hand fix for the rest.
- [ ] No rule is turned off to get there, unless the ticket names the rule and says why.
- [ ] `history.py` is in the `pyright` include list and `make typecheck` passes.
- [ ] The four golden tests pass with no golden change.
