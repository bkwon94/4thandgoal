# 04: One `numbers` module

**What to build:** The three round functions, `ordinal`, and `plural` move into one module in the model layer. The private round function in the history module becomes public there. Each round function keeps its behavior and its name, with a comment that says when to use it. Every importer reads from the new module.

**Blocked by:** 01

**Status:** done

- [ ] No module defines its own round, ordinal, or plural function. The two `_plural` helpers with different signatures become one function or two named functions.
- [ ] No module imports a private name from another module for a number function.
- [ ] No rounding result changes. The four golden tests pass with no golden change.
- [ ] The module this ticket makes is in the `pyright` include list, and `make typecheck` passes.

## Comments

- 2026-10-31: merged into `modular` from branch `modular-04-numbers`, commits 5dea4e7 and 18eaa1a. 1,466 tests collected. Names: `r2`, `round_half_up`, `one_decimal`, `one_decimal_text`, `ordinal`, `plural`, `count_noun`. Two thin wrappers in `sheet.py`, `_note_decimal` and `_note_count`, record the value in `Nums`; a later ticket may fold them into `Nums` methods. Two reviewers passed it.
