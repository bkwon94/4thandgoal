# Trade grade v3: position value and the trade value chart

Status: ready-for-agent
Date: 2026-10-20
Amends: `design/specs/2026-10-20-trade-grade-v2-design.md`

## Problem Statement

The v2 grade reads each player's own numbers: points per game, position rank, usage, injuries,
and the team's record and need. It does not know that an RB1 is worth more than a WR1 of the same
rank, or that a TE1 is worth less than both. It also has no market view of a player's worth. Two
players with similar points per game can be far apart in what the league would pay for them.
The grades in week 6 read fair on stats and wrong on value.

The page also carries a note that names a persona. Brian wants no names on the page.

## Solution

Each trade chapter gains a trade value for every traded player, read from the half-PPR redraft
trade value chart that Brian trusts, the one at peakedinhighskool.com. The chart for week N is
the one the author labels "Week N". The values and a position order shape the grade. Neither
appears on the page. The grade stays the writer's opinion from the fact sheet, with no note that
says so.

## User Stories

1. As the commissioner, I want each trade graded with a market view of each player, so that the
   grade matches what the league would pay.
2. As the commissioner, I want an RB valued above a WR, a WR above a TE, and a TE above a QB at
   equal rank, so that scarcity at the position counts.
3. As the commissioner, I want the grade for a week 6 trade to use the week 6 chart, so that the
   grade reflects the market at the time of the trade.
4. As the commissioner, I want a week 7 trade to use the week 7 chart, so that the newest values
   grade the newest trades.
5. As the commissioner, I want no trade value, chart name, or tier on the page or in the prose,
   so that the page reads as a grade and a reason, not a spreadsheet.
6. As the commissioner, I want the page note about opinions gone, so that no persona is named.
7. As the commissioner, I want the Tuesday build to fetch the chart on its own, so that no manual
   step stands between me and a published page.
8. As the commissioner, I want to drop a chart image into the repo by hand when the public one is
   late or wrong, so that the build can still use the right chart.
9. As the commissioner, I want a build to go on when the chart site is down, so that a site outage
   never blocks the Tuesday page.
10. As the commissioner, I want a misread chart to add no value facts rather than wrong ones, so
    that a bad read never moves a grade the wrong way.
11. As the commissioner, I want a player who is not on the chart graded from his v2 facts alone,
    so that a spelling mismatch costs nothing.
12. As the commissioner, I want a command that fetches and reads the chart for a week and shows
    the table, so that I can check a read before a build.
13. As the commissioner, I want week 6 rebuilt and republished with the week 6 chart, so that the
    live page carries v3 grades.
14. As the commissioner, I want every number on the page to still come from a cited fact, so that
    the v2 citation rules hold.
15. As the writer, I want the trade values as facts on the sheet, so that I can weigh each side.
16. As the writer, I want a side sum fact, so that a 2-for-1 trade compares in one read.
17. As the writer, I want a rule that tells me the position order, so that I break ties the same
    way every week.
18. As the verifier, I want a value number in a trade sentence to fail the code check, so that the
    writer cannot leak a value onto the page by citing the fact.
19. As the author of the chart, I want my full table never republished, so that my work stays mine.
20. As the maintainer, I want the chart read cached per week, so that one Claude image call per
    week is the whole cost.
21. As the maintainer, I want the fetch, the read, and the name match each to take a callable, so
    that tests run with no network and no Claude.

## Implementation Decisions

### The chart

- Source: the public half-PPR redraft PNG on peakedinhighskool.com. The site's WordPress media
  API lists every weekly file, one per chart date, with a filename of the form
  `1QB0.5PPR4pt_YYYYMMDD.png`. The build queries that API and picks the file for the week.
- Chart week: the file whose filename date falls on or after the Tuesday cutoff of week N and
  before the cutoff of week N+1. The cutoff is the one the trade window already uses, 08:00
  Eastern on the Tuesday after week N-1. The week 6 chart is dated 2026-10-13. The week 7 chart
  is dated 2026-10-20.
- Cache: one directory for charts under the data cache. Per week it holds the PNG and the parsed
  JSON. A PNG placed there by hand wins, and the build never overwrites or re-fetches it. A
  parsed JSON that exists is reused, so the image read runs once per week.
- Outage: if the media API or the file fetch fails and no file exists for the week, the build
  uses the newest cached chart that is 14 days old or less. Past that, the build makes no value
  facts and logs a warning. The build never fails on the chart.
- The build never republishes the image or the full table. Only the values of traded players
  reach the fact sheet, and none reach the page.

### The read

- The build sends the PNG to Claude with a structured output: the header week, the header date,
  and a list of rows with value, name, and position. The call goes through the same client and
  the same parse path the writer uses. The model is the writer's model.
- Guards, all of which must pass or the week gets no value facts:
  1. The header week equals the expected week.
  2. Values never rise from one row to the next.
  3. Every value is a multiple of 0.5 between 0 and 100.
  4. Every position is one of RB, WR, TE, QB.
  5. When a parsed chart for the prior week exists, the row count is within 10 percent of it.
- A failed guard logs which guard failed and keeps the PNG, so a hand check is possible.

### The name match

- A key is the name with letters only, lowercase, with a suffix of Jr, Sr, II, III, or IV
  removed, plus the position. Sleeper's `search_full_name` and `position` give a player's key.
  The chart row gives the other. The match runs from each traded player to the chart, never the
  other way, so two NFL players with one name never collide.
- A traded player with no match gets no value fact.

### The facts

- `T{n}.{pid}.value`: "{name}'s trade value was {v} before the trade." One number.
- `T{n}.{rid}.value`: "{team} gave {x} and got {y} in trade value." When a traded player has no
  value, the sentence adds ", with {name} unlisted" and names each such player. When the trade
  holds draft picks, the sentence adds "; the pick is not valued" or "the picks are not valued".
  The sums cover listed players only. The side fact exists only when at least one player in the
  trade has a value.
- Both facts carry the team and the player names as the v2 facts do, and their numbers go
  through the same number recorder.
- The vocabulary gains one term: **trade value**, the half-PPR redraft trade value from the
  chart for the week of the trade. It shapes the grade and never appears on the page.

### The writer

- Rule 18 gains two sentences. One sets the position order: at equal rank and points, an RB
  outweighs a WR, a WR outweighs a TE, and a TE outweighs a QB; a DEF carries little trade
  value. The other says the value facts weigh the two sides and never appear in a sentence: no
  value, no sum, no chart, no tier.
- The league has no kickers. The rule does not mention them.

### The verifier

- The code check fails a trade chapter sentence that holds a number equal to any number of a
  `.value` fact in that chapter, unless the same number is also in a cited fact that is not a
  `.value` fact. This holds whether or not the sentence cites the value fact.

### The page

- The note under the Trades label goes away. No text replaces it. The cards do not change.

### The pipeline and the CLI

- The bundle builder takes the chart values as one optional input beside the nflverse week. The
  pipeline wires a chart fetcher the same way it wires the nflverse fetcher, and tests patch that
  name. The build record in the verify file gains a `chart` source flag.
- A new `chart` command takes a season and a week, fetches and reads the chart, and prints the
  table and the guard results. It writes the cache like a build does.
- Week 6 is rebuilt with the normal build command after v3 lands. Brian reviews and publishes.

## Testing Decisions

- A good test feeds inputs at a seam and asserts text, numbers, or a result. It never asserts how
  a helper is built.
- Seam 1, the bundle: a fixture JSON of parsed chart values for week 6 with every traded player
  and a few more. Tests build the trade bundle with it and assert the value fact texts, the side
  sums, the unlisted clause, the pick clause, and that a player with no match has no fact. Prior
  art: the trade fact tests that use the week 6 trade bundle fixture.
- Seam 2, the chart module: the fetch takes a `fetch` callable, the read takes a `read`
  callable. Tests fake both. They cover: the week-to-file pick, the hand-placed PNG that wins, the
  reuse of a parsed JSON, the stale fallback at 14 days, the no-chart case, each guard, and the
  name match on the hard cases: a suffix, periods in initials, an apostrophe, a hyphen. Prior
  art: the nflverse download tests and the writer tests that pass a fake call.
- Seam 3, the verifier: a blurb with a value number in a trade sentence fails the code check, and
  the same number from a points fact passes. Prior art: the trade tests that call the code check.
- Seam 4, the render: the week page holds no opinion note. Prior art: the render tests.
- The writer prompt test: rule 18 holds the position order sentence. Prior art: the writer rule
  tests.
- One `live` test reads the real week 6 PNG with Claude and checks the guards pass. It runs only
  on purpose.

## Out of Scope

- Any value, sum, tier, or chart name on the page or in the prose.
- Tier colors and the trend column of the chart.
- Draft pick values. Rule 20 stands.
- Kickers. The league has none.
- The FantasyCalc or KeepTradeCut sources.
- A dynamic site or the Live page.
- The deferred v2 minors in the todo list.
- A split of the trade facts out of the sheet module, unless the chart facts force it.

## Further Notes

- The chart's Patreon release is Tuesday evening. The public file lands Wednesday morning. The
  Tuesday 08:00 build for week N needs the week N chart, which is public six days before. So the
  public fetch is enough, and the hand-placed PNG is a backstop.
- The Tuesday launchd job has never run. Week 7 is its first run and now adds a third network
  source. Read the build log after it fires.
- Credit: no terms of use exist on the site, and its robots file allows crawlers. The build
  takes only the values of traded players and never republishes the table.
- The one Claude image call per week costs about one cent.
