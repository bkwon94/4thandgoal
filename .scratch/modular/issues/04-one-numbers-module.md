# 04: One `numbers` module

**What to build:** The three round functions, `ordinal`, and `plural` move into one module in the model layer. The private round function in the history module becomes public there. Each round function keeps its behavior and its name, with a comment that says when to use it. Every importer reads from the new module.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] No module defines its own round, ordinal, or plural function. The two `_plural` helpers with different signatures become one function or two named functions.
- [ ] No module imports a private name from another module for a number function.
- [ ] No rounding result changes. The four golden tests pass with no golden change.
- [ ] The module this ticket makes is in the `pyright` include list, and `make typecheck` passes.
