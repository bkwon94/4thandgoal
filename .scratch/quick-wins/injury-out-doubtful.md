# The analyzer counts an injury only for Out or Doubtful

Kind: quick-win
Status: in-progress
Branch: `win-injury-out-doubtful`.
Source: the session of 2026-11-17.
Boundary: holds. 3 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The injury Measure reads only Out and Doubtful

Done condition: The injury Measure reads against a side only for a player it gets who is out for the season, on IR, PUP, NA, or Sus, or listed Out or Doubtful for the trade week, where the NFL injury report of the trade week decides Out or Doubtful when it lists him, a Sleeper Out or Doubtful from the last game on a Tuesday or Wednesday with no such report row never counts, and a Questionable status or a count of injury report weeks alone never counts.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 2. The injury facts name only Out and Doubtful

Done condition: The injury fact of the trade fact sheet and of the sell high sheet names an injury only for a player whom the rule of item 1 counts, says "his Out is from the last game and the report of this week is not out yet" for a stale Sleeper Out, and holds no count of injury report weeks.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 3. The Week line counts Doubtful in the trade week

Done condition: The Week line reads a Doubtful player as out in the trade week, the same as an Out player, and as able to play in the next week.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

## Comments

- Item 3 reverses rule 4 of `.scratch/grade-clarity/decisions/02-research-depth-chart-freshness.md`, "Questionable and Doubtful never count", for Doubtful only.
- Brian, 2026-11-17: the status must be the one of the current week. An Out from the last week needs the reports of this week. The snapshot holds the NFL injury report by week (`Snapshot.injuries`), and `week_line.py` already marks Tuesday and Wednesday as the days of a stale Out (`LAST_GAME_DAYS`).
