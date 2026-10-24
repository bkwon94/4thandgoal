# Research: the Yahoo sources and the cost of the web search tool

Date: 2026-10-23. Every URL below was read on this date.

## 1. The three Yahoo writers

Answer: Josh is Josh Norris. Hayden is Hayden Winks. Harmon is Matt Harmon. Yahoo signed Norris
and Winks on 2026-07-08, after Underdog closed its content network. The weekly waiver column at
Yahoo is not by any of the three. Justin Boone writes it.

Evidence for the names:

- Yahoo press release, "Yahoo Sports adds Josh Norris and Hayden Winks to award-winning Yahoo
  Fantasy roster":
  https://unified.www.yahooinc.com/press/yahoo-sports-adds-josh-norris-and-hayden-winks-to-award-winning-yahoo-fantasy-roster
  The release names the roster as "Matt Harmon, Nate Tice, Justin Boone and others".
- Barrett Media, 2026-07-08: https://barrettmedia.com/2026/07/08/yahoo-sports-josh-norris-hayden-winks/
- Awful Announcing: https://awfulannouncing.com/yahoo/josh-norris-hayden-winks-shutdown-underdog-content.html

### Author pages

All three return HTTP 200.

| Writer | Role | Author page |
| --- | --- | --- |
| Josh Norris | "Fantasy Analyst", co-host of the Josh and Hayden show | https://sports.yahoo.com/author/josh-norris/ |
| Hayden Winks | "Fantasy Analyst", co-host of the same show | https://sports.yahoo.com/author/hayden-winks/ |
| Matt Harmon | Host of Yahoo Fantasy Forecast | https://sports.yahoo.com/author/matt-harmon/ |

- Norris's page lists mostly short videos with no dates.
- Winks writes a weekly column, "Players Hayden Winks is higher and lower on than consensus for
  Week 7", published 2026-10-23:
  https://sports.yahoo.com/fantasy/article/fantasy-football-rankings-players-hayden-winks-is-higher-and-lower-on-than-consensus-for-week-7-174815135.html
- Norris and Winks share rankings articles, for example "Week 7 Fantasy Football WR Rankings
  (Top 42)": https://sports.yahoo.com/article/week-7-fantasy-football-wr-rankings-top-42-210415700.html
- Not confirmed: the exact job titles. Yahoo shows only labels such as "Fantasy Analyst".

### The weekly waiver wire column

- Week 7, by Justin Boone, published 2026-10-20:
  https://sports.yahoo.com/fantasy/article/week-7-fantasy-football-waiver-wire-rookies-mike-washington-jr-omar-cooper-jr-among-top-pickups-141451458.html
- The page says Boone "breaks down the recommended waiver-wire pickups" every Monday in season.
- The title pattern is "Week N Fantasy Football Waiver Wire: <players> among top pickups", under
  `/fantasy/article/`. Not confirmed: we fetched only the Week 7 URL, so the pattern is not
  checked against other weeks.
- Other Week 7 waiver pieces at Yahoo:
  - Chris Allen, 2026-10-23: https://sports.yahoo.com/fantasy/article/fantasy-football-4-players-off-the-waiver-wire-you-can-start-if-youre-desperate-in-week-7-152117020.html
  - David Hartman, 2026-10-19: https://sports.yahoo.com/articles/fantasy-football-2026-waiver-wire-221847111.html

### Podcast feeds

The feed URLs come from the Apple search API, `https://itunes.apple.com/search?term=...&entity=podcast`.
Each feed was fetched directly.

| Show | Feed | Apple page | State |
| --- | --- | --- | --- |
| Yahoo Fantasy Football with Josh & Hayden | https://feeds.simplecast.com/Lj5JhCEG | https://podcasts.apple.com/us/podcast/yahoo-fantasy-football-with-josh-hayden/id1558961587 | Live, built 2026-10-23 19:30 UTC |
| Yahoo Fantasy Forecast with Matt Harmon | https://feeds.simplecast.com/s3ulbOAs | https://podcasts.apple.com/us/podcast/yahoo-fantasy-forecast-with-matt-harmon/id1031567659 | Live, built 2026-10-23 15:43 UTC |

- "Reception Perception: The Show" is now an Audacy show, not a Yahoo show:
  https://rss.amperwave.net/v2/feed/audacynetwork/reception-perception-the-show
  Not confirmed: whether Harmon still hosts it.

### Yahoo fantasy RSS

- https://sports.yahoo.com/fantasy/rss.xml redirects to https://sports.yahoo.com/fantasy/rss/.
  It is a valid RSS 2.0 feed of `/fantasy/article/` links. The Week 7 Boone column was not in
  the items we read, so the feed does not hold every column.
- https://sports.yahoo.com/fantasy/football/rss.xml returns 404.
- Not confirmed: per-author RSS feeds.

### What the research prompt uses

The prompt names these sources first, in this order, then the wider web:

1. The Josh Norris author page and the Hayden Winks author page.
2. The Matt Harmon author page.
3. The weekly waiver wire column under `sports.yahoo.com/fantasy/article/`.
4. The two podcast feeds.

## 2. The Claude web search tool

### Price

- Web search costs **$10 per 1,000 searches**, so $0.01 per search, plus the standard token
  cost. The search results bill as input tokens. A search that fails is not billed.
  Source: https://platform.claude.com/docs/en/about-claude/pricing (section "Web search tool")
  and https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool (section
  "Usage and pricing").
- Code execution is free when it runs with `web_search_20260209` or later (dynamic filtering).
  Source: the pricing page.
- Claude Opus 5.5 costs $4 per million input tokens, $20 per million output tokens, and $0.20
  per million cache hits. Source: the pricing page, table "Model pricing".
- The response counts the searches in `usage.server_tool_use.web_search_requests`.

### Cost per call

One research call is one player. A call with up to 3 searches and about 20,000 input tokens of
results and 1,500 output tokens costs about 3 x $0.01 + 20,000 x $4 / 1M + 1,500 x $20 / 1M,
which is about $0.14. Thirty-two players cost about $4.50 a week. This is an estimate. The live
test reports the real usage.

### Model id

`src/cornerstone/writer.py` sets `MODEL = "claude-opus-5-5"`. Every call in the tool uses it.

### How the Python SDK declares the tool

The tool is a plain dict in the `tools` list of `messages.create` or `messages.parse`. No beta
header is needed. Source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool

```python
tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}]
```

- Versions: `web_search_20250305` (basic), `web_search_20260209` (dynamic filtering),
  `web_search_20260318` (adds `response_inclusion`). Opus 5.5 takes all three.
- `allowed_domains` and `blocked_domains` take bare domains. A request with both returns 400.
- Errors return HTTP 200 with a `web_search_tool_result` whose `content` is an error object.
- The API can stop with `stop_reason: "pause_turn"` on a long search turn.
- Citations are always on for web search. The structured outputs page says citations are
  incompatible with `output_config.format` and return a 400:
  https://platform.claude.com/docs/en/build-with-claude/structured-outputs (section "Feature
  compatibility"). That statement is about document citations. Not confirmed: whether web search
  with `messages.parse` returns a 400. The live test answers it.
