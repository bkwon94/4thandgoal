# Player data from nflverse in the report and the analyzer

**Status:** done 2026-10-24, tickets 01-09 on main `5a1d6ab`
**Date:** 2026-10-24

## Problem Statement

The weekly report says who scored, never why. A wide receiver who caught two touchdowns on three
targets reads the same as one who caught nine balls for 140 yards. The awards chase one touchdown.
The position leaders praise a score with no word on the volume behind it. The next week chapter
cannot tell a shootout from a slog.

The trade analyzer grades a side on snap and target share direction and red zone touches. It never
sees whether a player's points match his volume, so a buy-low and a real decline grade the same.
And the target count behind that share is ours, from our own play filter, and it counts two-point
tries as targets. It is 34 targets too high this season.

The data to fix all of this sits in files we already pull or one download away: the nflverse
weekly player file, the ffopportunity expected points, and two columns of the play by play we hold.

## Solution

Three new reads, each a flag in the build record so a missing week never stops a build:

1. The nflverse weekly player file gives target share, air yards share, and WOPR per player per
   game. The target count and the target share switch to it. Our own count stays for carries, red
   zone touches, and snaps.
2. The ffopportunity file gives expected points per player per game, rescaled to the league's
   half-PPR scoring. The expected gap, actual minus expected, is the new signal.
3. The play by play gives EPA and pass rate over expected per team per game.

The report gains three fact families. The awards chapter gets an unlucky award and a lucky award
from the expected gap. The position leaders chapter gets a volume line, WOPR for a WR or TE and
carry share for an RB. The next week chapter gets a shootout fact per NFL game where both teams
lean pass.

The trade rubric gains an expected gap adjuster behind a tunable that starts off. The trend
adjuster reads the nflverse target share and uses the WOPR direction as the tiebreak before red
zone touches. Before any of that, the target count drops two-point tries, as its own change.

## User Stories

### A reader of the report

1. As a reader, I want an unlucky award, so that I know which starter's volume outran his score.
2. As a reader, I want a lucky award, so that I know which score the volume does not support.
3. As a reader, I want no award when nobody clears the floor, so that a quiet week stays quiet.
4. As a reader, I want the expected gap in the award with the two numbers, so that I see the size of it.
5. As a reader, I want a volume number beside each position leader, so that a lead on volume reads apart from a lead on luck.
6. As a reader, I want the leader's rank on that number at his position, so that "first among tight ends" is a fact and not a flourish.
7. As a reader, I want a shootout note in the next week chapter, so that I know which NFL game to watch.
8. As a reader, I want the shootout note to name the league starters in that game, so that I know whose week it is.
9. As a reader, I want every new number cited by a fact, so that the verifier still rejects an uncited number.
10. As a reader, I want the facts to say which week the expected points cover, so that a lagged week never reads as the current one.
11. As a reader, I want a chapter that lacks a source to read as it does today, so that a missing file never leaves a hole in the page.

### A manager in the trade analyzer

12. As a manager, I want a side that gets players who score under expected to step up, so that a buy-low shows in the grade.
13. As a manager, I want a side that gives players who score over expected to step up, so that a sell-high shows in the grade.
14. As a manager, I want the expected gap adjuster's reason to name the player and the gap, so that I can check the claim.
15. As a manager, I want a handcuff or a player due back left out of the expected gap, so that a player with no recent games never moves a grade.
16. As a manager, I want the trend adjuster to read the nflverse target share, so that the analyzer and nflverse agree on a player's targets.
17. As a manager, I want the WOPR direction to break a flat trend before red zone touches, so that a deep target counts for more than a screen.
18. As a manager, I want the expected gap adjuster off until a real trade checks out, so that a live grade never changes on an untested rule.
19. As a manager, I want the two-point fix to go out alone, so that one change at a time touches the live grades.

### The pipeline on Tuesday

20. As the pipeline, I want each new file as a source flag in the build record, so that the page and the log say what a week lacked.
21. As the pipeline, I want the expected points file checked for the Monday night game, so that an early build reads the last full week and says so.
22. As the pipeline, I want the new files read through the existing cache with the same max age, so that a rebuild makes no network call.
23. As the pipeline, I want one agreement test between our target count and the nflverse count on the week 6 fixture, so that the switch compares like with like.
24. As the pipeline, I want EPA and pass rate over expected read only from pass or run plays, two-point tries left out, so that no null reaches a fact.

## Implementation Decisions

### The two-point fix

- The play columns gain `two_point_attempt`. The target count and the carry count skip a play
  where it is 1. The nflverse rule is "receiver set and no two-point try", and it matches the
  nflverse target count in 186 of 186 team weeks of 2026, weeks 1 to 6.
- This is its own change, first in the order. It moves live trade grades, so it goes out alone.

### The nflverse weekly player file

- One new download, `stats_player_week_{season}.csv.gz` from the nflverse stats_player release,
  through the existing cache. The file keys players by gsis id, and the existing id map joins it.
- The reader returns targets, target share, air yards share, and WOPR per player per week for the
  QB, RB, WR, and TE positions, over the same saved window as the usage.
- The usage week gains `air_yards_share` and `wopr`. Its `targets` and `target_share` come from
  this file when the file is there, and from our count when it is not. The source flag says which.
- The agreement test compares our count after the two-point fix with the file on the week 6
  fixture. The switch lands only with that test green.
- Our carry count leaves out QB scrambles and kneels, so it runs under the file's `carries` for a
  QB by 1 to 10 a week. Carries stay our read, so no fact reads the file's carries.

### Expected points

- One new download, `ep_weekly_{season}.csv` from the ffopportunity `latest-data` release, through
  the existing cache. One row per player per game, keyed by gsis id, full PPR.
- The reader rescales to the league: `total_fantasy_points_exp - 0.5 * receptions_exp +
  1 * pass_interception_exp`. The league pays half a point per reception where the file pays one,
  and minus one per interception where the file pays minus two. Fumbles have no expected column
  and stay out. The reader reads the reception and interception weights from the league scoring,
  so a scoring change never silently breaks the rescale.
- The reader returns expected points per player per game, and the week it reads through. It does
  not return the file's actual points. The file charges a lost fumble but not a fumble kept, and it
  has no return touchdowns, so its actual never matches the box score. The expected gap is the
  league's own points from Sleeper minus the expected points, computed where the points are at
  hand: the sheet for the report, the snapshot for the rubric.
- The file rebuilds the whole season on Tuesday morning. The last four uploads landed between
  06:26 and 08:57 ET, and two of four landed after the 08:00 build. The reader checks the file for
  the Monday night game id of week N. When it is there, the facts read week N. When it is not,
  the facts read through week N-1 and say so. No wait and no build move.
- The expected window is the last 3 games a player played. A player with fewer than 2 games in
  it has no gap. A game he did not play is not in the window.
- A lagged file sets the source flag false, which the build record defines as missing or
  incomplete, and the extract is not saved. The expected data in memory still carries the week it
  reads through, so the facts can say "through week N-1".

### Team EPA and pass rate over expected

- No new download. The play columns gain `epa` and `pass_oe`. The team week gains the sums per
  game over pass and run plays with two-point tries left out, where both columns are always
  present.
- The environment reader returns EPA per play and pass rate over expected per team per week.

### The report

- Three fact families join the sheet, built in the nflverse facts module as the drop facts are.
- `AW.unlucky` and `AW.lucky`: the started player with the largest expected gap under zero, and
  over zero, in week N, each with a floor of 5 points. The fact holds the actual, the expected,
  and the gap. No fact when no starter clears the floor. The awards chapter may cite them. The
  awards prompt rule says what the award means in one line, as the other awards have.
- `LEAD.{position}.{rank}.volume`: for each position leader, WOPR for a WR or TE and carry share
  for an RB, in week N, with his rank on it at the position league wide. None for a QB, a K, or a
  DEF. The position leaders chapter may cite them.
- `NX.shootout.{game}`: one per NFL game of week N+1 where both teams have a positive pass rate
  over expected over the last 3 games each played, with the league starters of week N in that
  game, the count first and the names capped at 8. The rate shows in percentage points to one
  decimal. The next week chapter may cite them. The writer picks the one with the most starters.
- When the expected points read through week N-1, there is no unlucky or lucky award fact for
  week N, and the awards chapter builds without them. The leader and shootout facts do not
  depend on that file.
- A chapter whose source is missing builds without the family and reads as it does today.

### The trade rubric

- A new adjuster, expected gap, last in the adjuster order. It reads the mean per-game expected
  gap over the expected window of the players a side gets, and the same for the players it gives.
  A side steps up one when its gets run under expected by `EXPECTED_GAP` or more, or its gives run
  over by the same: it buys low or sells high. A side steps down one when its gets run over
  expected by the gap, or its gives run under: it buys high or sells low. An up case and a down
  case together give no step. The reason names the players and their gaps.
- Handcuffs and players due back do not count, the same rule as the trend adjuster, and the
  shared rule lives in one place.
- `EXPECTED_GAP` starts at 3 points per game. `EXPECTED_ADJUSTER_ON` starts false, so the
  adjuster appears in no breakdown until a real trade checks out. Both are tunables with a reason
  comment.
- The trend adjuster keeps the Sleeper target share. On real data the Sleeper weekly target counts
  equal the nflverse counts every week, so a source switch buys nothing, and the saved extracts
  never reach the live API on Fly. When the snap and target shares are flat, the WOPR direction
  decides for a WR or TE before red zone touches. The WOPR comes from the nflverse weekly player
  file in the cache, read by the slow sources through week N-1 as the expected points are, and
  the file joins the API refresh. The swing is a tunable of its own, about 8 WOPR points, since
  WOPR is 1.5 times target share plus 0.7 times air yards share.
- The snapshot the API refreshes carries the expected games and the WOPR per player per week,
  read from the cache, with the two files in the refresh list so Fly downloads them.

### The lineup value of a player due back

- The roster fit adjuster values a player due back by his Sleeper projection ahead, the mean of his
  weekly projections from his return week through the last regular week, in place of his recent
  points per game, which are 0 for a player who missed the last 4 weeks. Every other player keeps
  his recent points. The start letter already comes from the consensus chart, and the trend and
  expected gap adjusters already skip a due-back player, so this closes the last hole for an
  injured top player. Ticket 10, added 2026-10-24 on Brian's Lamar Jackson case.

### The glossary

- The terms are in `GLOSSARY.md` under "Player data from nflverse": target, target share, WOPR,
  expected points, expected gap, expected window, pass rate over expected, shootout, unlucky
  award, lucky award.

## Testing Decisions

- A good test feeds inputs at a seam and asserts the output. It never asserts a weight or a
  column order.
- Reader seam: each new reader returns rows from a small fixture file in the nflverse fixtures
  folder. Cases: a player with no gsis id is skipped; a missing file returns None and the source
  flag is false; the rescale matches the league scoring on one hand-computed row; the Monday
  night check reads week N when the game is there and week N-1 when it is not; EPA and pass rate
  over expected skip two-point tries. Prior art: the usage reader tests and the drops reader tests.
- Agreement seam: our target count after the two-point fix equals the nflverse count for every
  team week in the play by play fixture.
- Fact seam: the sheet on the week 6 fixture with hand-set expected gaps, WOPR, and pass rates
  yields the three families. Cases: no award under the floor; the award names the two numbers;
  the leader volume rank is league wide at the position; a shootout fact only when both teams
  lean pass; the facts say "through week N-1" on a lagged file; every number in a fact's text is
  in its numbers; a chapter with the source missing cites no family. Prior art: the nflverse facts
  tests and the sheet tests.
- Rubric seam: the grade on a fixture snapshot with hand-set gaps. Cases: a side that gets a
  player 4 under expected steps up; a side that gives a player 4 over steps up; both cancel; a
  handcuff's gap does not count; a player with one game has no gap; the adjuster is absent with
  the tunable off; a flat trend with WOPR up steps up before red zone touches. Prior art: the
  rubric tests.
- Build seam: the build on the fixture writes the source flags for the two new files. Prior art:
  the pipeline tests.
- One prompt text test pins the awards rule line for the unlucky and lucky awards.

## Out of Scope

- The waiver board and the trade finder. Both are hidden, so they wait. Brian deferred them on 2026-10-24.
- The power rankings. Brian cut the luck fact on 2026-10-24.
- Next Gen Stats. Its only consumer was the sneaky WR fact on the waiver board.
- Betting lines. Brian said so on 2026-10-24.
- Pass rate over expected in the waiver board's environment score. That change waits with the board.
- A site change. Every new number arrives as a fact in text.
- An expected fumble term. The file has none.

## Further Notes

- The research with URLs is in `.scratch/nflverse/research.md`. The inventory of what we pull is
  in `.scratch/waiver/pipeline/nflverse-inventory.md`. The inventory's note that the expected points file
  arrives Friday is wrong; it rebuilds Friday, Sunday night, Monday, and Tuesday.
- Not confirmed: what starts the on-time nflverse dispatch runs. If they stop, the play by play
  and the player file land between 06:17 and 12:53 ET on Tuesday, and the source flags cover it.
- Order: the two-point fix, the player file reader, the expected points reader, the EPA and pass
  rate columns, the three report families, the rubric adjuster and the trend switch.
