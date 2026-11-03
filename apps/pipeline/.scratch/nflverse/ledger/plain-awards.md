# plain-awards

Status: DONE. Branch `plain-awards`, commit `7185395`, base main `9f25630`. Not pushed, not merged.

## New vocabulary lines, verbatim

The **Lucky**, **Unlucky**, and **WOPR** lines keep their old text. Each one now has a second bullet after it.

```
- **Unlucky**: the starter with the largest gap below his expected points, at least 5 under. Expected points are what his volume should have scored. Say "unlucky" only in a sentence that cites `AW.unlucky`.
- **Unlucky award in prose**: name it "the Unlucky award", never a bare "Unlucky". In the same sentence, say what it measures, with the numbers as the fact gives them. Plain phrase: "took the Unlucky award: 6.1 points from a stat line that usually scores about 14.8".
- **Lucky**: the starter with the largest gap above his expected points, at least 5 over. Say "lucky" for it only in a sentence that cites `AW.lucky`.
- **Lucky award in prose**: name it "the Lucky award", never a bare "Lucky". In the same sentence, say what it measures, with the numbers as the fact gives them. Plain phrase: "took the Lucky award: 22.7 points from a stat line that usually scores about 12.49".
- **WOPR**: weighted opportunity rating, 1.5 times target share plus 0.7 times air yards share; a weighted sum and not a share, so never a percent; it can pass 100 or go negative.
- **WOPR in prose**: never write "WOPR" in prose. Say what it measures. Plain phrase: "the 2nd-biggest share of his team's targets and air yards among started tight ends", or shorter, "2nd in passing volume among started TEs".
- **expected points**: what his volume should have scored. Never write "expected points" in prose. Plain phrase: "what his stat line usually scores".
Never write these words: best, star, carried, hero, MVP, clutch, exploded, cooked, WOPR.
Never write these phrases: the entire point, one of the problems, a lot to hang on, a polite way to say, expected points.
```

## Change from the brief

The Lucky example says "about 12.49", not "about 12.5". `code_check` does not round numbers. A prose "12.5" fails when the fact says "12.49". Each bullet also says "with the numbers as the fact gives them".

## Tests

- Added `test_wopr_fails_as_a_banned_word` in `tests/test_verifier.py`. "He had a big WOPR." gives `[0] banned word 'WOPR'`.
- Added `test_expected_points_fails_as_a_banned_phrase` in `tests/test_verifier.py`. "He beat his Expected Points." gives `[0] banned phrase 'expected points'`. This shows the match ignores case.
- Updated `test_vocabulary_has_the_banned_phrases_line` to the new phrase line.
- Extended `test_vocabulary_has_one_rule_line_for_the_unlucky_and_lucky_awards` with asserts for the two award bullets and the expected points plain phrase.
- `whole_word` already uses `re.IGNORECASE` and a whole-word regex. The verifier code did not change.

## Test line

- `uv run pytest -q tests/test_writer.py tests/test_verifier.py`: 145 passed, 1 deselected.
- `uv run pytest -q`: 1083 passed, 9 deselected. Main has 1081, plus 2 new tests.

## Ruff

`uv run ruff check --line-length 120 src tests`: Found 135 errors. Same as main.

## Not changed

The facts, the fact text, `writer.md`, and `tone.md` did not change. `tone.md` line 54 says "for the Lucky award", which agrees with the new lines. `rubric.md` uses "WOPR", but it is analyzer text, not prose.
