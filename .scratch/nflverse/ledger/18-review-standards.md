# 18 — standards review

Diff: `e29e2b4..6e9b528` on `nflverse-18`.

Verdict: no Critical. Two Important. Four Minor.

## Scope

- `cli.py`, `slow_sources.py`, and `snapshot.py` are each needed. The ticket says the snapshot marks the three
  sources as missing. `slow_sources.py` is where `missing` comes from. `SLOW_SOURCES` keeps the no-loader case equal
  to the loader case.
- The fourteen changed assertions are needed. Each one pinned the old rule that an absent expected points file or
  weekly player file is not missing.
- The three rewritten comments were false after the change. The module docstring said "except the expected points
  and the WOPR". The two field comments said "a None here is not in `missing`". All three are true now.
- No other comment in `src` or `tests` still says "not in `missing`" or "misses nothing".

## Critical

None.

## Important

1. `tests/test_cli.py:288-292` — the drift test is a tautology. `_SOURCE_NAMES` values come from
   `REFRESHED_SOURCES`, so the subset check passes by construction. It does not check the keys against
   `snapshot.SLOW_SOURCES`, which is where a real drift breaks the line.
   Fix: assert `set(cli._SOURCE_NAMES) == set(SLOW_SOURCES)` beside the subset check.
2. `src/cornerstone/cli.py:136-140` — the index-2 splice and `name.replace(" ", "_")` are fragile. A reorder of
   `REFRESHED_SOURCES` moves "points allowed". A rename such as "id map" to "ffids" breaks the key match with no error.
   Fix: write `_SOURCE_NAMES` as a plain seven-entry literal dict, and let the fixed test of item 1 guard the drift.

## Minor

1. `src/cornerstone/cli.py:134` — "come from the history, not from a refresh, so the line puts them after the depth
   charts" gives a false cause. The source of the data does not set the print order.
   Fix: say the order matches the old line, or drop the "so" clause.
2. `tests/test_slow_sources.py:90` and `:104,111` — `"expected_points" in sources.missing` is weaker than the exact
   lists in the other tests of the file.
   Fix: assert `sources.missing == NOT_IN_CACHE` there, and `== ["player_weeks"]` after the id map unlink plus `id_map`.
3. `tests/test_slow_sources.py:24` — `test_load_slow_sources_gives_every_source` now asserts two sources missing, so
   the name is no longer true.
   Fix: rename to `test_load_slow_sources_gives_every_source_in_the_cache`.
4. `src/cornerstone/cli.py:142` — `_JOIN_ONLY` is a hard-coded key beside derived keys. With the literal dict of
   Important 2, this mix goes away.
   Fix: keep it, but define it next to the literal `"id_map"` entry.

## Rules with no finding

- No "new", "improved", or "enhanced" name. No mock mode.
- Style matches the file: module-level comments above constants, f-strings, line length under 120.
- Comments are in STE: active voice, present tense, no `-ing` verb.

## Re-review of fix round 1

Diff: `6e9b528..f851530`.

Verdict: all five findings ADDRESSED. One new Minor.

1. Tautology test — ADDRESSED. `tests/test_cli.py:293` asserts the keys equal `SLOW_SOURCES`. That check can fail.
2. Index-2 derivation — ADDRESSED. `src/cornerstone/cli.py:135-138` is a plain dict of seven names. `cli.py` does not import `REFRESHED_SOURCES`.
3. False print-order comment — ADDRESSED. The false cause is gone.
4. False test names — ADDRESSED. Both names now say what the test checks.
5. Weak `in` asserts — ADDRESSED. All three asserts now check the exact list, and the expected values are correct.

### New Minor

1. `src/cornerstone/cli.py:133` — "keep the order of the line before the nflverse files joined it" tells the history of the code. The repo rule says comments are evergreen.
   Fix: drop the line. The comment above it already says the dict is in print order.
