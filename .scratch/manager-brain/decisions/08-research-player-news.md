# 08: How the Advisor gets player news

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

In prototype 04 Brian noted: "Taylor is on the colts who are trash. He is in trade rumors affecting his snap count and usage." The fact sheet has no news. The waiver page already runs a web search for expert takes per player (the `experts` facts of the waiver board, fact IDs `WV.research.{player_id}.{n}`). Find how the Advisor can reuse it: the cost and the time per player and per call, the freshness, the players it covers in one trade and in one press of the finder, and the cache. Find how a rumor stays a rumor in the case, with its source and date, and never turns into a fact.

## Decision

Brian, 2026-11-09, from the notes in `08-research-player-news.notes.md`.

1. The Advisor does not reuse the waiver web search. It reads only free agents: in week 8 of cpc, 0 of 24 researched players were on a roster.
2. On each analyzer call, code fetches the Sleeper news feed of each player of the trade: `api.sleeper.app/players/nfl/<player_id>/news`, through the `fetch_news` the pipeline already has. The Finder fetches it only for the players of its shortlist of 10, at most about 20 players.
3. The sheet gets the newest 2 items per player from the last 7 days, as facts `NEWS.{player_id}.{n}`. The text is "Reported on <YYYY-MM-DD> by <Source>: <description, cut at 300 characters>". The URL stays out of the numbers.
4. A cache in memory keeps the feed of a player for 1 hour. A failed call gives no news fact and never stops the analysis.
5. A rumor stays a rumor:
   - A code check: a bullet that cites a `NEWS.` fact must hold "reported", "report", "per", "according to", "rumor", or the source name. A failure retries once, as each check does now.
   - A prompt rule: a news fact is a report. The Advisor never states a trade or a role change as done.
   - A Jev check, log-only: "Does the bullet state the report as a sure fact?"
   - The number check already keeps each number to the cited news text.
6. Every news item gets the same rule, so a game recap also says "reported". The cost is a little wordiness. The gain is one simple rule with no Jev step in the path of the call.

Known risk: the endpoint is unofficial and can change with no notice. The fallback is a sheet with no news, so the Advisor judges as it did in prototype 04.
