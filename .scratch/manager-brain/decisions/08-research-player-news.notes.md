# 08: Research notes on the player news

Ticket: `decisions/08-research-player-news.md`. Research date: 2026-11-09.
Paths with `packages/` are relative to the repo root. Data paths are in the main checkout, because the worktree has no client data.

**Recommendation:** do not reuse the waiver web search for the Advisor. Fetch the Sleeper news feed of each player of the trade at the time of the call, and give each item to the sheet as a `news.report` fact with its source and date. The feed is free, takes about 0.11 s per player, and already holds the Taylor trade rumor. A new code check makes each bullet that cites a news fact say "reported" or name the source.

## Summary

- **The waiver search does not cover a trade.** It reads only the free agents of the waiver board, at most 32 per build. In week 8 of cpc, 0 of 24 researched players were on a roster. Every player of a trade is on a roster.
- **The waiver search is slow and costs money.** Each player is one Claude Opus 5.5 call with up to 4 web searches, at about $0.10 to $0.14 per player.
- **The Sleeper news feed covers the rostered players.** It answered for 173 of 173 rostered cpc players. 161 of them had at least one item, and 153 had an item from the last 7 days. The newest item had a median age of 0.75 days.
- **The feed already has the rumor that Brian named.** For Jonathan Taylor (`6813`), 3 of 5 items on 2026-11-09 are trade-deadline reports, each with a source, a time, and a URL.
- **The pipeline already uses the feed.** `fetch_news` gives the fact `AW.game_changer.news` of the weekly page. So the Advisor reuses a known source, not a new one.

## 1. How the waiver search works now

- The code is `packages/waiver/python/src/waiver/research.py`. The task named `apps/pipeline/`, but the step lives in the `waiver` package. The pipeline calls it once per build, after the engine: `apps/pipeline/src/cornerstone/pipeline.py:447-451`.
- **The players:** `research_players` takes the ranked players of each bucket but drops, each once, at most `RESEARCH_PLAYERS` = 32. Source: `research.py:42-50`, `packages/waiver/python/src/waiver/tunables.py:36`. The buckets hold pool players, so no rostered player gets a take.
- **The call:** one `messages.parse` call per player, model `claude-opus-5-5`, `max_tokens=16000`, effort `low`, with the tool `{"type": "web_search_20260209", "name": "web_search", "max_uses": 4}`. Source: `research.py:29-39`, `packages/facts/python/src/facts/writer.py:19` and `:73-99`.
- **The prompt:** the system prompt is `packages/waiver/python/src/waiver/prompts/research.md`. It keeps only items from the last 7 days, and it sets a search order: the Yahoo waiver column of Justin Boone, three Yahoo writers and two Yahoo podcasts, the wider web, and one spare search. The user message gives today's date, the player, his engine facts, and "Give at most 2 claims". Source: `research.py:53-65`, `tunables.py:39`.
- **The output:** `ResearchOut`, a list of `ResearchClaim` with `text`, `url`, `source`, `date`, and `stance` (`backs`, `disputes`, or `news`). Source: `packages/league/python/src/league/models.py:471-486`. A claim with no web URL drops: `research.py:68-70`.
- **The facts:** one fact per claim, `WV.research.{player_id}.{n}`, with the text "`<claim>` Source: `<source>`, `<url>`". The digits of the URL are not in the numbers. Source: `research.py:73-84`.
- **The failure rule:** a failed call leaves the player with no claim. When every call fails, `experts_missing` is true and the build goes on. Source: `research.py:87-115`.
- **The cache:** there is no separate cache. The claims save in the facts file of the week, so a rewrite reads them and does not search again. Source: the comment at `pipeline.py:447`.
- **On disk:** `clients/<slug>/data/<season>/week-<NN>/facts.json`, key `waiver.buckets.<bucket>[].research` and the `facts` of each player. The page shows them from `clients/<slug>/published/<season>/week-<NN>/waiver.json`. Source: listing of `clients/cpc/data/2026/week-08/` on 2026-11-09.

## 2. The cost and the time

### The waiver web search

The input tokens come from the log of a real week 8 rebuild of cpc: `.scratch/jev/evidence/AT-1/rebuild.log`, the 29 lines `ResearchOut call`. The prices come from https://platform.claude.com/docs/en/about-claude/pricing, read 2026-11-09: Opus 5.5 at $4 base input, $5 for a 5-minute cache write, $0.20 for a cache read, and $20 output per million tokens. Web search costs "$10 USD per 1,000 searches".

| Part | Tokens in 29 calls | Cost in 29 calls | Cost per call |
| --- | --- | --- | --- |
| Cache write | 90,299 | $0.45 | $0.016 |
| Cache read | 898,444 | $0.18 | $0.006 |
| Uncached input | 6,063 | $0.02 | $0.001 |
| Input total | 994,806 | $0.66 | $0.023 |
| Web searches | not logged, at most 4 per call | at most $1.16 | at most $0.04 |
| Output | not logged | unknown | unknown |

- The second rebuild in `.scratch/jev/evidence/AT-3/rebuild.log` gives almost the same input, 1,005,691 tokens in 29 calls.
- The log has no output tokens and no search count, so the full cost per call is an estimate. `tunables.py:33-35` states "about $0.14 per player with tokens", from the pricing page read 2026-10-23. The input and search parts above give $0.06 at most, so the output and the thinking make up the rest.
- The per-call time is not in any log, because the log lines have no time stamps. The build of AT-1 ran from 13:18:01 to 13:32:43, 882 s, with 62 Claude calls: 29 research, 19 writer, and 14 verifier. That is about 14 s per call on average over all kinds. A research call with 1 to 4 searches is most likely in the range of 10 to 30 s. One live probe can fix the number if the spec needs it.

### The Sleeper news feed

- The endpoint is `https://api.sleeper.app/players/nfl/<player_id>/news`. Source: `packages/league/python/src/league/provider/sleeper.py:34` and `:128-130`. It is unofficial: the docs at https://docs.sleeper.com list no news endpoint (the table of contents in decision 06 notes, section 1).
- It costs nothing. The docs give one limit: "stay under 1000 API calls per minute". Source: decision 06 notes, section 1.
- The time: 173 sequential GET calls on 2026-11-09 took a median of 0.114 s and a p90 of 0.124 s each. The body is about 5 to 6 KB. Source: a script run from the session scratchpad on the rostered players of `clients/cpc/data/2026/week-08/raw/rosters.json`.
- The shape: a list of at most 5 items, each with `published` in epoch milliseconds, `source`, `player_id`, and `metadata` with `title`, `description`, and `url`. The `url` is `None` for some Rotowire items. The order is not promised (`packages/week/python/src/week/sheet/awards.py:62`).
- The sources in the 805 items: Rotoballer 320, Rotowire 254, FantasyPros 231.

## 3. The freshness

- The weekly build runs on Tuesday after the Monday game. The week 8 waiver board of cpc was built at 2026-11-03 18:26 ET, a Tuesday. NorCal was built at 2026-11-04 19:51 ET. Week 7 of cpc was built at 2026-10-27 14:12 ET. Source: the `waiver.built` value in each `facts.json`.
- The prompt keeps items from the 7 days before the build date. So a take can be 7 days old at the build.
- On a Saturday, the build is 4 days old. A take can be up to 11 days old. A real case: the week 8 cpc board has a claim on Sam Roush dated 2026-10-28, which is 10 days old on Saturday 2026-11-07.
- The trade deadline of 2026 is Tuesday 2026-11-10, per the Rotoballer item on Taylor. A rumor of the deadline lives for days, not weeks, so a weekly take misses most of it.
- The Sleeper feed is fresh on the call. The newest item per rostered player had a median age of 0.75 days and a p90 of 2.85 days on 2026-11-09.

## 4. The coverage

- **One trade:** the analyzer judges the players of the trade, 2 to 3 in the 1-for-1, 2-for-1, and 1-for-2 shapes (`decisions/03-research-search-cost.notes.md:37`). A bigger hand-made trade has more. Each is on a roster.
- **One press of the Finder:** the partner filter passes about 9 or 10 of 11 partners. Jev picks at most 4 targets per side per partner (`TARGET_MAX`, `04-prototype-judge-arms.notes.md:195`). So the offers touch at most about 4 asker players and 40 partner players. The shortlist keeps 10 offers (`SHORTLIST_KEEP`, `04-prototype-judge-arms.notes.md:174`), so the Advisor pick reads at most 30 player slots, most often 10 to 20 unique players.
- **Only the shortlist needs news.** Jev narrows on the facts, and Claude reads the news when it picks three. So one press needs at most about 20 feed calls.
- **The waiver cache:** in the week 8 board of cpc, 24 unique players were researched and 20 have a claim. NorCal: 23 researched and 17 have a claim. Week 7 of cpc: 27 and 20. 0 of the 24 cpc players were on one of the 173 rostered spots. So the cache covers a trade only when a player was a free agent at the build and a manager added him later.

## 5. How a rumor stays a rumor

### The guards now

- `check_response` in `packages/analyzer/python/src/analyzer/analysis.py:315-349` runs the checks on each bullet and on the verdict reason.
- **The facts check:** each cited fact ID must be in the sheet, and the bullets of a side must cite at least one fact. Source: `analysis.py:292-294`.
- **The number check:** each number in a bullet must be in the numbers of a cited fact or in the breakdown, and must appear in their text. Source: `_prose_failures`, `_allowed`, and `_allowed_text` at `analysis.py:201-239`, with `number_failures` of `facts.verifier`.
- **The inner words check:** no bullet and no verdict reason holds a word of `INNER_WORDS`, matched whole, in any case, with its plural. Source: `analysis.py:47-68` and the calls at `:307` and `:347`.
- The ID suffix already acts as a kind: `_allowed` skips the numbers of a fact whose ID ends in `.value` (`analysis.py:233`). The `Fact` model has no kind field (`models.py:379-385`).

### The shape of a news fact

- **ID:** `NEWS.{player_id}.{n}`, with the prefix as the kind `news.report`. The prefix lets a check find each news fact with no change to the `Fact` model.
- **Text:** `Reported on <YYYY-MM-DD> by <Source>: <description cut at 300 chars>`. Use `Nums` on the description and the date, as `_news_facts` of `awards.py:58-72` does, with its `NEWS_MAX_CHARS` = 300. Keep the URL out of the numbers, as `research_facts` does.
- **Which items:** the newest 2 items per player from the last 7 days, newest first. Drop an item with no description.
- **Players:** the `players` list holds the player name, so the name check and the repeat rule still work.

### The guard

1. **The attribution check, in code.** A bullet that cites a `NEWS.` fact must hold an attribution word: "reported", "report", "reports", "per", "according to", "rumor", or the source name. Add it to `_bullet_failures` beside `_inner_word_failures`. A failure retries once, as each check does now.
2. **The prompt rule.** The analysis prompt says that a news fact is a report, not a fact. Claude names the source or says "reported", and never states a trade or a role change as done.
3. **The Jev check, log-only.** The faithfulness check of the MAP asks one more question per bullet with a news cite: "Does the bullet state the report as a sure fact?" It starts log-only, as the MAP says for every Jev check.

- The number check already keeps a rumor from growing numbers: each number must be in the cited news text.
- A code check cannot tell a rumor from a sure event in the text of the feed. So every news item gets the same rule, and a box-score recap gets "reported" too. The cost is a little wordiness. The gain is one simple rule with no Jev step in the critical path.

## 6. The options

Prices and times use the numbers of sections 2 and 4. A press of the analyzer is about 20 s and $0.10 to $0.12 now (`04-prototype-judge-arms.md`, decision 5).

| Option | Covers a trade | Freshness on Saturday | Extra cost | Extra latency |
| --- | --- | --- | --- | --- |
| A. Reuse the waiver cache only | almost never: 0 of 24 on a roster | up to 11 days old | $0 | 0 s |
| B. Web search per trade player on each call | yes | minutes old | about $0.10 to $0.14 per player, so $0.30 to $0.40 per trade and $1 to $3 per Finder press | 10 to 30 s per call, with the players in parallel; it doubles the press time |
| C. Weekly web search for all rostered players | yes | up to 11 days old | 173 players at about $0.12, about $21 per client per week | 0 s on the call; about 30 to 90 min more build time, sequential |
| D. Sleeper news feed per trade player on each call | yes, 161 of 173 rostered players had an item | median 0.75 days | $0 | about 0.1 s per player; about 0.3 s per trade and 2 s per Finder press, sequential, or one call time in parallel |
| E. D plus the waiver cache for a player the feed has no item on | yes | as D | $0 | as D |

- **B is out.** It doubles the time of a press and triples its cost, for news that D gives free.
- **C is out.** It costs about 5 times the waiver search now, about $4.50 a week, and it is stale by the weekend.
- **D is the recommendation.** Cache the feed per player in memory for 1 hour, so a second press on the same player makes no call. A failed call gives no news fact and never stops the analysis, as `_get_or_empty` does now (`sleeper.py:79-86`).
- **E adds little.** The 12 rostered players with no item are most likely deep bench players, and a waiver claim is a free-agent take. Leave it out unless the spec finds a gap.
- **The risk of D:** the endpoint is unofficial and can change with no notice. The fallback is a sheet with no news, so the Advisor judges as it does now.

## 7. The Taylor case

The feed for `6813` on 2026-11-09, the newest first (UTC):

| Published | Source | Title |
| --- | --- | --- |
| 2026-11-09 15:50 | Rotoballer | Broncos Could Add Offensive Help Before Trade Deadline |
| 2026-11-09 09:46 | Rotoballer | Giants Trading for Jonathan Taylor Would Be a "Surprise" |
| 2026-11-08 23:58 | Rotoballer | Colts Could Receive "11th-Hour Offer" for Jonathan Taylor |
| 2026-11-08 22:58 | Rotowire | Jonathan Taylor - Quiet before potential trade |
| 2026-11-08 22:55 | FantasyPros | Jonathan Taylor loses fumble in Week 9 loss |

Three of five items are trade reports with hedge words: "could", "would be a surprise", "potential". A fact text such as "Reported on 2026-11-08 by Rotoballer: The Indianapolis Colts could entertain an 11th-hour offer for running back Jonathan Taylor ..." lets a bullet say "Rotoballer reports the Colts could trade Taylor before the deadline", which passes the attribution check. A keyword count over all 805 items of the rostered players found 27 items about trade talk.
