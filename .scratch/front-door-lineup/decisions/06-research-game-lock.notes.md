# 06: Research notes on the game lock

Ticket: `decisions/06-research-game-lock.md`. Research date: 2026-11-11, a Wednesday of NFL week 10. No NFL game runs today. The first game of week 10 is NYG at WAS, Thu 2026-11-12 at 01:15Z.

All calls use a generic User-Agent and no key. The raw call output sits in the scratchpad of the research session and is not kept in the repo.

## The endpoints the repo uses now

`packages/league/python/src/league/provider/sleeper.py` holds the Sleeper adapter. The API and the pipeline both import it.

- `OFFICIAL_URL = "https://api.sleeper.app/v1"`: `state/nfl`, the league, the rosters, the matchups.
- `UNOFFICIAL_URL = "https://api.sleeper.app"`: `stats/nfl/{season}/{week}` and `projections/nfl/{season}/{week}`, with `season_type=regular` and one `position[]` per position.

The Sleeper docs at https://docs.sleeper.com/ cover only the `v1` read API. They do not list the stats, projections, schedule, or GraphQL endpoints. The docs say: "stay under 1000 API calls per minute, otherwise, you risk being IP-blocked". They also say the players call "is intended only to be used once per day at most".

## 1. Does the stats endpoint show a player once his game starts?

Yes. Sleeper writes a stats row for each player of a game within minutes of the kickoff. Before the first kickoff of a week, the endpoint returns an empty list.

### Evidence today, before any game of week 10

```
$ curl -s https://api.sleeper.app/v1/state/nfl
{"week":10,"leg":10,"season":"2026","season_type":"regular",...,"display_week":10,...}

$ curl -s -g 'https://api.sleeper.app/stats/nfl/2026/10?season_type=regular&position[]=WR'
[]

$ curl -s https://api.sleeper.app/v1/stats/nfl/regular/2026/10
{}
```

The `v1/stats/nfl/regular/...` path from the ticket is an old path. It returns `{}`. The repo path is the one that works.

### Evidence from week 9

`clients/cpc/data/2026/week-09/raw/stats.json` holds 743 rows. Each row has these fields at the top level:

- `game_id`, for example `"202610903"`. It is the same `game_id` as the Sleeper schedule and the Sleeper GraphQL below.
- `date`, for example `"2026-11-05"`. It is a date only, with no time. It is the US Eastern date of the game.
- `team`, `opponent`, `week_shard` (`"9_5"`), `company` (`"sportradar"`).
- `last_modified` and `updated_at`, in epoch milliseconds. They are the time of the last write to the row.
- `status`: `null` on all 743 rows.

The `stats` object holds `gp` (games played), `gms_active`, the snap counts, and the points.

- 454 rows have `gp` 1. The player took the field.
- 289 rows have no `gp`. 260 of them hold only `gms_active` and the `pos_rank_*` values of 999. 180 of these 289 players had no `injury_status` at the time of the fetch. So Sleeper writes a row for each player on the roster of a team in the game, and not only for players who play.
- `gms_active` is 1.0 on 713 rows, inactive players too. It is not a test of "active for the game". The 30 rows with no `gms_active` are all `DEF`.

I compared `last_modified` of each row with the kickoff time of its game from the Sleeper GraphQL (see question 2).

```
min minutes from kickoff to last_modified, per game_id:
{'202610903': 1.7, '202610931': 0.7, '202610916': 2.8, '202610930': 0.4, '202610935': 3.1,
 '202610902': 4.9, '202610906': 3.3, '202610926': 2.9, '202610921': 0.6, '202610914': 1.6,
 '202610922': 2.9, '202610929': 0.8, '202610919': 3.0, '202610905': 2.5, '202610920': 1.8}
rows before kick: 0
rows within 30 min of kick: 262 of 743
```

Each of the 15 games has rows whose last write came 0.4 to 4.9 minutes after the kickoff. No row has a write before the kickoff. Most of the 262 early rows belong to players who did not play, so Sleeper never wrote to them again.

### What I cannot see today

1. I cannot see the first write of a row, only the last write. The data shows that rows exist within 5 minutes of the kickoff. It does not show that they never exist earlier.
2. No game runs today, so I cannot poll the endpoint during a kickoff. The week 9 data is enough to set the delay at about 5 minutes or less.

### Result for the game lock

The stats endpoint shows a game started about 0 to 5 minutes late. A row in it for a `game_id` proves that the game started. An empty result does not prove that the game has not started, in the first minutes. Use it as a second signal, not as the lock source.

## 2. Which free source gives the kickoff time?

Three free sources answer. None needs a key.

### a. Sleeper schedule (REST)

```
$ curl -s https://api.sleeper.com/schedule/nfl/regular/2026
[{"status":"complete","date":"2026-09-13","home":"CAR","week":1,"game_id":"202610105","away":"CHI"}, ...]
```

`https://api.sleeper.app/schedule/nfl/regular/2026` returns the same 26946 bytes. It has 272 games, 14 in week 10.

- Time field: none. `date` is a date only, in US Eastern. For example, CHI at TB of week 9 shows `"date":"2026-11-08"`, and the kickoff was 2026-11-09T01:20Z.
- `status`: `pre_game` or `complete` today. A live game likely shows a third value. I cannot see it today.
- So this source cannot set a lock to the minute.

### b. Sleeper GraphQL `scores` (the sleeper.com web app uses it)

```
$ curl -s -H 'content-type: application/json' https://sleeper.com/graphql -d '{"operationName":"batch_scores","variables":{},"query":"query batch_scores { scores(sport: \"nfl\", season_type: \"regular\", season: \"2026\", week: 10) { date game_id metadata season season_type sport status week start_time } }"}'
```

It returns HTTP 200 and 14 games for week 10. One line per game:

```
202611023 pre_game 1794532500000 2026-11-13T01:15:00+00:00 NYG WAS False False False
202611011 pre_game 1794753000000 2026-11-15T14:30:00+00:00 DET NE  False False False
202611002 pre_game 1794765600000 2026-11-15T18:00:00+00:00 ATL KC  False False False
202611003 pre_game 1794878100000 2026-11-17T01:15:00+00:00 BAL LAC False False False
...
(game_id, status, start_time, metadata.date_time, home, away, has_started, is_in_progress, is_over)
```

- Time fields: `start_time` in epoch milliseconds, and `metadata.date_time` in ISO 8601 UTC with `+00:00`.
- Live fields: `status`, `metadata.has_started`, `metadata.is_in_progress`, `metadata.is_over`, `metadata.canceled`.
- `game_id` and the team codes (`WAS`, `LAR`, `LV`) match the stats and the projections of the repo. No map is necessary.
- Week 9 shows the past state: `202610903 complete 1793927700000 2026-11-06T01:15:00+00:00 True True`.
- Key: none. Note that this endpoint has no docs. Sleeper can change it without notice.

### c. ESPN public scoreboard JSON

```
$ curl -s 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?seasontype=2&week=10&dates=2026'
```

It returns HTTP 200 and 14 events for week 10, plus `week.teamsOnBye` (CHI, DEN, PHI, TB).

```
401873052 2026-11-13T01:15Z STATUS_SCHEDULED pre Thu, November 12th at 8:15 PM EST ['NYG', 'WSH'] True
401873053 2026-11-15T14:30Z STATUS_SCHEDULED pre Sun, November 15th at 9:30 AM EST ['DET', 'NE'] True
(event id, events[].date, status.type.name, status.type.state, status.type.detail, teams, competitions[].timeValid)
```

- Time field: `events[].date` and `competitions[].date`, in UTC with a `Z`. `timeValid` is true when ESPN has a confirmed time.
- Live field: `status.type.state` is `pre`, `in`, or `post`.
- Key: none. This endpoint also has no official docs.
- The ids differ from Sleeper. ESPN writes `WSH` and Sleeper writes `WAS`. The API needs a map of team codes to use it.

The ESPN and Sleeper GraphQL times agree for all 14 games of week 10.

## 3. When does Sleeper set the final inactive status?

No primary source says. The data shows that Sleeper does not mark the game-day inactives of the NFL as one status.

### The NFL rule

Each club names its inactive players 90 minutes before the kickoff. Sources:

- https://nfl.com/news/new-rule-to-allow-teams-to-replace-late-covid-19-inactives (a club can activate a new player up to 30 minutes before kickoff, in a 2020 COVID exception).
- https://nbcsports.com/nfl/profootballtalk/rumor-mill/news/game-time-decision-loophole-helps-teams-avoid-having-to-downgrade-players-from-questionable ("the club is permitted to wait until the 90-minute meeting to list the player on its Inactive List").

I found no page on operations.nfl.com that states the rule.

### The Sleeper fields

From `clients/cpc/data/2026/week-09/raw/players.json` (12229 players, fetched after week 9). For QB, RB, WR, TE, and K with a team:

```
(status, injury_status) counts:
('Active', None) 653, ('Inactive', 'IR') 96, ('Active', 'Out') 82, ('Active', 'Questionable') 18,
('Inactive', None) 13, ('Active', 'PUP') 6, ('Inactive', 'Questionable') 2,
('Practice Squad', 'NA') 1, ('Active', 'DNR') 1
```

- `injury_status` holds the injury report value: `Questionable`, `Out`, `IR`, `PUP`, `NA`, `DNR`, or `null`. No row holds `Inactive`.
- `status` holds the roster status: `Active`, `Inactive`, or `Practice Squad`. 96 of the 111 `Inactive` rows are on `IR`. It is not the game-day inactive list.
- `practice_participation` and `practice_description` are `None` on all 872 rows.
- 180 players of week 9 had no `gp` and no `injury_status`. These are healthy scratches and backups. Sleeper gave them no flag.

### What I cannot see today

The players file is a snapshot. It does not show when a value changed. No game runs today, so I cannot watch `injury_status` in the 90 minutes before a kickoff. The Sleeper docs ask for one players call per day, so a poll of it at the kickoff is not a good fit.

### Result for the game lock

The game lock does not need the inactive status. The lock depends on the kickoff of the game of the team, not on the player. The inactive status matters for the advice "start or sit" before the kickoff. That is a separate question for the spec.

## 4. Recommendation

Use the Sleeper GraphQL `scores` query as the source of the game lock.

| Source | Kickoff time | Live state | Same ids as the repo | Docs |
| --- | --- | --- | --- | --- |
| Sleeper GraphQL `scores` | `start_time`, epoch ms, UTC | `status`, `has_started`, `is_in_progress` | yes, `game_id` and team codes | none |
| ESPN scoreboard | `events[].date`, UTC | `status.type.state` | no, needs a team map (`WSH`) | none |
| Sleeper stats rows | none | a row exists about 0 to 5 min after kickoff | yes | none |

The reasons:

1. It gives the kickoff to the minute, in UTC, with no key.
2. It uses the same `game_id` and team codes as the stats and projections that the API reads now.
3. It gives a live flag `has_started` next to the time. The API can check both, so a slow flag or a wrong clock alone does not leave a started game unlocked.
4. One call gives the full week, so the API can fetch it once per request or keep a short cache.

A suggested rule: a game is locked when `now >= start_time` or when `has_started` is true. The ESPN scoreboard is the fallback if the GraphQL call fails.

## Open risks

1. No source has docs. Sleeper can change or block the GraphQL and the stats paths without notice.
2. No live game ran today. The live values of `status` and the live flags of a game in progress are not seen. The first chance is NYG at WAS at 2026-11-13T01:15Z. The week 9 `complete` rows already show the past state.
3. A moved or delayed kickoff changes `start_time`. The API must fetch it fresh and not keep it for days.
4. Sleeper gives no game-day inactive flag. If the spec wants to warn about an inactive starter, it needs another source or a separate research ticket.
