# Ticket 15 build: the once-per-page rule for "lucky" is a check

Status: DONE_WITH_CONCERNS
Branch: `nflverse-15`. Commit: `dd1474c`.

## What changed

- `src/cornerstone/verifier.py`: the constant `ONCE_PER_PAGE_WORDS = ["lucky", "unlucky"]` sits beside `GATED_WORDS`.
- `code_check` gains a count after the word gate loop. It reads the sentence text with names and URLs removed.
  The match is whole word and case-insensitive, so "unlucky" does not count as "lucky".
- A second sentence gives one failure in the shape of the other failures:
  `[2] sentences [0] and [2] say 'lucky'; a page may say it once`. The index is the second sentence.
- The prompts did not change.
- The ticket file: boxes 2, 3, and 4 are ticked. Box 1 stays open; see the concern. Status stays `open`.

## Tests added (`tests/test_verifier.py`)

- `test_lucky_in_two_sentences_fails_and_names_both`: "Lucky" and "LUCKY" in sentences 0 and 2 give one failure that names both.
- `test_unlucky_in_two_sentences_fails`: two "unlucky" sentences fail.
- `test_lucky_once_and_unlucky_once_pass`: one of each gives no failure.
- The helper `_awards_with_luck` adds `AW.lucky` and `AW.unlucky` to the awards chapter, so the word gate passes.

The first two tests failed before the code change. All three pass after it.

## Checks

- `uv run pytest -q`: `1039 passed, 9 deselected in 184.82s (0:03:04)`. Main has 1036; the 3 new tests make 1039.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` Main has 135. The change adds none.

## Week 6 result

The real `code_check` ran over each saved blurb of `data/2026/week-06` with the saved `facts.json`.
The count check gives 0 failures, so week 6 passes.

But the week 6 page says "lucky" in three sentences, one in each of three chapters:

- `motw` [1]: "Lucky waiver pickup Germie Bernard, a recent add, ..."
- `game_changer` [1]: "... a lucky waiver add for behold the lamb."
- `awards` [3]: "... about as lucky as a pickup gets."

## Concern

The verify step checks one chapter blurb per call. The count therefore holds per blurb, not per page.
The prompt rule is "at most once per page". Week 6 breaks that rule across chapters, and this check does not catch it.
A page-wide check needs state across chapters in `run_build`, and also in `run_rewrite` and `run_rankings`.
One way: pass the count of earlier "lucky" sentences into `write_and_verify`, so a later chapter fails on its first "lucky".
That change is larger than the ticket asked for, so I did not build it. Brian or the orchestrator must decide.

# Fix round 1: the rule holds for the page

Status: DONE. Commit: `e33f039` on `nflverse-15`, after `dd1474c`.

## What changed

- `src/cornerstone/verifier.py`:
  - `once_words(bare)` gives the once-per-page words in one sentence. The count in `code_check` now uses it.
  - `page_words(blurb, chapter)` gives the words that a blurb says, with the chapter names removed. With no chapter, no names are removed.
  - `code_check`, `verify_blurb`, and `write_and_verify` take `used_words: Collection[str] = frozenset()` and pass it down.
  - A sentence that says a word in `used_words` fails: `[1] says 'lucky', but another chapter of this page already did`.
  - The failure reaches the writer through `_feedback`, so the retry rewrites the chapter. The second failure gives the template blurb, as for any other failure.
- `src/cornerstone/pipeline.py`:
  - `run_build` carries a set of used words through the chapter loop. Each accepted blurb adds its `page_words`.
  - `_other_page_words` reads the saved blurbs of the other chapters. `run_rewrite` and `run_rankings` use it.
- The ticket file: box 1 is ticked. A note under Status says that the rule follows the chapter order.

## Design choice: one set, not a bool flag

I used one parameter, `used_words`, that holds the words, not a `lucky_used: bool`.
One bool for both words is wrong: "lucky" in chapter A would then fail "unlucky" in chapter B, but the ticket says that page passes.
Two bools need two parameters through three functions. One set is plainer and holds both words.

The message says "another chapter", not "an earlier chapter". A rewrite reads all other chapters, also the later ones, so "earlier" is not always true.

## Tests added

`tests/test_verifier.py`:
- `test_lucky_after_an_earlier_chapter_said_it_fails`: chapter B fails with the message above.
- `test_unlucky_after_an_earlier_lucky_passes`: "lucky" in A and "unlucky" in B pass.
- `test_page_words_skips_a_team_name_and_unlucky`: "Lucky Lambs" does not count, and "unlucky" is not "lucky".
- `test_write_and_verify_sends_the_page_word_failure_to_the_rewrite`: the second writer call gets the failure as feedback.

`tests/test_pipeline.py`:
- `test_build_carries_lucky_to_the_later_chapters`: after `game_changer` says "lucky", each later chapter gets `{"lucky"}`.
- `test_a_rewrite_sees_lucky_from_the_other_saved_blurbs`: a rewrite of `median` gets `{"lucky"}` from the saved `motw`. A rewrite of `motw` gets nothing from itself.

The three tests from the first round still pass. All new tests failed before the code change.

## Checks

- `uv run pytest -q tests/test_verifier.py tests/test_pipeline.py`: `149 passed in 27.05s`.
- `uv run pytest -q`: `1045 passed, 9 deselected in 155.49s (0:02:35)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` This is the same as main.
- Size: 120 lines added and 10 removed. Of these, about 40 lines are in `src` and the rest are tests.

## Week 6 result

The saved week 6 blurbs went through `code_check` in build order, with the used words carried. The check flags two sentences:

- `game_changer` [1]: "This week the new pickup hit 20.2 on an 8.13 projection, a lucky waiver add for behold the lamb."
- `awards` [3]: "Germie Bernard, a recent waiver add for behold the lamb, scored 20.2 on a projection under half that and takes Game Changer, about as lucky as a pickup gets."

The first "lucky", in `motw` [1], passes.

## Concerns

- The rule follows the chapter order. `motw` is first, so a recent add in `motw` can use up "lucky" before the Lucky award. The awards chapter must then write the award without the word.
- A cross-chapter failure names the second sentence and says "another chapter". It does not give the index of the first sentence in the other chapter.

# Fix round 2: the awards chapter owns the award words

Status: DONE. Commit: `81d6f58` on `nflverse-15`.

## What changed

- `src/cornerstone/verifier.py`:
  - `AWARD_WORDS` maps "lucky" to `AW.lucky` and "unlucky" to `AW.unlucky`. `AWARDS_CHAPTER` is "awards".
  - `reserved_words(chapter_key, sheet)` gives the award words of the sheet for every chapter except awards.
  - `page_word_feedback(used_words)` gives one line per word: "Do not say 'lucky'. Another chapter of this page already does."
    `write_and_verify` starts `feedback` with it, so the first `write_blurb` call hears the used words. With no used words it is None, as before.
  - The comment on the cross-chapter check is now active voice. The `page_words` docstring says why the chapter may be None.
- `src/cornerstone/pipeline.py`: `run_build` and `_other_page_words` add `reserved_words` to the used words. `run_rewrite` and `run_rankings` get the seed through `_other_page_words`.
- `tests/test_pipeline.py`: `Blurb` moved to the top import.

## Tests

`tests/test_verifier.py`, new:
- `test_the_awards_chapter_owns_lucky_when_the_sheet_has_the_lucky_award`: with `AW.lucky`, `motw` fails on "lucky" as the first chapter, and `awards` passes with it.
- `test_no_award_fact_reserves_no_word`.
- `test_the_first_writer_call_hears_the_used_words`: the first writer call gets the line; with no used words it does not.

`tests/test_pipeline.py`: the pipeline fixture week holds both `AW.lucky` and `AW.unlucky`. So the round 1 tests that put "lucky" in `motw` or `game_changer` saw it as reserved anyway. I rewrote them around the awards chapter, the one chapter where the carry shows:
- `test_build_reserves_the_award_words_and_carries_lucky`: awards gets nothing, every other chapter gets both words. A "lucky" in `game_changer` reaches awards.
- `test_a_rewrite_sees_lucky_from_an_earlier_saved_blurb`: a rewrite of awards sees "lucky" in saved `motw`.
- `test_a_rewrite_of_an_earlier_chapter_sees_a_later_lucky`: a rewrite of awards sees "lucky" in saved `median`, which comes later.
- `test_a_rewrite_does_not_count_the_chapter_against_itself`.

## Checks

- `uv run pytest -q tests/test_verifier.py tests/test_pipeline.py`: `154 passed in 26.42s`.
- `uv run pytest -q`: `1050 passed, 9 deselected in 154.83s (0:02:34)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.`

## Week 6

The saved week 6 facts hold no `AW.lucky` and no `AW.unlucky`, so no word is reserved. The result is the same as round 1: `game_changer` [1] and `awards` [3] fail, and `motw` [1] passes.

## Notes

- The first-attempt line arrives under the writer header "Feedback from the last attempt:". This reuses the existing mechanism as asked, but the header is not exact on attempt 1.
- The cross-chapter failure still names one sentence, as ruled.
