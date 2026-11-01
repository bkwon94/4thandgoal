# 19: The weekly trade chapter joins the assembly or goes

**What to build:** `sheet/trades.py` holds `trade_facts` and `grade_input_facts` for the weekly page, but the weekly assembly does not call them. Only the trade bundle in the test conftest does. Find out what the trade chapter on the week page reads today, and whether these facts were ever in the assembly. Then either add the module to `CHAPTER_FACTS` with a `facts` function, which changes the golden files on purpose, or delete the module and the test bundle that reads it. Brian decides which, from what the week page shows.

**Blocked by:** 11

**Status:** ready-for-agent

- [ ] The module is in `CHAPTER_FACTS` with a `facts` function, or it is gone with its test bundle.
- [ ] If it joins, the golden change is named in the ticket, and `make golden` rewrites the files in the same commit.
- [ ] The layer test and the full suite pass.
