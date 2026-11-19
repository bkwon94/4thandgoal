# 06: A tap sets a What-if on the page

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-33 to AT-36. Decisions 04 and 07, and the map Q16.

**App:** site, api

**What to build:** A tap on a result tile sets that result. The page calls the What-if route at once, and a new tap cancels the call before it. The header odds, the sentence, and the root-for list take the numbers of the answer, and the next week opens. A line at the top lists each set result, with a Reset that goes back to the numbers of the file. When the API is down, the page keeps the numbers of the file, and a tap shows one line that the What-if is not available now.

**Blocked by:** 04, 05.

**Status:** ready-for-agent

- [x] A tap on "Win and beat the median" in week 11 of Bo Girds shows the numbers of the API answer and opens Wk 12 (AT-33).
- [x] Reset clears the set line and shows the numbers of the file again (AT-34).
- [x] Two taps within 200 ms cancel the first call, and the page shows the second answer (AT-35).
- [x] With the API stopped, the page shows the file and one line on a tap (AT-36).
- [x] The site evidence set passes the overlap check after a tap, with the set line shown.
- [x] `make check-fast` passes.
