# 11: A facts command that rebuilds the facts of a saved week

**What to build:** A `cornerstone facts --week N` command. It runs `make_bundle` and `write_bundle` and makes no writer call. A change to the fact text then reaches a saved week before a rewrite.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] `cornerstone facts --week N` rebuilds and saves the facts of week N with no writer call, with a test.
- [ ] `make test` passes. `make lint` stays at 123 or lower.

## Comments

- 2026-10-22: found in the tone 09 review. `rewrite` reads the saved `facts.json`, so a change to the fact text does not reach a saved week until the facts are rebuilt.
