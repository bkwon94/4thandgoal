# History, trades, and drops: design

Date: 2026-10-20
Status: draft, waits for Brian's approval
Builds on: `design/specs/2026-10-20-cornerstone-weekly-design.md` (version 1, published for week 6)

## Intent

Version 1 reads one week of Sleeper data and writes the page from it. Brian's review of the
week 6 page asked for three things. First, blurbs that know what plays could have changed a
result, such as a receiver's drops in a close loss. Second, a chapter for the trades of the
week with an honest grade. Third, context from the season so far: streaks, trends, injury
history, and player form. Brian's words: "that historical context is key for good reports."

This design adds a history layer from weeks 1 to 5, a trades chapter, and a play-level data
source. Week 6 gets a rebuild and a republish with all three. Week 7 onward builds on them.

## Goals

1. Give every page from week 6 onward facts from the whole season: standings as of the week,
   streaks, 3-week trends for teams and players, season highs and lows, real schedule strength.
2. Add a Trades chapter with one card per completed trade and a grade per side.
3. Make a receiver's drops a citable fact, with an estimate of the points they cost, and let
   the writer say when the drops cost the game.
4. Make injury history a citable fact: weeks missed, a return this week, and the final
   pre-game report status.
5. Keep the Tuesday job to one command. Every new source degrades without a block.

## Non-goals

- No pages for weeks 1 to 5. Brian decided this. The weeks feed facts only.
- No Live page. That is a later project.
- No regrade of an old trade on a later page. The grade is for the week of the trade. A
  follow-up fact on a trade's anniversary is a later item.
- No playoff odds. No draft or auction recap.
- No change to the publish rule. Nothing publishes without `cornerstone publish`.

## Anti-goals

- A number on the page that no fact holds. Every number still binds to a cited fact.
- A drop estimate presented as a measured number. The method is on the page.
- A grade that reads as a computed score. The grade is Claude's opinion from a fact sheet, and
  the page says so.
- A claim about a player's status at kickoff that comes from the post-game Sleeper blob. Only
  the nflverse final pre-game report may ground a pre-game claim.
- A Tuesday build that fails because nflverse or ffverse is down.

## Constraints

- Same league, same stack: Python, `uv`, Pydantic, Jinja2, `httpx`, the Anthropic SDK, static
  site on GitHub Pages. Half PPR: `rec` 0.5, `rec_yd` 0.1, `rec_td` 6. Read the rates from
  `league.json` `scoring_settings`, never hard-code them.
- The citation rules from version 1 hold for every new fact: `Nums` for every number, a fact
  ID per fact, per-sentence citations, the code check, the verifier, the template fallback.
- A fact's text defines its terms. Each new stat gets one line in `vocabulary.md`.
- A history fact carries a streak or a trend as one number, to fit the two-number cap.
- The site, the chapters, and the mockup contract from version 1 stay. The Trades chapter is
  the one addition to the page. The standings highlight of Brian's team is gone as of `53d40c3`.
- House style for prose, comments, and docs is Simplified Technical English. Blurbs are exempt.

## Data sources

### Sleeper, per past week

The endpoints that take a week give any past week. Verified in version 1.

- `GET /league/{id}/matchups/{week}`: scores, starters, players points.
- `GET /league/{id}/transactions/{week}`: adds, drops, trades, with both roster ids.
- `GET /stats/nfl/{season}/{week}` and `/projections/nfl/{season}/{week}` (unofficial): per
  player stats and projections. The stats carry `rec_drop`, `rec_tgt`, `rec_rz_tgt`.

`rosters.json`, `users.json`, and the players blob are current-only. Standings as of a past
week must come from the matchups of weeks 1 to N, never from `rosters.json`.

### nflverse, per season

Public files on GitHub releases, no key. Each file holds every week of the season to date.
Checked on 2026-10-20: all three have weeks 1 to 6, and the week 6 rows landed Tuesday
morning before the 8:00 job.

| File | URL | Use |
| --- | --- | --- |
| Play-by-play | `https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz` | the receiver, `air_yards`, `yardline_100`, the play text |
| FTN charting | `https://github.com/nflverse/nflverse-data/releases/download/ftn_charting/ftn_charting_2026.csv` | `is_drop`, `is_catchable_ball`, joined to a play by `nflverse_game_id` and `nflverse_play_id` |
| Injuries | `https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2026.csv.gz` | `report_status` and `practice_status` per player per week, keyed by `gsis_id` |

The join from FTN to play-by-play is complete: 54 of 54 week 6 drops matched.

### ffverse id map

`https://github.com/dynastyprocess/data/raw/master/files/db_playerids.csv` maps `sleeper_id`
to `gsis_id`. Sleeper's players blob has no `gsis_id` for many players, Matthew Golden among
them, so this file is the bridge. Cache it with the players blob, one day.

### Degrade rules

- nflverse play-by-play or FTN down: drop facts use the Sleeper `rec_drop` count only, with no
  value estimate and no drop swing. The drop note on the page says "count only this week".
- nflverse injuries down: no injury history facts. The `.inj.` facts from version 1 stay.
- ffverse down: use the cached copy. With no cache, skip the nflverse facts for players with no
  `gsis_id` in the Sleeper blob.
- Sleeper past-week fetch down: the history layer uses the cached weeks it has. A missing week
  makes every `H.` and `P.` fact absent, never wrong. The standings, the upset ranks, the
  Matchup of the Week pick, and Must Watch then fall back to `rosters.json`, as in version 1,
  with a warning in the log. The page never loses a chapter over missing history. My call.
- The build logs each degrade. `verify.json` records which sources the build had.

## Part 1: the history layer

### Fetch and cache

- A new command, `cornerstone history --season 2026 --through 5`, fetches matchups,
  transactions, stats, and projections for each week from 1 to `through`. It writes them under
  `data/2026/history/week-0N/`. It skips a week that is on disk. Re-run with `--force` to refetch.
- `cornerstone build` reads the history from disk. It never fetches history itself. If history
  for weeks 1 to N-1 is absent, the build warns and runs with what it has.
- From week 7 on, the Tuesday job's `build` copies its own week's raw files into
  `data/2026/history/week-0N/` after a good build, so the history grows with no extra step.
  Builder's call whether this is a copy or a path convention.
- Each build saves the players blob's `injury_status` per player into the week's history
  directory. That is the per-week injury snapshot version 1 lacked.

### Model

`SeasonHistory` in `models.py` and `season_history()` in `facts_league.py` exist and cover one
week. Extend them. The builder owns the shape. The facts below are the contract.

### Facts

All facts are "as of this week". A trend window is the last 3 scored weeks including this one.

| ID | Text pattern | Vocabulary term |
| --- | --- | --- |
| `S.{rank}` | unchanged, but wins, losses, and points come from the history, not `rosters.json` | |
| `H.{rid}.streak` | "{team} has won {n} straight" or "has lost {n} straight", one number | **streak**: head-to-head results only, the median game excluded |
| `H.{rid}.trend` | "{team} has scored {avg} per week over the last 3 weeks, {up/down} from a season average of {avg}" | **team trend**: the last 3 weeks against the season average |
| `H.{rid}.high` | "{team}'s {pts} this week is a season high" or "season low", only when true | **season high**, **season low**: restored from version 1 |
| `H.{rid}.avg` | "{team} averages {pts} per week this season" | **season average** |
| `M{mid}.upset` | unchanged pattern, but the ranks come from the real standings before this week | |
| `M{mid}.move.{pid}` | unchanged, but recent adds read `transactions/{week-1}` from the history | |
| `P.{pid}.trend` | "{name} has {beaten/missed} projection in {n} of the last 3 weeks" | **player trend**: against projection over the last 3 weeks |
| `SOS.{rid}` | unchanged pattern, but the strength comes from the real records of past opponents | |

`H.` facts attach to the recap and MOTW chapters of both teams, and to the standings and next
week chapters. `P.` facts attach to the chapter of the player's matchup and to the awards
chapter for the award winners. Builder's call on caps: no chapter should gain more than six
history facts, so the writer prompt stays under the version 1 size by more than a third.

### What a past week cannot have

- Injury status from Sleeper, because the blob is current-only. Injury history comes from
  nflverse in part 4.
- News from Sleeper's news endpoint. The build never calls it for a past week.

## Part 2: the Trades chapter

### The page

A chapter between the recaps and the awards. Light background. The label reads "Trades".
One card per completed trade of the week. A card has:

1. Both teams, with avatars, each side on its own row.
2. Under each team, the players and picks that side got, with each player's points this week.
3. A grade per side, A to F, as a large letter in red beside the team name.

Under the cards, one blurb of four to six sentences for the chapter. With more than two trades,
the blurb covers the two with the widest gap between the grades and names the rest in one
sentence. Builder's call on the exact markup. The card must hold at 390px with no horizontal
scroll, like every chapter.

A week with no trade has no Trades chapter. The chapter key is `trades`.

### Which trades belong to the week

My call, after the review. A trade belongs to the page of week N when its `created` time is
after the fetch of week N-1 and before the fetch of week N. Sleeper's `leg` is not the rule,
because a trade made on Tuesday after the 8:00 job carries `leg` N but never shows in
`transactions/{N+1}`. The build therefore reads `transactions/{N}` and `transactions/{N-1}`,
and keeps each trade's `created` time. The build records the fetch time of its transactions
in `verify.json`, and the next build uses that time as the cutoff. The fetch time, not the
build start, is the bound, so a trade made between the fetch and the build lands on the next
page and no trade misses both pages. For week 6 only, with no saved fetch time, the window
ends at the write time of `raw/transactions.json`, because version 1 saved no fetch time. The
build start is the last fallback. The history copy of a week's
transactions is taken at build time. A trade made after that build carries `leg` N-1 and is not
in the copy, so the build of week N refetches `transactions/{N-1}` into
`raw/transactions_prev.json` and reads the window from that file. Without the file, the build
reads the history copy and logs a warning.

A trade is late when a player it moved is on the roster that gave him in `matchups.json`.
The players it moved scored for their old teams that week. A late trade gets a card and a
grade, but no `swing` fact and no `need` fact. The week 6 file holds one such trade, rosters
7 and 8 on Tuesday 2026-10-20.

### Which players count in the swing

My call. The `swing` fact for a side counts only the players that side got and started this
week, against the players it gave that the other side started this week. A bench player did
not change a result. A player traded twice in one week counts in the trade that put him on
the roster he played for. One `swing` fact per side per trade, no net per team.

### Model

A new `Trade` model from `transactions.json` rows with `type == "trade"` and
`status == "complete"`: both `roster_ids`, the `adds` and `drops` maps, `draft_picks`, and the
`created` time. The `Move` model keeps its trade rows for the recent-add facts. The builder
decides whether `Trade` derives from `Move` or reads the raw row.

### Facts

| ID | Text pattern | Vocabulary term |
| --- | --- | --- |
| `T{n}.sides` | "{team A} traded {players and picks} to {team B} for {players and picks}" | |
| `T{n}.{rid}.got` | "{team} got {name}: {pts} this week, {season pts} this season, position rank {r} of {of}" one fact per player got | |
| `T{n}.{rid}.gave` | same shape for each player gave | |
| `T{n}.{rid}.need` | "{team} is {w}-{l}, {rank} of 12, with {n} players at {pos} after the trade and {n} open roster spots" | **roster need**: depth at the traded positions and open spots, as of this week's lineup |
| `T{n}.{rid}.swing` | "The players {team} got and started scored {x} this week; the players it gave that {other team} started scored {y}." Then, when the gap points the same way as the result and is at least the margin: "The gap is {z}, {above/equal to} the margin of {m} in its matchup." Otherwise: "In its matchup, that is a gap of {z} against a margin of {m}, not enough to change the result." With more than one other roster, "{other team}" is "its trade partners" | **trade swing**: starters only. The gap counts only when it points the same way as the result: the winner gained at least the margin, or the loser gave away at least the margin. Only then may the writer say the trade decided or cost the game |
| `T{n}.{rid}.grade` | none. The grade is not a fact. See below | **trade grade**: an opinion from the fact sheet, A to F, with the reason |

The `need` fact reads the week's roster from `matchups.json` `players`, which is the roster at
lineup lock, after the trade. Open spots are the slot count minus the players on that list.
The slot count is the length of `league.json` `roster_positions` plus `settings.reserve_slots`,
because the `players` list holds the injured reserve player. The fact never claims a "before the trade" roster, because
`rosters.json` is current-only and an undo of later moves is not worth the risk. My call.

Each `got` and `gave` fact also carries the player's 3-week trend and injury status when the
history and part 4 give them. Picks appear as text in `sides` only. Sleeper gives no value for
a pick. The writer may not put a number on a pick.

### The grade

The writer returns the grade per side as a structured field next to the blurb, not inside the
prose. The `Blurb` model gains an optional `grades: dict[str, str]` keyed by `T{n}.{rid}` for
the `trades` chapter only. The key names the trade too, because one roster can make several
trades in a week. The renderer puts the letter on the card. The prose gives the reason.

The code check for this chapter requires `grades` to hold one `T{n}.{rid}` key per roster in
every trade of the week, each a single letter A to F. A miss fails the attempt like any code check
failure. On the template fallback, the cards render with "No grade" in gray where the letter
goes, and the template blurb lists the sides of each trade. The chapter never drops over a
failed blurb. My call.

The writer prompt for this chapter adds one rule: grade each side on value, from the fact sheet
only, with weight on this season's points, the trend, the roster need, and the injury status.
An honest grade. A trade can be a C for both sides. The verifier treats the grade as an
opinion under the rule that an opinion makes no factual claim. Every number in the reason
still cites a fact.

## Part 3 and 4: drops, play-level data, and injury history

### Facts

| ID | Text pattern | Vocabulary term |
| --- | --- | --- |
| `D.{pid}` | "{name} dropped {n} of {t} targets this week" | **drop**: a pass the FTN charting flags as a drop. With nflverse down, the count is Sleeper's `rec_drop` |
| `D.{pid}.value` | "{name}'s drops were worth about {pts} points by the drop value method, with {n} in the end zone" | **drop value**: an estimate. One reception at the league rate, plus the air yards at the per-yard rate, plus a touchdown when the throw reached the end zone |
| `M{mid}.dropswing` | "{team}'s starters dropped {n} passes worth about {pts}, at least the margin of {m}" only when true, for the losing side | **drop swing**: the losing side's drop value is at least the margin. Only then may the writer say the drops cost the game |
| `W.drops` | "Most drops this week: {name} ({team}), {n}; ..." top three league-wide | |
| `I.{pid}.history` | "{name} was on the NFL injury report in {n} earlier weeks this season and plays this week", one number | **injury history**: the weekly NFL report status from nflverse, per week |
| `I.{pid}.pregame` | "{name} was listed {status} on the final NFL injury report before his game this week" | **pre-game status**: the final NFL report before the game, from nflverse. A roast of a manager who started a player listed Out or Doubtful before the game cites this fact |

"Reached the end zone" means `air_yards >= yardline_100` on the play. A throw that landed
short, such as Golden's at the 4, counts as the air yards only. No touchdown is assumed.

The `D.` and `I.` facts attach to the chapter of the player's matchup, to the awards chapter
for award winners, and to the Game Changer chapter for that player.

### The page

- The awards chapter gains one tile, "Butterfingers", for the most drops among started
  Cornerstone players, with the count and the drop value. `W.drops` has the same scope. A
  player not on a Cornerstone roster never appears. Butterfingers is last in the pick order,
  after Overachiever, under the version 1 rule that one player holds one award. Five tiles
  instead of four. Builder's call on the tile layout at 390px. My call on the scope.
- A note under the All Matchups chapter states the drop value method in one sentence, in the
  style of the median note under the standings. With nflverse down, the note says the count
  is from Sleeper and no value was estimated.

### Writer and verifier rules

- Writer rule 11 keeps its ban on jokes about an injury itself. The `I.{pid}.pregame` fact
  lifts the ban on "started a player listed Out", for the pre-game status only. The `.inj.`
  facts stay post-game and keep the version 1 wording.
- The nflverse injuries file is the final game-status report, one row per player per week with
  no date. It is not a Friday report for a Thursday or Monday game, so no fact says "Friday".
  About half its rows have no `report_status`; those players get no `pregame` fact. Players on
  injured reserve are not in the file; the `history` fact covers them only through the weeks
  they were listed before the move. My call.
- A new vocabulary line for each term above. The verifier sees them through `vocabulary.md`.
- A drop fact names the receiver only. The writer may not blame the quarterback for a drop.
- The verifier gate that lets the writer say "cost the game" today keys on `.driver` and
  `.swing` fact IDs. The `dropswing` and the trade `swing` facts must pass that gate too. The
  builder extends the gate to those IDs rather than rename the facts. A trade `swing` fact opens
  the gate only when its text says the gap is above or equal to the margin.

## Week 6 rebuild and republish

After all four parts land: run `cornerstone history --through 5`, then `cornerstone build
--week 6 --season 2026`, then Brian reviews the page, then Brian publishes. The week 6 data
directory keeps its `raw/`. The facts and blurbs are rebuilt. The published page replaces the
one from 2026-10-20.

## Order of work

1. Part 1, the history layer. Everything else cites it.
2. Part 2, the Trades chapter. The grade needs the history.
3. Part 3 and 4 together, the nflverse fetch, the drop facts, and the injury history.
4. The week 6 rebuild, Brian's review, the republish.

Each part ends with the full test suite green, a review, and a commit. A build of week 6 from
disk after each part is the smoke test.

## Left to the builder

- The exact shape of `SeasonHistory`, `Trade`, and the new fact functions.
- Whether the history command copies or symlinks the current week into the history directory.
- The parse of the nflverse CSV files: the standard library `csv` module is enough. No pandas.
- The cache policy for the nflverse files, with a one-day cache as the default.
- The Trades card markup and the five-tile awards layout.
- Test fixtures: one trimmed week of each nflverse file under `tests/fixtures/`, cut to the
  plays and players the tests need.
- The cap on history facts per chapter, within the limit above.
