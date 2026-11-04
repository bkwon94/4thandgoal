# 06 notes: the ESPN API and the Yahoo API

Ticket: .scratch/clients/decisions/06-research-the-espn-and-yahoo-apis.md

Research read on 2026-11-03. Brian makes the decision.

## Sources and labels

ESPN has no official public API and no public docs. Each ESPN fact here comes from client source code, so each one has the label **[lib]**. ESPN can change the shape at any time. Yahoo has official docs, so a Yahoo fact has the label **[vendor]** unless a library is the only source.

The links pin the commit that this research read:

- `EA` is `https://github.com/cwendt94/espn-api/blob/700e15ddbb91124f031473d2411c8a6285944274/espn_api/`.
- `YF` is `https://github.com/uberfastman/yfpy/blob/5287b2d68d33d0f03f24eea70c179ae27aedc99c/`.
- `FS` is `https://github.com/ffverse/ffscrapr/blob/b6990181e125507a1b4642cea6bc9778d9acd6f3/`.
- `YD` is `https://sports.yahoo.com/developer/docs/`, the Yahoo Fantasy Sports API docs.
- `YO` is `https://developer.yahoo.com/oauth2/guide/flows_authcode/`, the Yahoo OAuth 2.0 guide.

The old URL `https://developer.yahoo.com/fantasysports/guide/` now gives a 308 redirect to `https://sports.yahoo.com/developer`.

## Auth

### ESPN

- **[lib]** The host is `https://lm-api-reads.fantasy.espn.com/apis/v3/games/`, and NFL is the game code `ffl`. Source: `EA` `requests/constant.py#L1-L5`.
- **[lib]** A public league needs no auth. The client sends no cookies when it has none. Source: `EA` `base_league.py#L36-L45`.
- **[lib]** A private league needs the two browser cookies `espn_s2` and `SWID`. On a 401 with no cookies, the client raises `ESPNAccessDenied("espn_s2 and swid are required")`. Source: `EA` `requests/espn_requests.py#L55-L90`.
- **[lib]** No login API works. The login function stays in comments: "Username and password no longer works using their API without using google recaptcha". Source: `EA` `requests/espn_requests.py#L286-L318`.
- So a person copies the two cookies from a logged-in browser. A CI job keeps them as two secrets. No source gives the lifetime of `espn_s2`. Expect a person to copy fresh cookies when ESPN ends the session.
- **[lib]** ffscrapr reads the two cookies from environment variables in its example. Source: `FS` `R/espn_connect.R#L8-L21`.

### Yahoo

- **[vendor]** "The Yahoo Fantasy Sports API uses OAuth 2.0 to authorize access to fantasy data." Source: https://sports.yahoo.com/developer
- **[vendor]** Access now needs an application form. "Each application is reviewed by the Yahoo Fantasy Sports team." The form asks for the product, the data, and the user base, such as "personal or single-league use". Access "is read-only by default". Source: https://sports.yahoo.com/developer/access/
- **[vendor]** The app registration asks for "access to private user data" and "Read or Read/Write access for Fantasy Sports". It gives a consumer key and a consumer secret. Source: `YD`, section "Register Your Application".
- **[vendor]** The base URL is `https://fantasysports.yahooapis.com/fantasy/v2`. Source: `YD`.
- **[vendor]** The flow is the authorization code flow. A user opens `https://api.login.yahoo.com/oauth2/request_auth` once and gives consent. The app trades the code at `https://api.login.yahoo.com/oauth2/get_token`. Source: `YO`.
- **[vendor]** "If your application does not have access to a browser, you must specify the callback as oob". Source: `YO`.
- **[vendor]** "The access token has a 1-hour lifetime." Source: `YO`.
- **[vendor]** The refresh token has "a long lifetime", with no number. A refresh call is a POST to `get_token` with `grant_type=refresh_token` and an `Authorization: Basic` header of `client_id:client_secret`. Source: `YO`.
- **[vendor]** The refresh token can rotate: "the client must discard the old refresh token and replace it with the new refresh token". The user can also revoke it. Source: `YO`.
- **[vendor]** Each call carries a user token. A public Yahoo league still needs a token.

How a CI job keeps a valid Yahoo token, with no browser:

1. Brian does the consent once on his own machine, with the `oob` callback. **[vendor]** `YO`.
2. Brian stores the consumer key, the consumer secret, and the refresh token as GitHub Actions secrets.
3. Each run trades the refresh token for an access token of one hour. **[vendor]** `YO`.
4. If Yahoo sends back a new refresh token, the job must store it. Otherwise the next run fails. A GitHub Actions job cannot write its own secret with the default `GITHUB_TOKEN`. So the job needs a token with the right to write secrets, or another store. This step is our inference, not a vendor statement.
5. **[lib]** yfpy reads the whole token as one JSON in the environment variable `YAHOO_ACCESS_TOKEN_JSON`. The required fields are `access_token`, `consumer_key`, `consumer_secret`, `guid`, `refresh_token`, `token_time`, and `token_type`. Source: `YF` `README.md#L175-L222`.
6. **[lib]** yfpy refreshes the token when it is not valid, and does a fresh 401 auth. Source: `YF` `yfpy/query.py#L326-L331` and `yfpy/query.py#L439-L440`.

## Data

### What each API gives

| Need | ESPN **[lib]** | Yahoo **[vendor]** unless marked |
| --- | --- | --- |
| League settings | `view=mSettings`: `rosterSettings.lineupSlotCounts`, `scoringSettings.scoringItems` by numeric `statId`, `acquisitionSettings.acquisitionBudget`. `EA` `football/settings.py#L9-L22`, `base_settings.py#L34-L37` | `/league/{league_key}/settings`: roster positions, stat categories, and stat modifiers. `YD` "League Resource". **[lib]** `uses_faab`, `playoff_start_week`, `waiver_rule`. `YF` `yfpy/models.py#L1098-L1115` |
| Teams and owners | `view=mTeam`: `id`, `owners`, `record.overall`, `transactionCounter.acquisitionBudgetSpent`, `waiverRank`. `EA` `football/team.py#L9-L39` | `/league/{league_key}/teams`, with managers. **[lib]** `faab_balance`, `waiver_priority`. `YF` `yfpy/models.py#L575`, `#L623` |
| Rosters per week | `view=mRoster&scoringPeriodId=N`, with a lineup slot per entry. `EA` `football/league.py#L113-L115` | `/team/{team_key}/roster;week={week}`. `YD` "Team Resource" |
| Matchups and scores per week | `view=mMatchupScore,mScoreboard`, with a filter on the matchup period. Team score is `totalPoints`, or `totalPointsLive` during play. Each team has `rosterForCurrentScoringPeriod.entries`. `EA` `football/league.py#L338-L366`, `football/box_score.py#L78-L83` | `/league/{league_key}/scoreboard;week={week}`, with team points and `team_projected_points`. `/team/{team_key}/matchups;weeks=1,3,6`. `YD` "League Resource", "Team Resource" |
| Player points per week | `appliedTotal` of the stat row with `statSourceId` 0. `EA` `football/player.py#L66-L96` | `/player/{player_key}/stats;type=week;week={week}`. `YD` "Player Resource" |
| Transactions | `view=mTransactions2&scoringPeriodId=N`, with a type filter in the `x-fantasy-filter` header. Fields: `id`, `teamId`, `type`, `status`, `scoringPeriodId`, `processDate`, `bidAmount`, `items` with `fromTeamId` and `toTeamId`. `EA` `football/league.py#L508-L555`, `football/transaction.py#L1-L33` | `/league/{league_key}/transactions`, with the types add, drop, commish, and trade. Filters: `type`, `types`, `team_key`, `count`. **No week filter.** `YD` "Transaction Resource" |
| Waivers and FAAB bids | Types `WAIVER` and `WAIVER_ERROR`, with `bidAmount`. A failed claim is a `WAIVER_ERROR` row. `EA` `requests/espn_requests.py#L194-L204` | **[lib]** `faab_bid` on a claim. `YF` `yfpy/models.py#L695`. Pending claims show only with `team_key`: "Pending transactions will not show up if you simply ask for all of the transactions in the league". The docs show only the status `successful`. `YD` |
| Trades | Type `TRADE_ACCEPT`. Caveat: "TRADE_ACCEPT rows from mTransactions2 often have empty items except for the authenticated owner's deals." The client fills them from player cards. `EA` `football/league.py#L517-L523` | Trades with trader and tradee team keys. **[lib]** `picks` on a trade. `YF` `yfpy/models.py#L672-L699` |
| Free agents | `view=kona_player_info` with `filterStatus` `FREEAGENT` and `WAIVERS`. `EA` `football/league.py#L411-L449` | `/league/{league_key}/players`, with `start` and `count` for pages. `YD` "Players Collection". **[lib]** yfpy asks for 25 players per call. `YF` `yfpy/query.py#L1622` |
| Player projections | The stat row with `statSourceId` 1, per scoring period, in the league scoring, with a stat breakdown. `EA` `football/player.py#L85-L96` | **No player projection in the docs.** Only `team_projected_points` at the team level. `YD`. **[lib]** yfpy models only `TeamProjectedPoints`. `YF` `yfpy/models.py#L882-L894` |
| Player list | `/players?view=players_wl` with `filterActive`, for the whole NFL, not one league. `EA` `requests/espn_requests.py#L162-L168` | `/game/{game_key}/players` or `/league/{league_key}/players`, in pages. `YD` "Player Resource" |
| NFL schedule | `view=proTeamSchedules_wl`, with game dates in ms. `EA` `requests/espn_requests.py#L156-L160`, `football/player.py#L36-L49` | `/game/{game_key}/game_weeks` gives the dates of each week. `YD` "Game Resource". **[lib]** a matchup has `week_start` and `week_end`. `YF` `yfpy/models.py#L1341-L1343` |
| Draft | `view=mDraftDetail`, with `bidAmount` and `keeper`. `EA` `base_league.py#L74-L104` | `/league/{league_key}/draftresults`. `YD` |

### History of past seasons

- **[lib]** ESPN keeps one league id across seasons. The league reply lists `status.previousSeasons`. Source: `EA` `base_league.py#L59-L61`.
- **[lib]** ESPN serves 2018 and later at `seasons/{year}/segments/0/leagues/{id}`. It serves older seasons at `leagueHistory/{id}?seasonId={year}`. Source: `EA` `requests/espn_requests.py#L44-L53`.
- **[lib]** The box score with player lines works only from 2019: "Cant use box score before 2019". Source: `EA` `football/league.py#L348-L349`. So the per-player history of ESPN goes back to 2019. Team scores go back further.
- **[vendor]** Yahoo gives one game id per NFL season, such as `461` for 2025 and `399` for 2020. `games;game_codes=nfl` with no `seasons` lists all seasons. Source: `YD` "Games Collection".
- **[lib]** The Yahoo NFL game list starts in 1999, with game key `50`. Source: `YF` `yfpy/query.py#L577-L597`.
- **[vendor]** League metadata has `renew` and `renewed` elements, with no explanation in the docs. Source: `YD`.
- **[lib]** `renew` holds the game id and league id of the season before, such as `"371_52364"`. `renewed` holds the season after. Source: `YF` `yfpy/models.py#L410-L413` and `yfpy/query.py#L1124-L1125`.

### The five fetches of our port

| Port method | Sleeper today | ESPN **[lib]** | Yahoo |
| --- | --- | --- | --- |
| `fetch_week` | 11 raw files, the schedule, the projections ahead, and trending | One league call with `mTeam,mRoster,mMatchup,mSettings,mStandings`, plus one call each for the scores, the transactions, and the players | Many calls: settings, teams, the scoreboard, one roster call per team for player points, the transactions, and the player pages |
| `fetch_live` | Rosters now and stats now | The same league call, with `totalPointsLive` | The scoreboard and the rosters of the current week |
| `fetch_past_leg` | Matchups, transactions, stats, and projections of one past week | The same views with `scoringPeriodId`. Player lines from 2019 only | The scoreboard and rosters with `week`. Transactions come for the whole season, so the adapter must sort them into weeks |
| `fetch_players` | One file of about 5 MB, cached one day | One `players_wl` call | Pages of 25 players. No single file |
| `fetch_projections` | A public Sleeper endpoint per week, with no league id | League-scored projections in the player views, by scoring period | **None** |

## IDs

| ID | Sleeper | ESPN **[lib]** | Yahoo **[vendor]** |
| --- | --- | --- | --- |
| League | A new id each season. The config holds `(season, id)` pairs | The same integer each season, with the season in the URL. `EA` `requests/espn_requests.py#L44-L53` | `{game_key}.l.{league_id}`, such as `461.l.1000`. A new key each season. `YD` "League Resource" |
| Team | `roster_id`, an integer from 1. The owner is a separate `user_id` | Team `id`, an integer. Owners are member ids. `EA` `football/team.py#L9`, `base_league.py#L118-L124` | `{game_key}.l.{league_id}.t.{team_id}`, such as `461.l.1000.t.1`. `YD` "Team Resource". **[lib]** a manager has a `guid` |
| Player | A Sleeper string id. A team defense has a non-digit id | An ESPN integer `id`. `EA` `football/player.py#L15` | `{game_key}.p.{player_id}`, such as `461.p.30121`. The game key prefix changes each season. `YD` "Player Resource" |
| Transaction | `transaction_id` string | `id`. `EA` `football/transaction.py#L3` | **[lib]** `transaction_key`, such as `406.l.413954.tr.555`. `YF` `yfpy/models.py#L672-L692` |

Each provider has its own player ids. No two of the three share a player id. A join across them needs an id map.

## Limits and terms

- **[lib]** ESPN publishes no rate limit and no developer terms. ffscrapr treats HTTP 429 as the limit. It suggests "under 1000 calls per 60 seconds". Source: `FS` `R/espn_connect.R#L10-L12`, `R/espn_api.R#L96-L98`.
- **[vendor]** The Disney Terms of Use cover ESPN. Section 2, clause B(x) forbids to "access, monitor, copy or extract the Disney Products using a robot, spider, script, or other automated means". It also forbids "data mining or web scraping". Source: https://disneytermsofuse.com/english/
- **[vendor]** Yahoo gives no number. It "may temporarily throttle or limit access" on excessive use. Source: https://sports.yahoo.com/developer
- **[vendor]** Yahoo allows one developer account. It forbids separation of the data. It requires the line "Fantasy data provided by Yahoo Fantasy" and the logo. Source: https://sports.yahoo.com/developer
- **[vendor]** Yahoo replies carry `refresh_rate="60"`, with no explanation. Source: `YD`.
- **[lib]** yfpy treats HTTP status 999 as the Yahoo rate limit. Source: `YF` `yfpy/query.py#L435-L437`.

## Field map

Legend for the gap column:

- **no**: the provider has the field.
- **map**: the provider has the data in another shape or vocabulary. The adapter translates it.
- **derive**: the adapter computes the field from other data.
- **GAP**: the provider cannot fill the field.

ESPN cells rest on espn-api **[lib]**. Yahoo cells rest on `YD` **[vendor]**, except where they name yfpy.

| Our field | ESPN source | Yahoo source | Gap |
| --- | --- | --- | --- |
| `RawState.season` | `seasonId` | Game `season` | no |
| `RawState.display_week` | `scoringPeriodId`. `EA` `base_league.py#L56-L69` | League `current_week`. **[lib]** `YF` `yfpy/models.py#L434` | no |
| `RawState.season_start_date` | Derive from `proTeamSchedules_wl` game dates | Derive from `game_weeks`. **[lib]** league `start_date`, `YF` `yfpy/models.py#L471` | derive |
| `LeagueSettings.last_scored_leg` | Derive from the schedule winner of each matchup period | Derive from the scoreboard status of each week | derive |
| `LeagueSettings.reserve_slots` | IR count in `lineupSlotCounts` | `IR` count in roster positions | map |
| `LeagueSettings.waiver_budget` | `acquisitionSettings.acquisitionBudget` | No budget field found. Only `uses_faab` and the team `faab_balance` **[lib]** | GAP: Yahoo |
| `RawLeague.roster_positions` | `lineupSlotCounts`, by numeric slot id | Roster positions, by name | map |
| `RawLeague.scoring_settings` by Sleeper stat key | `scoringItems` by numeric `statId` | Stat modifiers by numeric `stat_id` | map |
| `RawUser.user_id`, `display_name` | Member `id` and display name | Manager `guid` and `nickname` **[lib]** | map |
| `RawUser.avatar`, `metadata.team_name` | Team name and `logo` | Team name and team logos | map |
| `RawRoster.roster_id` | Team `id` | `team_id` from the `team_key` | map |
| `RawRoster.owner_id` | First of `owners` | Manager `guid` **[lib]** | map |
| `RawRoster.players` | `roster.entries` | `roster;week={week}` | map |
| `RosterSettings.fpts`, `fpts_decimal` | `record.overall.pointsFor`, one float | Standings points for, one float | map |
| `RosterSettings.wins`, `losses` | `record.overall` | Standings outcome totals | no |
| `RosterSettings.waiver_budget_used` | `transactionCounter.acquisitionBudgetSpent` | Budget minus `faab_balance` **[lib]**. Needs the budget, so it fails with the gap above | GAP: Yahoo |
| `RosterSettings.waiver_position` | `waiverRank` | `waiver_priority` **[lib]** | no |
| `RawMatchup.roster_id`, `points` | `teamId`, `totalPoints` | Team key, team points | map |
| `RawMatchup.matchup_id` | Schedule entry `id`, or one number per home and away pair. Bye: no away team | No id. Number the pairs in the scoreboard | derive |
| `RawMatchup.players`, `starters` | `rosterForCurrentScoringPeriod.entries` with `lineupSlotId`. Rebuild the ordered list with `"0"` for an empty slot | `roster;week` with `selected_position`. Rebuild the same list | derive |
| `RawMatchup.players_points` | `appliedTotal` per entry | Player week stats, one call per team | map |
| `RawTransaction.transaction_id`, `type` | `id`, `type` | `transaction_key`, `type` | map |
| `RawTransaction.status` with `failed` | `WAIVER_ERROR` rows give a failed claim | Only `successful` in the docs. No failed claim | GAP: Yahoo |
| `RawTransaction.leg` | `scoringPeriodId` | No week field and no week filter. Derive from `timestamp` and the week dates | derive |
| `RawTransaction.created` in ms | `processDate` | `timestamp` in seconds, times 1000 | map |
| `RawTransaction.roster_ids`, `adds`, `drops` | `teamId` and `items`. Trade items can be empty, and the client fills them from player cards | Players with source and destination team keys | derive |
| `TransactionSettings.waiver_bid` | `bidAmount` | `faab_bid` **[lib]** | map |
| `RawTransaction.draft_picks` | Not found in the client | `picks` **[lib]** | GAP: ESPN |
| `RawProjection.stats` for week N | Stat row with `statSourceId` 1. Rescore to half PPR from the breakdown | None | GAP: Yahoo |
| `RawAheadWeek.projections`, half PPR | Stat rows with `statSourceId` 1 for later scoring periods. Not tested in the client | None | GAP: Yahoo |
| `RawStatLine.stats` by Sleeper key, such as `gp`, `tm_off_snp`, `pts_half_ppr` | Numeric stat ids. `tm_off_snp` not found | Numeric stat ids. `tm_off_snp` not found | GAP: both |
| `RawStatLine.team`, `player.position` | `proTeamId`, default position | Team abbreviation, display position | map |
| `RawStatLine.game_id` | Not found. The pro schedule gives a date and an opponent only | Not found | GAP: both |
| `RawTrending.count`: adds across all leagues in one day | Not found. Only ownership percent | Not found. Only `percent_owned` | GAP: both |
| `RawScheduleWeek` | The full season schedule in `mMatchup` | `matchups` of each team, all weeks | derive |
| `RawBracketMatch.r`, `m` | Derive from `playoffTierType` | Derive from `is_playoffs` and `is_consolation` **[lib]** | derive |
| `players` file keys: `full_name`, `position`, `team`, `injury_status` | `fullName`, eligible slots, `proTeamId`, `injuryStatus` | Name, display position, team, status | map |
| `players` file keys: `gsis_id`, `injury_body_part` | Not found | Not found | GAP: both |

The table has **10 GAP rows**. Yahoo misses 9: the waiver budget, the budget used, failed claims, both projections, and the four NFL rows. ESPN misses 5: draft picks and the four NFL rows. Both miss 4 rows of NFL data, not league data: the Sleeper stat keys, `game_id`, the trending count, and the `gsis_id`. Sleeper serves those 4 from public endpoints with no league id and no auth.

## The Sleeper assumptions in the port

1. **`players_cache: Path` in three methods.** `fetch_week`, `fetch_live`, and `fetch_players` take a cache path for one bulk file. Yahoo has no bulk file. Fix: let each adapter own its cache dir from its constructor, and drop the argument from `Provider`.
2. **A players dict keyed by the Sleeper id.** `fetch_players` and `RawWeek.players` give `dict[str, dict]` with Sleeper keys, and readers take raw keys. Fix: name one canonical player id, and make each adapter map its ids to it with an id map.
3. **Projections from a separate public endpoint.** `fetch_projections` takes only `season`, `week`, and `last_regular_week`, with no league id. Yahoo has no projections. ESPN has them only in the league reply. Fix: put projections behind an NFL data port, which Sleeper fills for every league.
4. **NFL data inside the league fetch.** `fetch_week` also gets `state`, `stats`, `projections`, `trending`, and `players`, which are not league data. Fix: split `Provider` into a league provider and an NFL data source. Keep Sleeper as the one NFL data source.
5. **One `league_id: str` per season.** The caller passes `config.league_id(season)`, which suits Sleeper's new id each season. ESPN repeats one id. Yahoo needs `{game_key}.l.{id}`. Fix: keep the `(season, id)` pairs. Let a Yahoo adapter build the key, or let a later tool fill the pairs from `previous_league_id`, `previousSeasons`, or `renew`.
6. **The "past leg" fetches one week of transactions.** `fetch_past_leg` assumes transactions by week. Yahoo has no week filter. Fix: let the Yahoo adapter fetch the season once and sort the moves into weeks by timestamp.
7. **`roster_id` as the team key, with users apart.** The models join `owner_id` to `users`, as Sleeper does. ESPN and Yahoo nest owners in the team. Fix: none in the port. The adapter can synthesize `users` and `rosters`.
8. **Sleeper wire shapes in the raw models.** Examples: `fpts` plus `fpts_decimal`, `matchup_id` per row, `starters` with `"0"` for an empty slot, `created` in ms, and Sleeper `type` and `status` strings. Fix: keep them as the internal shape now, and document each one as an adapter duty.
9. **Sleeper stat and scoring keys.** `scoring_settings`, `stats`, and projections use names such as `rec_yd` and `pts_half_ppr`. Fix: keep the Sleeper names as our stat vocabulary, and give each adapter a map from its numeric stat ids.
10. **Raw saved as Sleeper JSON.** `file_json` gives "the JSON of the raw file `name`, in the shape Sleeper sent it", and `history.py` reads it back. Fix: say in `raw.py` that a raw file is the internal shape, and let a later adapter also save its own replies apart.
11. **Raw reads outside `parse.py`.** The waiver modules, `snapshot.py`, `history.py`, `live.py`, and `pipeline.py` read raw fields. `waiver_price.py` holds the Sleeper status map `CLAIM_RESULTS = {"complete": True, "failed": False}`. Fix: open a ticket that moves those reads behind `parse.py`.

## Answer

**Suggestion for Brian to decide.** Yes, the port can take ESPN and Yahoo later, if this spec makes three small choices now. First, split the league provider from an NFL data source, and keep Sleeper as the one NFL data source. Second, name the Sleeper player id the canonical id. Third, move the cache path into the adapter. Leave the field translations, the derived Yahoo week of a move, and the Yahoo gaps in FAAB budget, failed claims, and projections to the later spec of each provider.

Two risks stay. ESPN is unofficial, its cookies need a person, and the Disney terms forbid automated access. Yahoo needs an approved app, a refresh token that a CI job must store again when Yahoo rotates it, and the attribution line.

## A second ESPN source

Brian gave `pseudo-r/Public-ESPN-API`. Source: https://github.com/pseudo-r/Public-ESPN-API

- **[lib]** It is unofficial. It says the APIs "are not officially supported and may change without notice."
- **[lib]** It gives the base URL `https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}`. espn-api now uses the host `lm-api-reads.fantasy.espn.com`.
- **[lib]** It lists the views `mTeam`, `mRoster`, `mMatchup`, `mMatchupScore`, `mSettings`, `mDraftDetail`, `mScoreboard`, `mStandings`, `mStatus`, and `kona_player_info`.
- **[lib]** It agrees that a private league needs the cookies `espn_s2` and `SWID`.
- It does not cover the transactions, the waiver claims, the FAAB bids, the projections, or the history of past seasons. For those, `cwendt94/espn-api` stays the source.
- It says that "Public" means the endpoint is reachable. It does not mean permission to collect or reuse the data.
