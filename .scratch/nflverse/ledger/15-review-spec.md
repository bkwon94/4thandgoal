# Ticket 15 spec review: the once-per-page rule for "lucky" is a check

Branch `nflverse-15`, base `e29e2b4`, head `e33f039`. Verdict: one Critical, two Important, two Minor.

## Critical

1. `src/cornerstone/verifier.py:124` and `src/cornerstone/pipeline.py:289-293`: the awards chapter fails when it names its own Lucky award.
   - `AWARD_TITLES["lucky"]` is "Lucky" (`src/cornerstone/sheet.py:83`). The `AW.lucky` fact text starts with "Lucky:" (`sheet.py:603`).
   - `page_words` and `code_check` remove only `scope_teams` and `scope_players`. Award titles stay in the text.
   - `run_build` writes `motw` and `game_changer` before `awards`. A recent add called "lucky" in `motw` puts "lucky" in `used`.
   - Then "Jane Doe takes the Lucky award" in the awards chapter fails. I checked it: `page_words` on that sentence gives `{'lucky'}`.
   - Lucky is not a tile (`render.py:27`, `TILE_KEYS`). On two failures the awards chapter falls to the template, and the Lucky award is gone from the page.
   - Fix: when the sheet holds `AW.lucky`, give every chapter except `awards` a used set that already holds "lucky". Do the same in `_other_page_words`.

## Important

1. `src/cornerstone/verifier.py:457` and `src/cornerstone/writer.py`: the writer never sees `used_words` on the first attempt.
   - Each week where an earlier chapter used "lucky", the later chapter burns attempt 1 on a predictable failure. Only the retry gets the hint through `_feedback`.
   - Fix: pass `used_words` to `write_blurb` and add one line to the user prompt: "Another chapter already said: lucky."
2. `tests/test_pipeline.py:882`: no test shows that a rewrite of an earlier chapter sees a later chapter.
   - The code is right: `_other_page_words` reads every saved blurb with `k != key` (`pipeline.py:344-347`). The test checks only `median` after `motw`.
   - Fix: add a "lucky" to a saved later blurb, rewrite `motw`, and assert `seen["motw"] == {"lucky"}`.

## Minor

1. `src/cornerstone/verifier.py:357`: the cross-chapter failure names one sentence. Box 1 says "the failure names both sentences".
   - The in-chapter failure names both. The page-wide failure says "another chapter" with no chapter key.
   - Fix: carry `dict[str, str]` of word to chapter key, and put the key in the message.
2. `src/cornerstone/writer.py:195`: the template blurb skips the check.
   - It cannot say "lucky" today. It quotes `fact_ids[0]`, and `AW.game_changer` comes before `AW.lucky` in the awards chapter. A team name with "Lucky" is a name, so it does not count.
   - Fix: none now. Add a comment at `template_blurb` if the fact order of the awards chapter changes.

## Checks that hold

- Boxes 2, 3, 4: met by `test_lucky_once_and_unlucky_once_pass`, `test_unlucky_after_an_earlier_lucky_passes`, `test_page_words_skips_a_team_name_and_unlucky`. The diff removes no test line.
- Box 1: met in-chapter by `test_lucky_in_two_sentences_fails_and_names_both`; page-wide by `test_lucky_after_an_earlier_chapter_said_it_fails`, with Minor 1.
- Retry path: `code_check` adds the failure, `verify_blurb` returns `passed=False`, `_feedback` joins `code_failures`, and the loop calls `write_blurb` once more with it. A second failure returns `template_blurb`. `test_write_and_verify_sends_the_page_word_failure_to_the_rewrite` covers it.
- `run_rewrite` and `run_rankings` read all other saved blurbs, earlier and later.
- `uv run pytest -q tests/test_verifier.py tests/test_pipeline.py`: `149 passed in 25.07s`.

## Real-data result, week 6

The saved week 6 blurbs went through `code_check` in build order, with `used` carried. Week 6 has no `AW.lucky` fact, so the Critical does not show here. Two sentences fail, as the builder reports:

- `game_changer` [1]: "This week the new pickup hit 20.2 on an 8.13 projection, a lucky waiver add for behold the lamb."
- `awards` [3]: "Germie Bernard, a recent waiver add for behold the lamb, scored 20.2 on a projection under half that and takes Game Changer, about as lucky as a pickup gets."

`motw` [1] passes: "Lucky waiver pickup Germie Bernard, a recent add, posted 20.2 and decided it, and without him, that is a loss."

In rewrite mode, `motw`, `game_changer`, and `awards` each fail on their own "lucky", because each sees the other two. Every other chapter passes.

# Re-review of fix round 2, commit `81d6f58`

Diff `e33f039..HEAD`. Verdict: all three findings ADDRESSED. The fix adds one new Minor issue.
`uv run pytest -q tests/test_verifier.py tests/test_pipeline.py tests/test_writer.py`: `199 passed, 1 deselected in 28.50s`.

## Findings

1. Critical, awards chapter denied its own award name: ADDRESSED.
   - `reserved_words` (`verifier.py:135`) gives the award words to every chapter except `awards`, but only when the sheet holds `AW.lucky` or `AW.unlucky`.
   - `run_build` (`pipeline.py:292`) passes `used | reserved`. `_other_page_words` (`pipeline.py:349`) adds it, so `run_rewrite` and `run_rankings` get it too.
   - Tests: `test_the_awards_chapter_owns_lucky_when_the_sheet_has_the_lucky_award` (`tests/test_verifier.py:965`) and `test_build_reserves_the_award_words_and_carries_lucky` (`tests/test_pipeline.py:877`).
2. Important, the writer did not hear `used_words` on attempt 1: ADDRESSED.
   - `write_and_verify` starts `feedback` with `page_word_feedback(used_words)` (`verifier.py:479`). Test: `test_the_first_writer_call_hears_the_used_words` (`tests/test_verifier.py:985`).
3. Important, no test for a rewrite of an earlier chapter that sees a later one: ADDRESSED.
   - `test_a_rewrite_of_an_earlier_chapter_sees_a_later_lucky` (`tests/test_pipeline.py:904`): a rewrite of `awards` sees "lucky" in the saved `median`.

## The header note: Minor

On attempt 1 the line sits under "Feedback from the last attempt:" (`writer.py:175`). The line itself is a plain command: "Do not say 'lucky'. Another chapter of this page already does."
The writer can follow it with no knowledge of an earlier attempt. The wrong header does not change what the writer must do, so the risk is low.

## New issue from the fix

Minor 3. `src/cornerstone/writer.py:190`: `write_blurb` sets `attempt=1 if feedback is None else 2`.
   - When `used_words` is not empty, a pass on the first try now saves `attempt: 2` in `blurbs.json`. The log at `pipeline.py:252` also shows "attempt 2".
   - This happens for every chapter except `awards` in each week with `AW.lucky` or `AW.unlucky`. The log line and the saved field are the only consumers, so the page does not change.
   - Fix: give `write_blurb` an `attempt` argument from the loop in `write_and_verify`, or give the used words their own prompt argument with an exact header. The second fix also solves the header note.

Minor 4. `src/cornerstone/verifier.py:497`: on the retry, `feedback = _feedback(result)` replaces the used-word lines.
   - When attempt 1 fails for another cause, such as a number, attempt 2 does not hear "Do not say 'lucky'". The check still catches a "lucky" on attempt 2, and the chapter then falls to the template.
   - This was true before the fix too, so it is not a regression.
   - Fix: prepend `page_word_feedback(used_words)` to the retry feedback.
