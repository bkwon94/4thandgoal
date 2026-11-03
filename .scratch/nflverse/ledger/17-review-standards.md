# 17 — standards review

Verdict: pass with one Important finding. Diff `e29e2b4..f553825`.

## Critical

None.

## Important

1. `src/cornerstone/pipeline.py:181-187` — A degraded refetch returns the fresh extract and drops the saved `drops` and `injuries`. Before this change, a week 6 rebuild kept them. This is a loss of facts when the play by play is down. Fix: when `saved` is set and the refetch is degraded, return `saved` and log one line, or ask the owner to accept the loss.

## Minor

1. `tests/test_pipeline.py:848` — `"usage" in caplog.text` is a weak check, because other log text can hold "usage". Fix: assert the full line `"nflverse.json lacks environment, expected, next_games, usage"`.
2. `tests/test_pipeline.py:846` — `bundle` is not used. Fix: write `_, record = make_bundle(...)`.
3. `src/cornerstone/pipeline.py:177` — `(saved is not None and not missing) or nflverse is None` is dense. Fix: optional; split into two `if` lines with one return each.

## Checks that pass

- `model_fields_set`: `NflverseWeek` sets no `model_config`, no alias, and no `populate_by_name`. A run in the worktree gave these results. An old four-key file reports `environment, expected, next_games, usage` as missing. A file with the four keys present as `null` reports none missing. A `model_dump_json` round trip reports none missing, so a fresh save always passes the check.
- Exception width: the broad `except Exception` is the old outer guard with its `noqa` reason. The fetcher catches only HTTP errors, so a narrow catch here lets a parse error or `KeyError` stop the build. The width is correct. The `saved` value is set before the fetch, so a failure in `load_nflverse` still returns `None`.
- Scope: only `_nflverse_for_week`, two tests, one helper, and the ticket boxes change. No other raw file loads again.
- Style: line length is under 120. Log text matches the "build goes on" form of the old lines. No old comment is removed. The docstring stays true and adds the refetch rule.
- Names: no "new", "improved", or "enhanced". No mock mode. The fakes are the old test fetchers.
- STE: the comments and the docstring use active voice and present tense, with no `-ing` verb.
- Tests: names say what they check. `_old_extract` is five lines and clear. The failed-refetch test checks the file bytes and `drop_source == "nflverse"`, which are real values.
