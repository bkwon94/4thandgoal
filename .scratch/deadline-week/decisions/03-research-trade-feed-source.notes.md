# 03 notes: where the live feed of trades gets its data

Ticket: `03-research-trade-feed-source.md`. Map: `../MAP.md`.
Worktree: `.claude/worktrees/deadline-week`, branch `deadline-week`. Each repo source is a file of this repo, read on 2026-11-18.
The live calls went to the public Sleeper API on 2026-11-19 01:50 UTC: 7 calls in all. The raw answers stay in the session scratchpad, not in the repo.
These notes name rosters by roster id only, because the repo is public.

## Summary

- Sleeper allows a browser read from any origin. Each answer carries `access-control-allow-origin: *`.
- The Sleeper docs set a soft limit of 1000 calls per minute per IP, with an IP block past it.
- Sleeper's own CDN caches each transactions answer for up to 300 s. A plain read can be about 5 minutes old, or up to 10 minutes with `stale-while-revalidate`. A query string skips that cache.
- A trade gives `roster_ids`, `adds`, `drops`, `draft_picks`, `waiver_budget`, `status`, `created`, and `status_updated`. It gives no names.
- The browser cannot get player names from Sleeper cheaply. The API on Fly already has them in `GET /teams`.
- Recommendation: path (b). Add one cheap read route on the Fly API with a 30 s server cache. The browser polls it every 60 s while the page is visible. Cost: none extra. Freshness: about 30 s to 90 s.

## 1. How the repo reads transactions now

- `packages/league/python/src/league/provider/sleeper.py:34` sets `OFFICIAL_URL = "https://api.sleeper.app/v1"`.
- `packages/league/python/src/league/provider/sleeper.py:220`, `:244-245`, and `:293` read `{league}/transactions/{week}`. The weekly build also reads week N−1 again as `transactions_prev.json` (`:43-45`), because Sleeper adds moves to a week after the build.
- `packages/league/python/src/league/provider/raw.py:96-109` holds `RawTransaction`: `transaction_id`, `type`, `status`, `leg`, `created` in ms, `roster_ids`, `adds`, `drops`, `settings`, `draft_picks`.
- `packages/league/python/src/league/parse.py:221-233` `parse_trades` keeps only `type == "trade"` and `status == "complete"`. It turns `created` into a UTC time, and it builds a `DraftPick` from each pick. It drops `waiver_budget`.
- The PRD of transaction history (`.scratch/transaction-history/PRD.md`) changes only the pipeline. Each weekly build writes the full week N−1 into `history/`. The site does not change. So the site sees trades only once a week, through `page.json`.
- `clients/cpc/published/2026/week-09/page.json` key `trades` holds each trade as `sides`. Each side has `team` (with `roster_id`, `name`, `owner`, `avatar_url`, record), `players` (each with `name` and `headshot: "headshots/<player_id>.png"`), and `picks`.

## 2. The CPC league

`clients/cpc/client.toml` `[seasons.2026]`: `provider = "sleeper"`, `league_id = "1386167364424318976"`.
`GET https://api.sleeper.app/v1/state/nfl` gave `"week":11,"leg":11`. The deadline is after the week 11 games, so the feed reads leg 11. A trade lands in the leg of the week in which it happens (field `leg`, below).

## 3. CORS

Each call sent `Origin: https://example.com`.

`GET /v1/league/1386167364424318976/transactions/10` and `/11`, both `200`:

```
access-control-allow-credentials: true
access-control-allow-origin: *
access-control-expose-headers: etag,date
cache-control: public, s-maxage=300, stale-while-revalidate=300, stale-if-error=600
cdn-cache-control: public, max-age=300, stale-while-revalidate=300, stale-if-error=600
etag: W/"..."
server: cloudflare
```

`OPTIONS` with `Access-Control-Request-Method: GET` gave `HTTP/2 204` and:

```
access-control-allow-methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
access-control-allow-origin: *
access-control-max-age: 1728000
```

A plain `fetch(url)` sends no custom header, so the browser sends no preflight at all. A browser on any origin can read the answer.

### The cache of the Sleeper CDN

- The first read of week 11 gave `cf-cache-status: MISS`. A read 94 s later gave `cf-cache-status: HIT` and `age: 94`.
- The same URL with `?t=<unix time>` gave `cf-cache-status: MISS`. So a query string skips the CDN cache.
- Without a query string, a new trade can take up to 300 s to show. With `stale-while-revalidate=300`, the worst case is about 600 s.

## 4. Rate limit and terms

Source: https://docs.sleeper.com/, read 2026-11-18.

- "A general rule is to stay under 1000 API calls per minute, otherwise, you risk being IP-blocked."
- "Be mindful of the frequency of calls."
- "The Sleeper API is a read-only HTTP API that is free to use for non-commercial purposes"
- "No API Token is necessary, as you cannot modify contents via this API."
- The docs say nothing for or against a read from a browser. This is a personal, non-commercial project, so the terms allow it.

## 5. The fields of a trade

Weeks 10 and 11 hold no trade: week 10 has 22 `free_agent/complete`, 16 `waiver/complete`, 13 `waiver/failed`. Week 11 has 9 `free_agent/complete`.
So a third read took week 9, which has 2 trades. The saved CPC history of weeks 1 to 9 holds 22 trades, each with `status: "complete"`.

The keys of a live trade: `adds`, `consenter_ids`, `created`, `creator`, `draft_picks`, `drops`, `leg`, `metadata`, `roster_ids`, `settings`, `status`, `status_updated`, `transaction_id`, `type`, `waiver_budget`.

| Field | Live value in week 9 | Meaning (docs.sleeper.com) |
| --- | --- | --- |
| `type` | `"trade"` | The kind of move. Other kinds are `free_agent` and `waiver`. |
| `status` | `"complete"` | The state. The docs show only `"complete"`. Week 10 shows `"failed"` for waivers. |
| `leg` | `9` | The week of the move. |
| `created` | `1794158840673` | The ms time stamp of the proposal. |
| `status_updated` | `1794160439613` | The ms time stamp of the last status change. For a complete trade, this is the accept time. Here it is 27 minutes after `created`. |
| `roster_ids` | `[5, 10]` | The rosters in the trade. |
| `consenter_ids` | `[5, 10]` | The rosters that agreed. |
| `adds` | `{"<player_id>": <roster_id>, ...}` | Each player and the roster that gets him. 7 players in each live trade. |
| `drops` | `{"<player_id>": <roster_id>, ...}` | Each player and the roster that gives him. |
| `draft_picks` | `[]` | Each traded pick: `season`, `round`, `roster_id` (first owner), `previous_owner_id`, `owner_id` (new owner). |
| `waiver_budget` | `[{"amount": 5, "sender": 4, "receiver": 8}]` | FAAB sent in the trade. The second live trade sent $5. |
| `creator` | a Sleeper user id | The user who proposed it. Do not show it. It is a user id, not a roster id. |
| `settings`, `metadata` | `null` | Null for a trade. |

Notes for the spec:

- Sort the feed by `status_updated`, not by `created`. A trade can sit for a while before the accept.
- Show only `type == "trade"` and `status == "complete"`, as `parse_trades` does. The docs do not list the states of a pending trade. A pending trade likely does not show in this endpoint at all, but no live sample proves that.
- `parse_trades` drops `waiver_budget`. The feed must keep it, because one of the two week 9 trades sent FAAB.
- A trade can have more than two rosters. Read `roster_ids`, and never assume two sides.

## 6. The three paths

Facts that the table uses:

- The Fly API runs one `shared-cpu-1x` machine with `min_machines_running = 1` (`apps/api/fly.toml`). It always runs, so a new route costs nothing extra.
- The Fly API allows the site origins with CORS (`apps/api/fly.toml` `CORNERSTONE_ALLOWED_ORIGINS`, `apps/api/src/cornerstone_api/app.py:290`).
- The API counts 30 requests per minute per IP on most routes (`apps/api/src/cornerstone_api/settings.py:24`, `app.py:88-98`, keyed on `Fly-Client-IP`). The cheap read routes run `_read_guard` instead (`app.py:101-104`). It checks the passphrase and counts nothing.
- The API caches `GET /teams` for `TEAMS_CACHE_SECONDS = 300` (`packages/league/python/src/league/tunables.py:27`).
- The site Worker `cpc` serves static assets only (`apps/site/wrangler.jsonc`). It has no script, no KV, and no cron now.
- The Workers Free plan gives 100,000 requests per day and 5 Cron Triggers per account (https://developers.cloudflare.com/workers/platform/limits/).
- The KV Free plan gives 100,000 reads per day and 1,000 writes per day (https://developers.cloudflare.com/kv/platform/limits/). A write each minute is 1,440 per day, so the cron must write only on a change.

| | (a) Browser reads Sleeper direct | (b) Browser reads the Fly API, which reads Sleeper with a short cache | (c) Cloudflare cron Worker writes a JSON file |
| --- | --- | --- | --- |
| Cost | Free. | Free. The machine runs now. | Free if within limits. It needs a new Worker script, a KV namespace or R2 bucket, and a cron. |
| Load on Sleeper | One call per open phone per poll. 20 phones at 30 s is 40 per minute, far under 1000. | One call per cache window, whatever the number of phones. 2 per minute at a 30 s cache. | One call per cron run. 1 per minute at most, because a cron runs at most each minute. |
| Load on our side | None. | One cheap read per phone per poll, on a machine that already serves the analyzer. | A KV read per phone per poll. A KV write per change. |
| Freshness | Up to 300 s to 600 s, from the Sleeper CDN. A query string fixes that, but then each phone hits the Sleeper origin. | About the cache time plus the poll time. With a query string on the server read, about 30 s to 90 s. | About 60 s to 120 s, plus the KV spread time, which the limits page does not state. |
| Names | None from Sleeper without the 5 MB player file. It still needs the Fly API, or `page.json`, for names. | The route has the roster and player names on the server (section 7). The answer carries the names. | The Worker has no names. It must also read the player file or the Fly API. |
| Failure | Sleeper down: the feed shows nothing. A Sleeper IP block hits one phone. A Sleeper shape change breaks each phone at once, with no place to catch it. | Sleeper down: the API serves the last good answer. Fly down: the feed and the analyzer fail together. The deadline board can show the trades of the weekly build. | Sleeper down: the file keeps the last good list. One more system to deploy and watch, for a feature that lives four days. |
| New code | Site only. | One API route and one site poll. The route reuses the Sleeper provider and `parse_trades`. | A Worker script, its bindings, a deploy step, and a site poll. |

## 7. How names map

- Team names: `GET /teams` on the Fly API gives each `roster_id` with `team`, `manager`, `avatar`, and `players` (`packages/analyzer/python/src/analyzer/routes.py:133-157`). `page.json` key `teams` also maps each roster id to `name`, `owner`, and `avatar_url` (`clients/cpc/published/2026/week-10/page.json`).
- Player names: `GET /teams` gives each rostered player with its name and headshot, through `_player` (`routes.py:112-121`). Every player in a trade is on a roster before and after the trade, so the map covers each `adds` and `drops` key.
- Picks need no name. Show the round and the season, and map `roster_id` and `owner_id` to team names.
- FAAB needs no name. Map `sender` and `receiver` to team names.
- Headshots: the site already uses `headshots/<player_id>.png` for each player in a published trade. A player outside the published pages may have no headshot file in `public/`. The route can return the `headshot` URL that `_player` gives.
- The cache of `GET /teams` is 300 s, so it can hold the roster before the trade. That is fine for the names, because a name does not change. The route must not read roster membership from the cache to decide which side got a player. It reads that from `adds`.

## 8. Recommendation

Path (b), with these numbers:

1. Add one route to the Fly API, for example `GET /<slug>/deadline/trades`. It runs `_read_guard`, so it checks the passphrase and does not count against the 30 per minute limit.
2. The route reads `transactions/<leg>` of the current leg from Sleeper with a query string, so the Sleeper CDN cache does not delay it.
3. The route keeps its answer for 30 s on the server. Sleeper then sees at most 2 calls per minute.
4. The route returns each complete trade with team names, player names, picks, FAAB, and `status_updated`.
5. The site polls the route every 60 s while the page is visible, and stops when the tab hides or the deadline passes.

The reasons:

- It is free. The Fly machine runs now, and the route is a cheap read.
- The load on Sleeper stays flat, whatever the number of phones at the dinner.
- At the dinner, many phones share one public IP. Under the 30 per minute limit, 12 phones at a 30 s poll make 24 requests per minute. With the analyzer, that hits the limit. `_read_guard` avoids that, and a 60 s poll halves the load.
- The names come from data the API already has. Path (a) and path (c) both still need the API or a big file for names.
- One place handles a Sleeper failure or a shape change, and can serve the last good answer.
- Path (c) adds a new system to deploy for a feature that lives four days.

Path (a) is the fallback if Fly is down for the event. Sleeper allows it, and the site can show roster ids mapped through `page.json` teams.

## Open questions for the spec

- The poll time: 60 s gives news within about 90 s. 30 s halves that, but doubles the reads per phone.
- The deadline board can show the trades of the weekly build when the route fails. Decide if it shows a note.
- No live sample shows a pending or vetoed trade. Decide if the spec needs one before the event.
