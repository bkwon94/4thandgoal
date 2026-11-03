# 06 notes: the ESPN API and the Yahoo API

Research for `06-research-the-espn-and-yahoo-apis.md`. Read on 2026-11-03. Brian makes the decision.

ESPN has no official public API and no public docs. The ESPN facts below come from the source of `cwendt94/espn-api`, a maintained client. ESPN can change the shape at any time. Abbreviations: `EA` is `https://github.com/cwendt94/espn-api/blob/master/espn_api/`. `YD` is `https://sports.yahoo.com/developer/docs/`. `YF` is `https://github.com/uberfastman/yfpy/blob/main/yfpy/`.

## Auth

ESPN, unofficial:
- The host is `https://lm-api-reads.fantasy.espn.com/apis/v3/games/`. Source: `EA` `requests/constant.py`.
- A public league needs no auth. A private league needs the two browser cookies `espn_s2` and `SWID`. On a 401 with no cookies, the client raises `ESPNAccessDenied("espn_s2 and swid are required")`. Source: `EA` `requests/espn_requests.py`, lines 55 to 86.
- No login API exists. The client keeps a login function in comments only. So a person copies the cookies from a logged-in browser. Source: same file, lines 289 to 316.

Yahoo, official:
- OAuth 2.0: "The Yahoo Fantasy Sports API uses OAuth 2.0 to authorize access to fantasy data." Source: https://sports.yahoo.com/developer
- The landing page now asks for an application with a review. The docs page still names the app flow at https://developer.yahoo.com/apps/create/ with "Fantasy Sports" read access. So one person must register an app and do one authorization-code login. Sources: https://sports.yahoo.com/developer and `YD` "Register your application".
- Each call carries a user token, and the user must see the league. A public league on Yahoo still needs a token.
- The old URL `developer.yahoo.com/fantasysports/guide/` now redirects to `sports.yahoo.com/developer`.

## The data each gives

| Need | ESPN (unofficial) | Yahoo (official) |
| --- | --- | --- |
| League settings | `view=mSettings`: `rosterSettings.lineupSlotCounts`, `scoringSettings.scoringItems` by numeric `statId`. `EA` `football/settings.py` | `/league/{key}/settings`: `roster_positions`, `stat_categories`, `stat_modifiers` by numeric `stat_id`, `uses_faab`. `YD` "League resource" |
| Teams and owners | `view=mTeam`: id, name, record, `pointsFor`, `logo`, `waiverRank`, `transactionCounter.acquisitionBudgetSpent`. `EA` `football/team.py` | `/league/{key}/teams`: `team_key`, managers, `waiver_priority`, `faab_balance`, `team_logos`. `YF` `models.py` lines 506 to 623 |
| Rosters per week | `view=mRoster&scoringPeriodId=N`, with a lineup slot per entry. `EA` `football/league.py` line 113 | `/team/{key}/roster;week=N`, with `selected_position` per player. `YD` "Roster resource" |
| Matchups and scores | `view=mMatchupScore` and `mScoreboard`, per player points in `appliedTotal`. `EA` `football/league.py` lines 312 to 360 | `/league/{key}/scoreboard;week=N`: team points and `team_projected_points`. Player points need `/players/stats;type=week;week=N` per team. `YD` |
| Transactions | `view=mTransactions2&scoringPeriodId=N`, types `FREEAGENT`, `WAIVER`, `WAIVER_ERROR`, `TRADE_ACCEPT` and more, with `bidAmount`, `status`, `items`. `EA` `football/league.py` lines 508 to 555, `football/transaction.py` | `/league/{key}/transactions`: types add, drop, add/drop, trade, commish. `faab_bid`, `status` ("successful"), `timestamp` in seconds, `picks`. `YD` "Transaction resource", `YF` `models.py` lines 672 to 699 |
| Waiver claims with FAAB bids | Yes, `bidAmount`. `get_league_offers` reads `WAIVER` and `WAIVER_ERROR`. `EA` `requests/espn_requests.py` line 194 | `faab_bid` on a done claim. |
| Failed claims | Yes, `WAIVER_ERROR` rows. | No. The docs show no failed status. Pending claims show only per team with `team_key`: "Pending transactions will not show up if you simply ask for all of the transactions in the league." `YD` |
| Trades | Caveat: "TRADE_ACCEPT rows from mTransactions2 often have empty items except for the authenticated owner's deals." The client fills them from player cards. `EA` `football/league.py` line 518 | Yes, with trader and tradee team keys and `picks`. |
| Players | `view=players_wl` and `kona_player_info`: numeric `id`, `proTeamId`, `defaultPositionId`, `injuryStatus`, `ownership.percentOwned`. `EA` `football/player.py` | `/game/nfl/players`: `player_key` `{game}.p.{id}`, `editorial_team_abbr`, `display_position`, `headshot`, `percent_owned`. `YD` "Player resource" |
| Projections | Yes. A stat row with `statSourceId` 1 holds the projection, in league scoring, with a stat breakdown. `EA` `football/player.py` lines 66 to 100 | No player projections in the docs. Only `team_projected_points`. A scraper project uses Selenium for projections. https://github.com/andrewrgoss/yahoo-fantasy-fball-scraper |
| Past seasons | The same league id each year, with `seasons/{year}`. Before 2018: `leagueHistory/{id}?seasonId={year}`. `EA` `requests/espn_requests.py` lines 44 to 53 | A new `league_key` each season, because the game id changes each year (`461` is NFL 2025). `renew` and `renewed` link the seasons, such as `"371_52364"`. `YD` "Game resource", `YF` `query.py` line 1124 |

## Rate limits and terms

- ESPN: no documented limit and no developer terms. Use is at ESPN's discretion, and a change can break the adapter without notice.
- Yahoo: no number. Yahoo "may temporarily throttle or limit access" on excessive use. The terms allow one developer account, forbid separation of the data, and require the line "Fantasy data provided by Yahoo Fantasy" with the logo. Source: https://sports.yahoo.com/developer
- Yahoo throttle in practice: yfpy treats HTTP status 999 as the rate limit. Source: `YF` `query.py` lines 435 to 437.

## The fields the pipeline reads, and who can fill them

Fields that the pipeline does not read are left out: `RawBracketMatch.r` and `.m`, `RawUser.metadata.avatar` aside from the avatar URL. `bracket` is fetched and saved but no module reads it.

| `raw.py` field | Read by | ESPN | Yahoo |
| --- | --- | --- | --- |
| `RawState.season`, `display_week` | `parse.py` | Yes, `status.latestScoringPeriod` | Yes, game `current_week` |
| `RawState.season_start_date` | `parse.py`, `cli.py` | Derive from the pro schedule | Derive from `game_weeks` |
| `LeagueSettings.last_scored_leg` | `parse.py` | Derive | Derive from matchup status |
| `LeagueSettings.reserve_slots` | `parse.py` | Yes, IR slot count | Yes, `IR` in `roster_positions` |
| `LeagueSettings.waiver_budget` | `waiver_price.py` | Yes, in settings | Not found. `faab_balance` gives the budget left |
| `RawLeague.roster_positions` | `parse.py` | Map slot ids | Map position names |
| `RawLeague.scoring_settings` by Sleeper key (`rec`, `rec_yd`, `rec_td`, `pass_int`) | `facts_nflverse.py`, `nflverse_expected.py`, `pipeline.py` | Map numeric `statId` | Map numeric `stat_id` |
| `RawUser.user_id`, `display_name`, team name, avatar | `parse.py`, `waiver_*.py` | Yes, members and `logo` | Yes, managers and `team_logos` |
| `RosterSettings.fpts` + `fpts_decimal` | `parse.py` | Yes, as one float | Yes, as one float |
| `RosterSettings.wins`, `losses` | `parse.py` | Yes | Yes, in standings |
| `RosterSettings.waiver_budget_used` | `waiver_price.py` | Yes | Derive: budget minus `faab_balance` |
| `RosterSettings.waiver_position` | `waiver.py` | Yes, `waiverRank` | Yes, `waiver_priority` |
| `RawRoster.roster_id`, `owner_id`, `players` | many | Yes | Yes, team id from `team_key` |
| `RawMatchup.matchup_id` | `parse.py` | Synthesize from the home and away pair | Synthesize from the scoreboard |
| `RawMatchup.points`, `players`, `players_points` | `parse.py` | Yes | Yes, with one call per team |
| `RawMatchup.starters` as an ordered list with `"0"` for an empty slot | `parse.py` | Rebuild from the lineup slot ids | Rebuild from `selected_position` |
| `RawTransaction.type`, `status` (`complete`, `failed`) | `parse.py`, `waiver_price.py` | Map; `WAIVER_ERROR` gives failed | Map. **No failed claims** |
| `RawTransaction.leg` | `parse.py`, `waiver_price.py` | Yes, `scoringPeriodId` | **No week field.** Derive from `timestamp` |
| `RawTransaction.created` (ms) | `parse.py` | Yes | Yes, seconds times 1000 |
| `RawTransaction.adds`, `drops`, `roster_ids` | `parse.py`, `waiver_price.py` | Yes. Trade items can be empty | Yes |
| `TransactionSettings.waiver_bid` | `parse.py`, `waiver_price.py` | Yes, `bidAmount` | Yes, `faab_bid` |
| `RawTransaction.draft_picks` | `parse.py` | Not found | Yes, `picks` |
| `RawProjection.stats["pts_half_ppr"]`, `RawAheadWeek.projections` | `parse.py`, `waiver_projection.py` | Rescore the projected breakdown to half PPR | **No** |
| `RawStatLine.stats` by Sleeper key (`gp`, `tm_off_snp`, `pts_half_ppr`) | `parse.py`, `snapshot.py` | Numeric ids. `tm_off_snp` not found | Numeric ids. `tm_off_snp` not found |
| `RawStatLine.game_id`, `team`, `player.position` | `snapshot.py`, `parse.py` | `game_id` not found | `game_id` not found |
| `RawTrending.player_id`, `count` (adds across all Sleeper leagues) | `waiver.py` | **No.** Only `percentOwned` | **No.** Only `percent_owned` |
| `players` file: `full_name`, `position`, `team`, `injury_status`, `injury_body_part`, `gsis_id` | `parse.py`, `waiver_*.py`, `nflverse.py`, `snapshot.py` | Name, position, team, `injuryStatus`. Body part and `gsis_id` not found | Name, position, team. Injury body part and `gsis_id` not found |

Fields that one of them cannot fill: failed claims and `leg` on Yahoo; `draft_picks` on ESPN; all projections on Yahoo. Fields that neither fills in the Sleeper form: `trending.count`, the stat keys `gp` and `tm_off_snp`, `game_id`, `injury_body_part`, and the `gsis_id` of a player. Each of these is NFL data, not league data.

## The Sleeper shapes in the port

1. **One fetch for league data and NFL data.** `fetch_week` gets the league files and the NFL files in one call: `state`, `players`, `projections`, `stats`, `projections_ahead`, `trending`. These come from the public Sleeper NFL endpoints, with no league id and no auth. A port with no Sleeper shape splits them: a league provider and an NFL data source.
2. **Sleeper player ids everywhere.** Each key of `adds`, `drops`, `players`, `starters`, and `players_points` is a Sleeper id. `player_ids.py` tests a DEF by a non-digit id and builds a Sleeper CDN headshot URL. `nflverse.py` joins on the `sleeper_id` column of the id map. `ChartValues` keys by Sleeper id. A port with no Sleeper shape names one canonical player id and makes each provider map its ids to it.
3. **A players file of about 5 MB in the Sleeper form.** `RawWeek.players` is `dict[str, dict]` with Sleeper keys, and five modules read the keys. A port needs a typed player record, with a name, position, NFL team, injury status, and canonical id.
4. **Sleeper stat and scoring keys.** `scoring_settings`, `stats`, and projections use Sleeper names such as `rec_yd` and `pts_half_ppr`. A port needs one stat vocabulary that each adapter maps into.
5. **The Sleeper file layout of each model.** Examples: `fpts` plus `fpts_decimal`; `matchup_id` on each row in place of a pair; `starters` as an ordered list with `"0"` for an empty slot, matched to `roster_positions` by index; `users` apart from `rosters`; `type` and `status` strings of Sleeper; `created` in milliseconds; `waiver_budget` plus `waiver_budget_used` in place of the budget left. Each adapter can synthesize these, but the shape is Sleeper's.
6. **Transactions by week.** `fetch_week` calls `transactions/{week}`, and `leg` is on each move. Yahoo has no week filter and no week field.
7. **One league id per season.** `config.league_ids` holds `(season, id)` pairs, and each fetch takes a `league_id: str`. This fits all three. ESPN repeats the same id. Yahoo needs a `{game_id}.l.{league_id}` key per season. No change is needed.
8. **The raw shape leaks past `parse.py`.** The docstring says `parse.py` is "the only module that knows the shape of the raw data". But `waiver.py`, `waiver_price.py`, `waiver_drops.py`, `waiver_projection.py`, `snapshot.py`, `history.py`, `live.py`, and `pipeline.py` also read raw fields. `waiver_price.py` holds `CLAIM_RESULTS = {"complete": True, "failed": False}`, a Sleeper status map. `history.py` saves the raw files as Sleeper JSON and reads them back.

## Recommendation

Brian decides. This is a recommendation only.

1. **Keep `raw.py` as the Sleeper wire shape, and do not generalize it now.** A field-by-field neutral raw model is a large change with no second provider to test it. It would also break the empty golden diff of this spec.
2. **Name the split in the port now, with no code change to Sleeper's behavior.** Write in `provider/README.md` and `base.py` that the port has two roles: the league provider and the NFL data source. Sleeper fills both today. The NFL endpoints of Sleeper need no auth, so an ESPN or Yahoo client can keep Sleeper as its NFL data source. Then the fields that neither API fills stay filled.
3. **Make the Sleeper player id the canonical id, by decision.** Record it in an ADR. A later ESPN or Yahoo adapter then maps its ids to Sleeper ids with the id map that `nflverse.py` already reads. The dynastyprocess id map has ESPN and Yahoo id columns too, but that is not checked here.
4. **Correct the claim that `parse.py` is the only reader of the raw shape.** Either fix the docstring, or open a ticket that moves the raw reads of the waiver modules, `snapshot.py`, and `history.py` behind `parse.py`. Brian chooses which. The move is the real work a later provider spec needs.
5. **Leave for the later ESPN or Yahoo spec:** the map of stat and scoring keys, the synthesized `matchup_id` and `starters`, the derived Yahoo `leg`, and the Yahoo gap in failed claims and projections.

The answer to the ticket: yes, the port can take ESPN and Yahoo later, with no Sleeper shape in the port contract, if this spec names the two roles and the canonical id. ESPN is unofficial and can break. Yahoo needs a registered app, an OAuth login, and the attribution line.

## A second ESPN source

Brian gave `pseudo-r/Public-ESPN-API`. Source: https://github.com/pseudo-r/Public-ESPN-API

- It is unofficial. It says the APIs "are not officially supported and may change without notice."
- It gives the base URL `https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}`.
- It lists the views `mTeam`, `mRoster`, `mMatchup`, `mMatchupScore`, `mSettings`, `mDraftDetail`, `mScoreboard`, `mStandings`, `mStatus`, and `kona_player_info`.
- It agrees that a private league needs the cookies `espn_s2` and `SWID`.
- It does not cover the transactions, the waiver claims, the FAAB bids, the projections, or the history of past seasons. For those, `cwendt94/espn-api` stays the source.
- It says that "Public" means the endpoint is reachable. It does not mean permission to collect or reuse the data.
