# 02: The Advisor gives the read of one trade

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-16, AT-17, AT-18, AT-21, AT-22, AT-23, AT-40, and AT-49.

**App:** both

**What to build:** A manager grades a trade and gets the read of the Advisor, not a rubric letter. Code builds the sheet from the facts the analyzer has now, and Jev answers the atomic questions of one trade: is it fair, does the asker need it, and does the other manager need it and would he accept. The answers join the sheet as facts. The Advisor reads the sheet and gives the Lean, the Case with its condition first, the fairness, and 3 to 5 Bullets per side, each with a Mark and a fact id. The guards check the fact ids, the numbers and names, and the inner words, and a failed check retries once. After two failed calls, the API gives an honest error, and the call does not count toward the grade limit. The analyze document carries `lean`, `case`, the fairness block, and per side the Bullets with `text`, `mark`, `fact_id`, and `fact_text`. It has a new document version. The page shows a plain form of the read: the Lean word, the Case, the fairness line, and the Bullets with their Marks. The Finder keeps its old path until ticket 10.

**Blocked by:** none

**Status:** in-review

- [ ] `/analyze` for Maye d'force B with U giving Jahmyr Gibbs for Bijan Robinson returns a Lean of the five, a Case, a fairness block, and 3 to 5 Bullets per side with their fact text.
- [x] No key of the analyze document holds a letter, a factor, a decision, or an answer.
- [ ] All You Need Is Love giving Ja'Marr Chase for Xavier Worthy reads Pass or Lean no, lopsided with All You Need Is Love as the side that gives more.
- [x] With an Anthropic key that is not valid, `/analyze` returns a plain error after two calls, and the grade count does not change.
- [x] A repeat press returns the same document from the cache.
- [x] The page shows the Lean, the Case, the fairness line, and the error with Try Again.
- [x] The route tests of the API cover the guards, the retry, the honest error, and the document version with a stub Advisor and the fake Jev.
- [x] `make check-fast` passes.
