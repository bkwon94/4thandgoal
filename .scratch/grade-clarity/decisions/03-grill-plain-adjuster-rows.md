# 03: The plain words of each adjuster row

Map: `.scratch/grade-clarity/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The breakdown shows 7 adjuster rows: roster fit, standing, trend and usage, injury, handcuff, schedule, and expected gap. Each row has a step and a reason that the code writes in `adjusters.py`. Brian finds the reasons hard to read. Some text also names the value chart, such as the note of a week with no chart and the reason of an unlisted player.

The grill takes each row and each place that names an inner part, with a real example of today's text. Brian picks the plain words for each. The spec needs the label and the reason form of each row.

## Decision

Brian decided each row on 2026-11-05, in a grill on a real grade: roster 10 gives Omar Cooper Jr. to roster 6 for Parker Washington.

The form of every row:
1. A row shows only when it moves the grade or says something new. A row such as "No player it gets is a handcuff" hides.
2. The mark (up, down, or even) shows the step. The text never says "one step up" or "no step".
3. One short sentence in a manager's words. The text never says "trade value", "highest-value", "best lineup", "the line", "hole", "win-now move", "return bet", "star", or "opportunity". "The better player" replaces "the highest-value player".

The rows:
- **The deal** (the start letter): "You get far more than you give." It names no source.
- **Roster** (roster fit): the count of players above the line at each position the trade touches, with the line as a plain rank. "You keep 3 WRs in the top 36, and you get the better player." "You go from 2 RBs in the top 24 to 1."
- **Standing:** the race, the need, and whether the trade meets it. "Out of the playoff race, so you want the better player for the rest of the season, and you get him." "In a playoff spot, so you need points now, and this trade gives some up."
- **Usage** (trend and usage): one clause per player, with the numbers kept and no weeks.
  - WR and TE: snap share, target share, and air yards per target.
  - RB: snap share, carry share, and target share.
  - QB: no usage row.
- **Injury:** "Cooper is out until week 11. He was on the injury report in 5 of 8 weeks."
- **Upside:** "Cooper is a top WR, due back in week 11." "Spears gets more work while Pollard is out."
- **Handcuff:** "Spears backs up your RB, Pollard, on the Titans depth chart."
- **Schedule:** names the players, the bye weeks after the Week line, and each playoff opponent with its rank at the player's position. "Washington faces TEN (3rd most points to WRs), CLE (8th), and HOU (25th) in weeks 15 to 17." The last sentence "The schedule leans for this side" goes.

The Week line names the opponent of each week the same way: "Week 9: Washington plays at TEN, 3rd most points to WRs." The rank is the points allowed per game at the position, from `league/points_allowed.py`. Rank 1 gives up the most.

The value chart:
- "Chart week N" leaves the as-of line.
- The note for a week with no values becomes "This week's player values are not out yet, so both sides start even."

The expected gap row is off (`EXPECTED_ADJUSTER_ON = False`), so it is not in this decision. Route share has no source in the cached nflverse files, so it is out of scope.
