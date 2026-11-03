# 19: The weekly trade chapter joins the assembly or goes

**What to build:** `sheet/trades.py` holds `trade_facts` and `grade_input_facts` for the weekly page, but the weekly assembly does not call them. Only the trade bundle in the test conftest does. Find out what the trade chapter on the week page reads today, and whether these facts were ever in the assembly. Then either add the module to `CHAPTER_FACTS` with a `facts` function, which changes the golden files on purpose, or delete the module and the test bundle that reads it. Brian decides which, from what the week page shows.

**Blocked by:** 11

**Status:** done

- [x] The module is in `CHAPTER_FACTS` with a `facts` function, or it is gone with its test bundle.
- [ ] If it joins, the golden change is named in the ticket, and `make golden` rewrites the files in the same commit.
- [x] The layer test and the full suite pass.

## Comments

- 2026-11-02: decision "go". Merged into `modular` from branch `modular-19-trade-chapter`, commit 5b0bbf3. 1,479 tests collected. The trade chapter left the weekly build on 2026-10-21, and only a test bundle read `sheet/trades.py`, so the module and 36 tests went. The tied matchup result keeps one test in `test_sheet.py`. The assembly list is `FACT_GROUPS`, not `CHAPTER_FACTS`. The PRD line that moves the trade facts under the sheet no longer applies. The `chart` parameter of `Context` has no reader now; ticket 20 removes it. Two reviewers passed it after one fix pass.
