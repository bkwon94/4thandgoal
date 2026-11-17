# The analyzer counts an injury only for Out or Doubtful

Kind: quick-win
Status: in-progress
Branch: `win-injury-out-doubtful`.
Source: the session of 2026-11-17.
Boundary: holds. 3 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The injury Measure reads only Out and Doubtful of the trade week

Done condition: The injury Measure reads against a side only for a player it gets who is out for the season, on IR, PUP, NA, or Sus with no near return, or listed Out with no near return or Doubtful by the NFL game status of the trade week, so a Sleeper Out or Doubtful with no NFL game status for the trade week, an Out with a near return, a Questionable status, or a count of injury report weeks never counts.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 2. The injury facts name only Out and Doubtful

Done condition: The injury fact of the trade fact sheet and of the sell high sheet names an injury only as the rule of item 1 reads it, gives the latest NFL practice status of the trade week in place of a Sleeper Out that has no NFL game status yet, and holds no count of injury report weeks.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 3. The Week line reads the NFL game status of the trade week

Done condition: The Week line reads a player as out in the trade week for an NFL game status of Out or Doubtful, and never for a Sleeper Out or Doubtful with no NFL game status for the trade week.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

## Comments

- Item 3 reverses rule 4 of `.scratch/grade-clarity/decisions/02-research-depth-chart-freshness.md`, "Questionable and Doubtful never count", for Doubtful only.
- Brian, 2026-11-17: the status must be the one of the current week. An Out from the last week needs the reports of this week. The snapshot holds the NFL injury report by week (`Snapshot.injuries`), and `week_line.py` already marks Tuesday and Wednesday as the days of a stale Out (`LAST_GAME_DAYS`).
- Brian, 2026-11-17: an Out with a near return stays news, with no mark. The NFL practice status fills the days before the game status. Source: the nflverse file `injuries_<season>.csv.gz` (`INJURIES_URL`), from the NFL injury API.
- The case of Brian: Kenneth Walker III, Sleeper id `8151`, KC. He missed week 10 and news has him back in week 11. On 2026-11-17 the Sleeper file has him `Out` (groin), and `data/nfl/2026/returns.json` has no row for him. Today the injury Measure reads him against the side that gets him: "out with no return week on file". His Out must not count in the trade. Build the red test of item 1 on this case.
