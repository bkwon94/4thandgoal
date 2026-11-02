# 11: Every chapter is `facts(bundle, config)`

**What to build:** Each chapter module exports one function, `facts(bundle, config)`, that returns the list of facts for that chapter. The assembly calls each in order and joins the lists. A chapter function reads no file, no environment variable, and no global. The league facts module and the trade facts module move under the sheet as chapters of the same shape.

**Blocked by:** 03, 10

**Status:** done

- [ ] Every chapter module has one public `facts` function with the same signature.
- [ ] The assembly is a list of chapter functions in order, and nothing else decides the order.
- [ ] A test calls one chapter with the fixture bundle and a config and gets its facts.
- [ ] The four golden tests pass with no golden change.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-11-chapter-shape`, commits 028aa28 to d451f98, the merge 89a56c3, and the fix ae38dd4. 1,510 tests collected. Term fix: the sheet modules are fact groups that feed chapters, so the list is `FACT_GROUPS` and the shape is `facts(context, config)`; the glossary gains Fact group. Deviations from the ticket text, accepted: `facts_league.py` builds league models, not facts, and stays out; `trade_facts.py` is the analyzer's sheet and stays out; `sheet/trades.py` is off the assembly and goes to ticket 19. Two reviewers passed it after one fix pass.
