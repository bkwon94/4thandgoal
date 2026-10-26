# Rubric

The rubric grades each side of a proposed trade with a letter from A to F. Code sets the start
letter. The numbers live in the tunable table, `src/cornerstone/tunables.py`. This file names them
and never repeats their values, so the table is the one place to change a number.

## Letters

- A: the side gets far more than it gives.
- B: the side gets more than it gives.
- C: the two sides are about even.
- D: the side gives more than it gets.
- F: the side gives far more than it gets.

## Start letter

Each side gets a start letter from the trade value of the players it gets and the players it
gives. Divide the sum it gets by the sum it gives. Find the band of that ratio. Each band includes
its lower bound.

- `BAND_A` and up starts at A.
- `BAND_B` and up starts at B.
- `BAND_C` and up starts at C.
- `BAND_D` and up starts at D.
- Below `BAND_D` starts at F.

When a side gives no trade value and gets some, it starts at A. When both sides are at zero, both
start at C.

## Consolidation

Two good players must not beat one great player on a plain sum. When one side gives exactly one
player and gets two or more, divide the depth side's sum by `CONSOLIDATION_MARGIN`. The depth side
is the side that gives two or more. Both sides use the divided sum in their ratios. A trade of
three for two, or of any two or more for two or more, gets no discount.

## Unlisted

A traded player with no row on the chart week's chart is unlisted. He has no trade value. When any
player in the trade is unlisted, neither side gets a start letter from trade value. Both sides
start at C, and the breakdown names the unlisted player. When the week has no chart at all, both
sides start at C too.

A handcuff is the exception. A handcuff counts as zero in the sums, with a chart row or without
one. A handcuff with no chart row keeps the start letter. See the handcuff section.

## Adjusters

After the start letter, each adjuster moves a side by one step at most: up, down, or not at all.
The breakdown lists every adjuster in this order, with its step and a one-line reason: roster
fit, standing, trend and usage, injury, handcuff, schedule, and expected gap. Expected gap runs only
when its tunable is on. Schedule shows a lean in place of a step.

## Roster fit

Roster fit reads two things of the side's roster, before the trade and after it: the best lineup
and the holes.

The best lineup fills the league's roster slots with the players who have the most points per game
over the last `LINEUP_WEEKS` completed weeks. The fixed slots fill first. Then each flex slot takes
the player left with the most points per game who can play there. At equal points, the position
order breaks the tie: RB over WR, WR over TE, TE over QB, QB over K, K over DEF.

A player's position rank is his place at his position among every player with a stat line in the
known games, rostered or not. The order is the points per game he counts for in a best lineup.
RB24 is the 24th running back in the league. The line is the last position rank a starter can hold:
`LINE_RB_WR` at RB and WR, and `LINE_QB_TE` at QB and TE. A flex slot reads the line of its
player's own position. K and DEF have no line.

A hole is a starting slot that holds a player below the line, or holds no player. A K or DEF slot
is never a hole. A hole that exists before the trade too is not new. A hole can move to another
slot of the same kind, such as from one flex slot to the other. It is still not new.

A starter who misses a week with no cover is a hole too. The bye window is `BYE_WINDOW` weeks
from the trade week. A starter with his bye in the window needs a cover. So does a starter due
back after the trade week and inside the window. A cover is a bench player above the line at a
position the slot allows. Each bench player covers one slot only. A bench player with his bye in
the same week cannot cover. A starter due back after the window is a hole, whatever his rank.
With no schedules, no bye hole reads, and the reason says that the schedules are not available.

- A new hole with no lineup gain is one step down. The reason names the slot, the player, and his
  position rank. For a starter with no cover, it names the week of his bye or his return.
- A lineup loss of `FIT_THRESHOLD` or more is one step down. With a new hole too, the step is
  still one down, and the reason names the hole.
- A lineup gain of `FIT_THRESHOLD` or more is one step up. A gain that opens a new hole is no
  step, because the two cancel. The reason names the gain and the hole.
- The side that gets the single highest-value player in the trade, with no lineup loss, gets one
  step up. A new hole blocks this step too, and the step is none. A lineup change smaller than `FIT_THRESHOLD` is no lineup loss. Trade
  value picks that player. When the week has no chart or a traded player is unlisted, points per
  game pick him.
- In a trade of one player for two or more, the side that gets two or more gets the step up only
  when every player it gets starts in its best lineup after the trade.

## Standing

A contender holds one of the `PLAYOFF_SPOTS` playoff spots by record. The standings rank by wins,
then by points for. A seller has more than `SELLER_GAP` wins fewer than the team in the last
playoff spot. Every other team is in the middle and gets no step.

- A contender gets one step up when its best lineup gains now. It also gets one step up when it
  gets a player due back by week `RETURN_BY_WEEK`.
- A contender gets one step down when its best lineup loses now and it gets a player who is due
  back after week `RETURN_BY_WEEK` or not at all.
- A seller gets one step up when it gets the highest-value player in the trade.
- A seller gets one step down when it gives that player for a lineup gain now.

A return week comes from the returns file, `data/<season>/returns.json`, which the commissioner
keeps. It holds the week each injured or suspended player returns. A player with a status of Out, IR,
or one of the suspension and PUP statuses, and with no row in the file, counts as not back by
week `RETURN_BY_WEEK`.

## Trend and usage

Compare each player's snap share and target share over the last `SHARE_WEEKS` scored weeks with
the `SHARE_WEEKS` scored weeks before them. A share that moves by enough points is up or down.
Every other share is flat. A player with too few weeks of data counts as flat.

- The players the side gets are up and the players it gives are down: one step up.
- The players the side gets are down and the players it gives are up: one step down.
- Shares that point both ways are mixed: no step. A player with one share up and one share down
  makes the trade mixed.
- When every share is flat and the players include a WR or TE, his WOPR direction over the same
  window decides first. A WOPR that moves by `WOPR_SWING` or more is up or down, and the steps
  follow the share rules above. It falls through when a window week has no WOPR or the WOPR
  points both ways.
- When every share is flat, red-zone use decides. Red-zone use is the red-zone targets and
  rushes over the season. More red-zone use in the players the side gets is one step up. More in the
  players it gives is one step down. Equal use is no step.

A handcuff on either side is left out of the comparison, and the reason says so. A player whose
return week on file is later than the last completed week is out now, so he has no use to
compare. He is left out on both sides too, and the reason says that he is due back.

## Injury

A player the side gets is an injury risk in two cases:

- He is out now, and he has no return week on file, or his return week is later than the trade
  week plus `RETURN_WINDOW_WEEKS`.
- He was on the injury report in `INJURY_WEEKS` or more weeks this season. Only the weeks
  before the trade count.

Out means a status of Out, IR, or one of the suspension and PUP statuses. This is the same set
that the standing adjuster uses.

Two or more such players are still one step down. The adjuster never fires for a player the
standing adjuster credits as a return bet. When the injury report is not available, only the
first case runs, and the reason says so. A player with no entry in the id map gets no count of
report weeks, and the reason names him.

## Handcuff

A handcuff is a running back the side gets who is second or lower on his NFL team's depth chart,
when the first on that chart is on the side's roster after the trade. He is insurance for the
team's own starter.

A backup who takes 25 percent or more of his team's carries over his last 3 games counts as a
running back, not a handcuff. The count reads his carries from the Sleeper stat lines, and the
known games count. Every adjuster grades him as any running back, and the handcuff reason names
his share. With fewer than 2 played games, or with no carry data, the depth chart alone decides.

- He counts as zero in the start letter sums.
- Roster fit does not step down for a lineup loss when the side gets a handcuff. The block covers
  a lineup loss only. A new hole still steps down.
- Trend and usage leaves a handcuff on either side out of the comparison.

The handcuff adjuster itself gives no step. It names the handcuff. When the depth chart or the id
map is not available, no player is a handcuff, and the reason names the missing source. A running
back with no entry in the id map gets no handcuff check, and the reason names him.

## Schedule

Schedule never moves a letter. It shows a lean for the side: for, against, or even. The verdict
rule reads the lean of the side that asked. It reads two signals for the players the side gets
against the players it gives. The trade week is N.

- Byes. A player's bye is left when his NFL team's bye week is N or later. Otherwise it is done.
  Fewer byes left in the players the side gets leans for. More leans against. An equal count is
  even.
- Playoff opponents. For each player, find his NFL team's opponents in weeks 15 to 17. Find the
  rank of each opponent in points allowed to his position. Rank 1 allows the most points, so a low
  rank is a soft opponent. Take the mean rank for each player, then the mean over the players on
  each side. A mean for the players it gets lower by `SCHEDULE_RANK_GAP` or more leans for. Higher
  by `SCHEDULE_RANK_GAP` or more leans against. Anything closer is even.

Two signals that agree give that lean. One signal with the other even gives that lean too. Two
signals that conflict give even. A player with no schedule, a defense, or a position with no
points allowed rank counts on neither side. When the schedules or the points allowed are not
available, the lean is even, and the reason says so.

## Final letter

Add the steps of all the adjusters. Clamp the sum to `CLAMP_STEPS` either way. Move the start
letter by the clamped sum: up toward A, down toward F. The letter stops at A and at F. The
breakdown shows the start letter, each adjuster, and the final letter.

## Verdict

The verdict is for the side that asked: accept, counter, or decline, with one reason. It reads the
final letter of each side.

- The asker's letter is `ACCEPT_AT_OR_ABOVE` or better: accept.
- The asker's letter is `DECLINE_AT_OR_BELOW` or worse: decline.
- A letter between the two: accept when the other side's letter is no better than the asker's.
  Counter when the other side's letter is better.

Schedule turns only a letter between the two bands. A schedule for the asker turns a counter into
an accept. A schedule against the asker turns that accept into a counter. Schedule never turns an
accept at `ACCEPT_AT_OR_ABOVE` or better, and never turns a decline.

## Fairness

The fairness is for both sides, not only the side that asked. It reads the final letter of each
side and gives one of three states.

- Both letters are `WIN_WIN_AT_OR_ABOVE` or better: win-win, good for both.
- Either letter is `LOPSIDED_AT_OR_BELOW` or worse: lopsided. The side with the lower letter gives
  more. At equal letters, the side with the lower start letter gives more.
- Any other pair of letters: fair.

Each side gets one reason: the reason of its first adjuster with a step up, in rubric order. A
side with no step up gets the reason of its start letter.

## What the breakdown never holds

The breakdown and every text made from it hold no trade value, no sum, no ratio, no chart name,
and no lineup total. They hold the letter, the adjuster steps, and plain reasons only.
