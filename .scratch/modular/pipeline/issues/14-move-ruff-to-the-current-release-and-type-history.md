# 14: Move `ruff` to the current release, and type `history.py`

**What to build:** Lint runs on the current `ruff` release, and `history.py` passes `pyright` in basic mode. Ticket 13 pinned `ruff` at 0.0.272, the version lint ran before, because the current release reports 57 errors, most of them import order. Ticket 13 also left `history.py` out of the `pyright` include list for three errors that predate it.

**Blocked by:** 04, 13

**Status:** done

- [ ] `ruff` is pinned at the current release. `uv run ruff check src tests` is clean, with `--fix` for the mechanical rules and a hand fix for the rest.
- [ ] No rule is turned off to get there, unless the ticket names the rule and says why.
- [ ] `history.py` is in the `pyright` include list and `make typecheck` passes.
- [ ] The four golden tests pass with no golden change.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-14-ruff`, commits 81fc784, a0788e4, and 604d2e0. 1,514 tests collected. 91 findings on 0.17.3: import order and small rewrites by `--fix`, three by hand with no behavior change. The `quantize` error was a type inference on a `Decimal` sum with an int start; no float reaches it. Two reviewers passed it after one fix pass.
