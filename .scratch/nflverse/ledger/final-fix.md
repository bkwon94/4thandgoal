# Final fix wave

Branch `nflverse-final` in the worktree `cornerstone-fantasy-sleeper-weekly-report.nflverse-final`. Base main `3dfd0fd`. Not pushed. Not merged.

Commits:

1. `5a82296` nflverse: keep the used words on the retry and key only due-back rows (items 1 to 5).
2. `e57445d` nflverse: fix the STE breaks in the comments of tickets 11 to 18 (STE table and the history comment).

## Items

1. Important 1, `verifier.py` retry: done. Each attempt now gets the used-word lines through their own argument. The retry feedback holds only `_feedback(result)`. Test first, red for the right reason, then green.
2. Important 2, `cache.py` key: done. `_content_hash` builds `due_back` with `week > snapshot.as_of.stats_through`. Both the `returns` and the `projections_ahead` comprehensions read it. Test first, red, then green.
3. Minor 1 and Minor 3: done. About 25 source lines.
   - `writer.py` has `PAGE_WORDS_HEADER = "Words this page already uses:"`. `build_writer_prompt` takes `page_words`. `write_blurb` takes `page_words` and `attempt`.
   - `write_and_verify` loops `for attempt in (1, 2)` and passes the number. A first-try pass saves `attempt: 1`.
   - Attempt 1 no longer gets "Feedback from the last attempt:".
   - `prompts/writer.md` rule 14 now names the "Words this page already uses:" section. Its first sentence is true again, because only a retry gets feedback.
   - `page_word_feedback` keeps its name. Its docstring no longer calls the lines first-attempt feedback.
4. Minor 2: done. `DOCUMENT_VERSION = 5`. The comment above it stays as the reason.
5. Minor 4, 5, 6: done.
   - Minor 4: the `_content_hash` docstring names the hand-kept returns file and the daily Sleeper projections.
   - Minor 5: rule 8 of `writer.md` adds 'Say "unlucky" at most once per page.'. The `verifier.py` comment names both words, in the STE form of the table row. `tone.md` is unchanged, because the review fix names `writer.md` only.
   - Minor 6: the `pipeline.py` comment uses the review text.
6. STE table: done, every row. The history comment at `cli.py:133` is deleted. Two docstrings got a line wrap to stay under 120 characters.

## Tests added

- `tests/test_verifier.py::test_the_retry_still_hears_the_used_words`: attempt 1 fails for an unsupported sentence. The second `write_blurb` call still gets "Do not say 'lucky'".
- `tests/test_api.py::test_the_cache_key_ignores_the_projection_rows_of_a_player_already_back`: a return week equal to `stats_through`, and a projection change, leave both keys unchanged.
- Changed: `test_the_first_writer_call_hears_the_used_words` now checks the exact header, no feedback header on attempt 1, and `attempt == 1`.
- Changed: `test_retry_sets_attempt_two_and_passes_feedback` passes `attempt=2`, because the loop now sets the number.

## Checks

- `uv run pytest -q tests/test_verifier.py tests/test_api.py tests/test_writer.py`: `248 passed, 1 deselected in 67.23s (0:01:07)`
- `uv run pytest -q`: `1081 passed, 9 deselected in 151.94s (0:02:31)`
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` Same as the base.

## Left

Nothing from this wave. The "Leave" list of the review stays for a later cleanup.
