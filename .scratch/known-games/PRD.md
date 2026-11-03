# The trade analyzer grades from the known games

**Status:** ready-for-agent
**Date:** 2026-10-26
**Decision record:** `docs/adr/0002-grade-from-known-games-not-the-last-completed-week.md`
**Glossary:** "Known games", "In progress", "Pending", "Before the trade" in `GLOSSARY.md`

## Problem Statement

Brian trades during the week of games. A player plays Thursday night and has a great game, or a bad
one, or gets hurt. On Saturday Brian grades a trade with that player, and the grade is the same as it
was on Wednesday. On Sunday night, after the 1 pm and 4:25 pm games, every grade is still the Wednesday
grade. The analyzer reads every player stat through week N-1 and sees nothing of week N until the
Tuesday build. During the week it is not useful.

The chart is not the problem. The trade value chart reprices once a week and that is right. The
adjusters are the problem. Lineup value, trend and usage, and the injury read all stop at week N-1,
and the hand-kept returns file is the only thing that lowers a hurt player's value.

## Solution

Every player stat a grade reads ends at the known games: weeks 1 to N-1 plus every week N game that
has a stat line on Sleeper, final or in progress. Sleeper posts stat lines during games, within
minutes, and the live fetch already pulls them. The snapshot keeps week N as one more week of history
for player stats only. The standings and the chart week still end at week N-1.

A game in progress counts, and the grade says so. The as-of stamp counts the week N games it read and
the ones in progress. Every factor reason that reads an in-progress game says "game in progress". A
count that Sleeper has not posted yet, such as Sunday snaps until Monday, is pending. The grade skips
that count for that game and never reads it as zero, and the stamp names what is pending.

A player Sleeper tags Out, IR, PUP, or Sus with no week in the returns file takes his projection ahead
as his lineup value, as if due back at week 14. Sleeper projects zero for the weeks he is out, so his
value drops the same day, with no edit to the returns file.

The grade cache keys on a hash of the week N stat lines of the rostered players, so a new fetch with
new numbers is a new grade. The injuries file and the player weeks file refresh every 6 hours, so a
Monday morning grade sees the Sunday snaps and the Sunday WOPR.

## User Stories

1. As a manager, I want a Saturday grade to read a player's Thursday game, so that a trade for him
   prices his latest game.
2. As a manager, I want a Sunday night grade to read every Sunday afternoon game, so that I can trade
   on what I just watched.
3. As a manager, I want a grade at 3:45 pm Sunday to read the 1 pm games in their fourth quarter, so
   that the grade never hides a game that is on.
4. As a manager, I want every factor reason that reads a game in progress to say so, so that I know
   the number can still move.
5. As a manager, I want the as-of stamp to say how many week N games the grade read and how many are
   in progress, so that I know what the grade saw.
6. As a manager, I want the stamp to name a pending count, such as snaps, so that I know why a share
   did not move yet.
7. As a manager, I want a missing snap count to never read as zero snaps, so that a Sunday starter
   never looks benched on Sunday night.
8. As a manager, I want a bad game with targets and red zone usage still there to dock a player a
   little, not a lot, so that one bad box score does not sink a buy.
9. As a manager, I want a bad game with usage gone to dock a player, so that a real decline shows.
10. As a manager, I want a player hurt in his game and tagged Out to lose most of his value that day,
    so that a trade for him grades as the risk it is.
11. As a manager, I want that hurt player's value to recover the day Brian adds his return week to the
    returns file, so that a short absence does not read as a lost season.
12. As a manager, I want a Questionable or Doubtful tag to move nothing, so that the Friday injury
    report does not shake every grade.
13. As a manager, I want the trade value chart to hold all week, so that the market anchor stays
    stable and only our read of the week moves.
14. As a manager, I want the standings to stay at week N-1 until Tuesday, so that a contender does not
    become a seller at halftime.
15. As a manager, I want the finder to read the same known games as the grader, so that the suggested
    trades match the grades.
16. As a manager, I want a repeat grade in the same five minutes to come from the cache, so that the
    analyzer stays fast.
17. As a manager, I want a grade after a new stat line to be a new grade, so that a Wednesday grade
    does not serve all week.
18. As a manager, I want the Monday morning grade to see the Sunday snaps and WOPR, so that the usage
    read is one morning behind, not one day.
19. As a manager, I want the Tuesday build and the saved history to work as before, so that the weekly
    report never changes because of this.
20. As a manager, I want a week N stat fetch that fails to leave the grade at week N-1 and say so, so
    that an outage reads as stale and never as a quiet game.
21. As a manager, I want the trend and usage reason to give the week N numbers it read, so that I can
    check the claim against the box score.
22. As a manager, I want the site to show the known-games stamp under the decision, so that I see
    the bound without a tooltip.
23. As Brian, I want a saved week to grade the same as before, so that every existing rubric test
    passes unchanged.
24. As Brian, I want the expected gap to keep its weekly lag with no change, so that the expected
    points file stays a Tuesday source.

## Implementation Decisions

- **The known-games week.** The snapshot build takes the live raw fetch, which already holds the week
  N stat lines from Sleeper, and parses week N with the same parse as a saved week. Week N joins the
  history for player stats when it has at least one stat line. The player stat bound, the `through`
  that the stat readers take, becomes N in that case. The standings keep their own bound at N-1. A
  saved week, with no week N raw, grades exactly as today.
- **Two bounds in the as-of stamp.** The stamp splits the single stats-through week into the player
  stat bound and the standings bound, and adds a known-games block: the count of week N games read,
  the count in progress, and the pending counts by name. The result document carries the block. The
  site renders it as one line under the decision.
- **Final or in progress.** A week N game is in progress when now is past its kickoff by less than 4
  hours 30 minutes. The kickoff comes from the nflverse schedules file, which is already a refreshed
  source, matched by season, week, and NFL team. A game with no schedule row counts as final. No new
  source. The label never changes which games count, only how the stamp and the reasons describe them.
- **Pending counts.** A week N stat line with a game played and no snap count is pending for snaps.
  The snap share reader skips that game. The target share reader and the points reader use it. The
  red zone reader uses it. The WOPR window reads the week N row of the nflverse player file when the
  file has it, and ends at N-1 otherwise, with the stamp naming WOPR as pending.
- **The in-progress label in reasons.** The trend and usage reason, the roster fit reason, and any
  reason that quotes a week N number of an in-progress game adds "game in progress" to that player's
  sentence. The adjuster steps do not change because of the label.
- **Out with no return week.** The due-back rule widens: a player whose Sleeper injury status is in
  the out set and who has no week in the returns file counts as due back at the standing adjuster's
  return-by week, 14. His lineup value is then his projection ahead from that week, as for any
  due-back player. The injury adjuster still docks one step for out with no near return. A player with
  a week in the returns file grades as today.
- **The cache key.** The grade cache key and the finder cache key add a hash of the week N stat
  lines of the players on the two rosters: the fields the readers use, which are points, games played,
  snaps, team snaps, targets, red zone targets, and red zone rushes. The document version bumps.
- **Refresh cadence.** The refresh takes a max age per source. The injuries file and the player weeks
  file take 6 hours. Every other source keeps 24 hours. The refresh route and the start-up refresh
  pass the per-source ages the same way.
- **The Tuesday roll.** On the Tuesday after the cutoff the trade week rolls to N+1 and week N is the
  last completed week. The live path already saves it to the history then. Nothing in that path
  changes. The known-games week is then week N+1, with no stat lines until Thursday night.
- **A failed week N fetch.** The live fetch of the week N stats is part of the raw fetch today. When
  the stat lines are missing or empty, the known-games week is N-1, the stamp says stats are stale,
  and the grade runs as today.
- **Prose rules.** "Known games", "in progress", and "pending" are the words, per the glossary. No
  reason says "live", "partial", or "current week".

## Testing Decisions

- A good test gives a raw week and a history and checks the snapshot, the grade, or the document.
  It never reads a private helper. It names the week, the game, and the number it expects.
- **The snapshot build.** A live raw with week N stat lines gives a snapshot whose player stat bound
  is N, whose standings bound is N-1, and whose stamp counts the games read, the games in progress by
  the kickoff rule with a fixed clock, and the pending snaps. A raw with no week N lines gives today's
  snapshot. A saved week gives today's snapshot. Prior art: the snapshot tests and the live tests.
- **The rubric.** A fixture history plus a partial week N: lineup value moves with the new game,
  trend and usage reads the new target share and skips the pending snaps, the reason carries "game in
  progress" when the clock says so, and an Out player with no return week takes his projection ahead.
  Every existing rubric test passes unchanged. Prior art: the rubric tests and ticket 10 of the
  nflverse feature.
- **The API.** The cache key changes when a week N stat line of a rostered player changes and ignores
  a stat line of a player on neither roster. The document carries the known-games block. The finder
  reads the same bound. Prior art: the cache key tests in the API tests.
- **The refresh.** An injuries file 7 hours old refreshes on the live path. A schedules file 7 hours
  old does not. Prior art: the day-old refresh tests in the live tests.
- **Real-data check.** On a game day, one live grade through `make analyze` with a player who played
  that day, and the stamp and the reason read by hand.

## Out of Scope

- A live scoreboard source for game status.
- Any move on a Questionable or Doubtful tag.
- Odds, game totals, and spreads.
- The expected gap in week. The expected points file stays a Tuesday source.
- A change to the start letter or the chart week during the week.
- A change to the Tuesday build, the weekly report, or the saved history.
- The start-or-sit feature. Its handoff is `.handoff/cornerstone-start-sit.md`.

## Further Notes

- Sleeper posts the Sunday snap counts on Monday. Targets, red zone touches, and points post during
  the game. The research of 2026-10-26 saw 338 week 7 stat lines on a Monday with snaps for the
  Thursday game only.
- The nflverse player file update time during the week is a fact the first ticket must confirm. The
  design holds either way, because the WOPR window reads the file when it has the row.
- The longest NFL game in recent seasons ran under 4 hours 30 minutes. If a game runs past that, its
  label flips to final while it is still on. The numbers still count either way.
- The site change is one ticket in the site repo: read the known-games block and render one line.
