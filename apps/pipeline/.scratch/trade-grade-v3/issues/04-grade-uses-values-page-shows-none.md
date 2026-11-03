# 04: The grade uses the values and the page shows none

**What to build:** The writer weighs each side by trade value and a position order, and the grade reflects it. No value, sum, chart name, or tier reaches a sentence; the code check blocks it. The opinion note under the Trades label is gone from the page.

**Blocked by:** 01 (Value facts on the sheet)

**Status:** done

- [ ] Rule 18 gains a sentence on the position order: at equal rank and points, an RB outweighs a WR, a WR outweighs a TE, and a TE outweighs a QB; a DEF carries little trade value. No mention of kickers.
- [ ] Rule 18 gains a sentence that the value facts weigh the two sides and never appear in a sentence: no value, no sum, no chart, no tier.
- [ ] The code check fails a trade chapter sentence that holds a number equal to any number of a `.value` fact in that chapter, unless the same number is also in a cited fact that is not a `.value` fact. This holds whether or not the sentence cites the value fact.
- [ ] The note "Grades are Tina's opinion from the fact sheet, not a computed score." is removed from the week page. No text replaces it. The cards do not change.
- [ ] A writer prompt test checks rule 18 holds the position order sentence.
- [ ] Verifier tests: a blurb with a value number in a trade sentence fails; the same number from a points fact passes.
- [ ] A render test checks the week page holds no opinion note.
- [ ] `uv run pytest -q` passes.
