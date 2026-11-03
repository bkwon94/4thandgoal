# Ticket 15 review: standards

Diff: `e29e2b4..HEAD` on `nflverse-15` (`dd1474c`, `e33f039`).
Verdict: no Critical and no Important finding. Three Minor findings.

## Critical

None.

## Important

None.

## Minor

1. `src/cornerstone/verifier.py:355`: the comment uses the passive voice ("The chapters are written one at a time").
   Fix: write "The build writes the chapters one at a time, so it passes in the words that the other chapters used."
2. `src/cornerstone/verifier.py:123-125`: `page_words` takes `Chapter | None`, and no comment says why the `None` shape exists.
   Fix: add one line that says a saved blurb can have no chapter in the sheet, so no names are removed for it.
3. `tests/test_pipeline.py:860`: `Blurb` comes from a local import, but the file imports `cornerstone.models` at line 22.
   Fix: add `Blurb` to the top import block and remove the local import.

## Checks that pass

- Scope: the change touches `verifier.py`, `pipeline.py`, two test files, and the ticket file only. Nothing is outside the ruled ticket.
- `used_words`: `code_check`, `verify_blurb`, and `write_and_verify` read it as `Collection[str]` and never mutate it.
- `run_build` (pipeline.py:290-293): the loop owns `used` and grows it with `|=` after each call. The mutation is local and clear.
- `run_rewrite` (pipeline.py:371) and `run_rankings` (pipeline.py:445): each builds a fresh set from `_other_page_words`. The set excludes the chapter in the rewrite.
- Regex: `whole_word` uses `(?<!\w)word(?!\w)` with `re.IGNORECASE`, so "unlucky" does not match "lucky" and "LUCKY" matches.
- Names: `page_words` uses `remove_names(without_urls(...))`, the same helpers and order as the `bare` text in `code_check` (verifier.py:304).
- `page_words` has one job. The pipeline calls it in one shape, `(blurb, chapter)`; only `_other_page_words` can pass `None`.
- Docstrings stay true. No comment is removed. No name uses "new", "improved", or "enhanced". No mock mode.
- Tests assert exact failure strings and exact sets. Test names say what they check. The spy copies `used_words`, so the aliasing in `run_build` does not hide a fault.
- Line length stays at 120 or fewer in all added lines.
