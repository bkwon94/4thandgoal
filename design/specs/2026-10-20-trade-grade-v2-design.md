# Trade grade v2: design

Date: 2026-10-20, late night
Status: draft, waits for Brian's approval
Amends: the Trades chapter in `design/specs/2026-10-20-history-trades-drops-design.md`

## Intent

Brian reviewed the week 6 rebuild on the branch `history-trades-drops`. His words: "trade grader is
pretty terrible. It seems to use the scores from that week to give it a grade. That doesn't make
any sense." The grade must be a snapshot at the moment of the trade. It weighs each player's value
up to that point in the season, the trends in his usage, the roster construction of each team, and
each team's position in the standings. How the players scored in the week of the trade is a
separate story on the page, never an input to the grade.

Brian also asked for one blurb per trade, not one blurb for every trade, and for each trade card to
expand and close like a matchup recap.

This design replaces the Trades chapter's facts, writer rules, chapter shape, and card. The trade
model, the window, the late-trade rule, and the swing stay.

## Goals

1. Grade each side of each trade from facts that end the week before the trade.
2. Give the writer the usage trends Brian named: snap share, target share, red-zone use.
3. Give the writer each team's standing, record, and roster depth as of the week before the trade.
4. Write one blurb per trade, three to five sentences, with the grade reason for both sides.
5. Show each trade as a card that opens and closes, with the grades visible when closed.

## Non-goals

- No route share. It is paid data, not in Sleeper, nflverse, or ESPN.
- No ESPN source. Its public endpoints give nothing the grader needs beyond Sleeper and nflverse.
  Brian's ESPN idea is parked for the Live page or for news.
- No bye-week facts. Sleeper's players blob carries no bye week. A later item.
- No regrade of an older trade on a later page. Unchanged from part 2.
- No change to the publish rule. Brian publishes after this lands and after his review.

## Anti-goals

- A grade that reads from this week's points, the swing, or any fact dated after the trade.
- A number on the page that no fact holds. The citation rules hold for every new fact.
- A card that hides the grade until it opens. The letters show on the closed card.

## Constraints

- Same stack and same citation rules as part 2: `Nums` for every number, `_fact(...)`, fact IDs,
  the code check, the verifier, the template fallback, one vocabulary line per new term.
- Writer rules 15 to 17 hold: at most two numbers per sentence, digits only.
- The grade stays Claude's opinion. The spec from part 2 says so, and the note on the page says so.
- Every chapter holds at 390px with no horizontal scroll.
- The branch `history-trades-drops` is the base. The work lands there before any merge.

## Data

Every input comes from Sleeper and nflverse data already on disk. "Before the trade" means weeks 1
to N-1, with N the week whose page carries the trade, for every trade in the window, late or not.

| Input | Source | Note |
| --- | --- | --- |
| Points per week, weeks 1 to N-1 | history `matchups.json` `players_points`, else `stats.json` `pts_half_ppr` | `player_points` exists |
| Projection per week | history `projections.json` | `player_trend` exists |
| Snap share per week | `stats.json` `off_snp` over `tm_off_snp` | both in the Sleeper stats |
| Target share per week | `stats.json` `rec_tgt` over the sum of `rec_tgt` of every player on the same NFL team in that week's stats | the stats file covers QB, RB, WR, TE, K, DEF; that is close enough, and the vocabulary line says so |
| Red-zone use per week | `stats.json` `rec_rz_tgt` and `rush_rz_att` | |
| Position rank by season points | `stats.json` `pts_half_ppr` summed over weeks 1 to N-1, ranked among every player at the position in those files | |
| Injury history and pre-game status | nflverse injuries, part 4 | `I.` facts exist |
| Team record, standing, points for | `season_records(history, N-1)` | exists |
| Roster depth and open spots | this week's `matchups.json` roster, part 2 `need` | exists; a late trade still gets no `need` |

A player with fewer than 3 scored weeks before the trade gets the facts his weeks allow. A fact
that needs a window the data cannot fill is absent, never wrong.

## Facts

The `T{n}.{rid}.got.{pid}` and `.gave.{pid}` facts lose their "this week" clause and the swing
reference. They become the pre-trade profile. Each new fact ID below is per trade and per player, so
the chapter of trade `n` holds only its own players.

| ID | Text pattern | Term |
| --- | --- | --- |
| `T{n}.{rid}.got.{pid}` | `{team} got {name}: {ppg} points per game over {g} games before the trade, position rank {r} of {of} by season points.` then the trend sentence from part 1 computed through week N-1, with the same text | **points per game**: half-PPR points over the weeks with a scored game, weeks 1 to N-1 |
| `T{n}.{rid}.gave.{pid}` | same shape with `gave` | **position rank by season points**: among every player at the position in Sleeper's weekly stats, weeks 1 to N-1 |
| `T{n}.{pid}.usage` | `{name}'s snap share was {s} percent over the last 2 weeks before the trade, {up/down/flat} from the 2 weeks before that.` | **snap share**: offensive snaps over the team's offensive snaps |
| `T{n}.{pid}.targets` | `{name}'s target share was {t} percent over the last 2 weeks before the trade, {up/down/flat} from the 2 weeks before that.` only for RB, WR, TE | **target share**: targets over the targets of every player on his NFL team in Sleeper's stats |
| `T{n}.{pid}.redzone` | `{name} had {a} red-zone targets and {b} red-zone carries this season before the trade.` | **red-zone use**: targets and carries inside the 20 |
| `T{n}.{pid}.injury` | `{name} was listed {status} on the NFL injury report in week {N-1}, and in {n} weeks this season before the trade.` when listed in N-1; else `{name} was on the NFL injury report in {n} weeks this season before the trade.` when n > 0; else no fact | **injury before the trade**: the nflverse report through week N-1. The week N pre-game report is after the trade and never feeds the grade |
| `T{n}.{rid}.team` | `{team} was {w}-{l}, {rank} of 12, before the trade.` from `season_records(history, N-1)` | |
| `T{n}.{rid}.need` | the part 2 text with its record clause removed: `{team} has {n} {POS} and {n} {POS} after the trade and {k} open roster spot(s).` The depth is the roster at lineup lock, after the trade, as part 2 ruled | |
| `T{n}.{rid}.impact.{pid}` | `{name} scored {pts} this week for {team}.` one per player in the trade, with the team that started him | **trade impact**: what the traded players scored in the week of the trade. It never feeds the grade |
| `T{n}.{rid}.swing` | unchanged from the final-review fix: starters only, follows the result | |

"Up" and "down" mean a change of 5 percentage points or more. Else "flat". The share is over the last
2 scored weeks before the trade, against the 2 scored weeks before those. A player with fewer than 4
scored weeks gets the share over the weeks he has, with no direction clause. The percent is an
integer. Fact text and vocabulary say "last 2 weeks". The one record in a trade chapter is the
`team` fact: the `need` fact carries no record, and the `S.` facts stay out of trade chapters.

## Chapters

The single `trades` chapter goes away. Each trade gets a chapter `trade_{n}`, title
`{A} and {B}` (or `{A}, {B} and {C}`), with facts: every `T{n}.` fact and nothing else. No `H.`,
`P.`, `S.`, or `I.` fact joins a trade chapter, because each of those carries week N data. The scope
is the trade rosters. Sentence range 3 to 5. `grade_keys` holds the `T{n}.{rid}` of that trade only.

One writer call per trade. Six calls for week 6. The verifier and the fallback work per chapter.
The template fallback for `trade_{n}` is the `T{n}.sides` sentence, no grades.

## Writer rules

Rule 18 is replaced:

```
18. In a trade chapter, grade each side on value at the moment of the trade, from the fact sheet
only: points per game and position rank before the trade, the trend, snap share, target share,
red-zone use, the injury report before the trade, the team's record and standing before the trade,
and its roster need. A team near the
bottom of the standings earns credit for a move. A team near the top earns credit for an upside bet
such as a player back from injury or suspension. Never let `impact` or `swing` facts move a grade.
Give an honest grade: one letter, A, B, C, D, or F. A trade can be a C for both sides. Put each
grade in `grades` under a key from the "Grade keys" line. Give the reason in the sentences.
```

Rule 19 is replaced:

```
19. In a trade chapter, write the grade reasons first. Then at most one sentence on how the trade
played out this week, from the `impact` or `swing` facts.
```

Rule 20 stays. The verifier rule on grades stays.

## The page

The Trades chapter keeps its label and its note. Each card keeps its two team rows with the grade
letter beside each team name, visible when the card is closed. Beside each player the card shows
his points per game before the trade, from the `got` fact, with a small `ppg` label. This week's
points are not on the card; the blurb's last sentence covers them. Under the rows, a full-width button
in the style of the recap button reads `Read the grade` and `Hide the grade` when open. The panel
holds the blurb for that trade, with the same slide as the recap panel. A card with a template
fallback or no blurb shows `No grade` in gray on both rows and the panel holds the template
sentence.

## Week 6

After this lands: `cornerstone build --week 6 --season 2026` rebuilds every chapter, Brian
reviews, Brian publishes. The new build lands as a new commit on top. No rewrite of history.

## Left to the builder

- The exact shape of the usage helpers and where they live; `history.py` holds the player helpers today.
- Whether `T{n}.{pid}.usage`, `.targets`, and `.redzone` are one function or three.
- The card and button markup, within the existing tokens and the recap pattern.
- The split of the old `trade_facts` into profile, usage, team, impact.
- The history fixtures hold `stats.json` with `off_snp`, `tm_off_snp`, `rec_tgt`, `rec_rz_tgt`,
  `rush_rz_att`, `pts_half_ppr`, and `gp`. Checked on 2026-10-20; no recut needed. Golden in week 5:
  47 of 61 snaps, 7 targets, 3 red-zone targets, 17.3 points.
