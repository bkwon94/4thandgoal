# 10: The `sheet/` package, as a move

**What to build:** The sheet module becomes a package. A base module holds `Nums`, `fact`, `fmt`, `Context`, and the tokens. One module per chapter holds that chapter's functions. An assembly module holds `chapters` and `build_bundle`. The package re-exports every name callers use today, so no caller changes in this ticket. Modules outside the sheet that need the base import it from the base module.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] No module outside the sheet imports from a chapter module. The waiver, the verifier, the writer, the analysis, and the trade facts import the base.
- [ ] No chapter module is longer than 400 lines.
- [ ] Every function keeps its name and body. The diff is moves and imports only.
- [ ] The four golden tests pass with no golden change.
