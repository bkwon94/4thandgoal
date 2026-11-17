# The analyzer counts an injury only for Out or Doubtful

Kind: quick-win
Status: in-progress
Branch: `win-injury-out-doubtful`.
Source: the session of 2026-11-17.
Boundary: holds. 3 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The injury Measure reads only Out and Doubtful

Done condition: The injury Measure reads against a side only for a player it gets who cannot play in the trade week (Out, IR, PUP, NA, Sus, or out for the season) or who is listed Doubtful, and never for a Questionable status or a count of injury report weeks alone.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 2. The injury facts name only Out and Doubtful

Done condition: The injury fact of the trade fact sheet and of the sell high sheet names an injury only for a player who cannot play in the trade week or who is listed Doubtful, and holds no count of injury report weeks.
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
