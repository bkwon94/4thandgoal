# 08 build: the site renders the known-games line

Status: DONE_WITH_CONCERNS

## Built
- `src/lib/known-games-line.ts`: `knownGamesLine(asOf)` builds the sentence.
- `AsOfLine` in `src/components/analyze-result.tsx` calls it. The finder page reuses `AsOfLine`, so both pages match.
- `src/lib/analyze-types.ts`: new `KnownGames` type. `AsOf` gains optional `completed_through` and `known_games`.
- Site fixtures in `.scratch/site-react/fixtures/` now copy the pipeline fixtures.

## Files changed
analyze-types.ts, known-games-line.ts, known-games-line.test.ts, analyze-result.tsx, analyze-result.test.tsx, trade-finder.test.tsx, two fixtures.

## TDD
- RED: `Failed to resolve import "./known-games-line"` (module missing, 0 tests ran).
- GREEN: 7 of 7 tests pass in `known-games-line.test.ts`.

## Output
- `pnpm test`: 33 files, 285 tests, all pass (page test with no blurb text included).
- `pnpm typecheck`: clean.
- The site has no `lint` script. `typecheck` is the only static check.

## Self-review
- Rendered line is now: "Stats through week 6, plus 14 week 6 games. · Chart week 6 · rosters fetched <time>". The sentence leads, then chart week and fetch time stay.
- Pipeline fixtures changed names and reasons, so the finder test card assertions changed (Jameis Winston, Wan'Dale Robinson).
- The find fixture has stats_through 5 and 0 games, so the finder line reads "Stats through week 5".

## Concerns
- Order and the "." before " · " are my choice. The ticket does not fix the layout of chart week and fetch time.
- No lint script exists in the site.

## Fix round 1
- Renamed the function to `knownGamesSegments` (file `known-games-segments.ts`). It returns an array with no period inside a segment. Each pending count is its own segment.
- `AsOfLine` joins the segments and "Chart week N" with " · ".
- `name.charAt(0)` replaces `name[0]`. The types comment is now a present fact.
- Tests: segment shapes, `{snaps: 9, usage: 1}` case, full-line page case, and a check for no "live", "partial", or "current week".
- `pnpm test`: 33 files, 286 tests, all pass. `pnpm typecheck`: clean.
