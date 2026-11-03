# Manager pages: one page per team, the best-looking page on the site

Status: ready-for-agent
Date: 2026-10-29
Repos: the pipeline `cornerstone-fantasy-sleeper-weekly-report` and the site `cpcfantasyfootball`. The same PRD sits in both.
Glossary: **Manager page**, **Managers index**, **Hero**, **Roster grade**, **Playoff odds**, **Bench points**, **Points line**, **Slot rank**, **Moves**, **Best adds**, **Top performers**, **Awards shelf** in the site `GLOSSARY.md`. **Position rank**, **Lineup value**, **Hole**, **The line**, **Depth** in the pipeline `GLOSSARY.md`.
ADRs: none new. Pipeline ADR 0003 rules depth by position rank. ADR 0006 rules a start as a real start.
Follows: `.scratch/next-week-byes/PRD.md`.

## Problem Statement

The site tells the story of the week. It never tells the story of one team. A manager who wants to know
how good his roster is, what he did on the wire, who carried him, and where he stands for the playoffs
reads six chapters across two pages and adds it up himself. Brian wants a page per manager, built from
data, with the polish of the best page on the site.

## Solution

A **manager page** per team per season at `/<season>/managers/<roster_id>`, and a **managers index** at
`/<season>/managers/` that lists the twelve teams in standings order. A "Managers" entry in the menu.
Every team name on the standings, the rankings rows, the matchup cards, and the trade cards links to
the team's page.

The page opens with the **hero**: the avatar, the team name, the owner, the record, and the standing.
Under it, three numbers: the **roster grade** as a letter, the **playoff odds** as a percent with the
change since last week, and the power rank with its move. Then five chapters: Season So Far, Roster,
Moves, Best Adds, Top Performers.

The pipeline writes one `site/<season>/managers.json` each week after the report, from the saved
weeks of the season. Publish copies it next to `rankings.json`. The site joins it with `rankings.json`
for the odds and the rank. No writer call. Every line on the page comes from data.

Three moments move, all off under reduced motion: the grade letter settles in and the slot ranks
follow in a stagger, the odds number counts up once, and the points line draws from week 1 to now.
Everything else uses the one reveal the site has.

## User Stories

1. As a reader, I want a page for each team, so that I read one team's season in one place.
2. As a reader, I want the team name on the standings to open its page, so that I never hunt for the way in.
3. As a reader, I want the team names on the rankings rows, the matchup cards, and the trade cards to link too, so that every mention is a way in.
4. As a reader, I want a "Managers" entry in the menu, so that I can reach the index from any page.
5. As a reader, I want the index in standings order with the avatar, the name, the owner, the record, and the grade, so that I pick a team at a glance.
6. As a reader, I want the hero to show the team first, so that the page feels like the team's own.
7. As a reader, I want the grade, the odds, and the power rank under the hero, so that the three numbers that matter are one glance away.
8. As a reader, I want one quiet line of context under each number, so that I see the trend without a chart.
9. As a reader, I want the grade as a letter, so that it reads like a report card.
10. As a reader, I want the slot ranks under the grade with one depth word each, so that I see why the grade is what it is.
11. As a reader, I want the points line against the league median, so that I see the team's form in one shape.
12. As a reader, I want a filled dot for a win and a hollow dot for a loss on the points line, so that the results ride on the line.
13. As a reader, I want bench points for the season and the worst week with the player that sat, so that I see how well the manager sets lineups.
14. As a reader, I want the awards shelf with four counts, so that I see what the report gave the team.
15. As a reader, I want a zero count on the shelf in the quiet color, so that the shelf reads whole.
16. As a reader, I want the moves by week, newest first, so that this week's moves come first.
17. As a reader, I want a week with no moves to read "No moves.", so that the timeline reads whole.
18. As a reader, I want the season totals of adds, drops, and trades at the top of the moves chapter, so that I see how active the manager is.
19. As a reader, I want each add with its bid, so that I see what the manager paid.
20. As a reader, I want each trade with both sides, so that I see what the team gave and got.
21. As a reader, I want the best adds with the points since the add and the projection over the same span, so that I see which pickups paid.
22. As a reader, I want the top five performers with the total and the points per game started, so that I see who carried the team.
23. As a reader, I want headshots on the performers and the adds, so that the rows read like the report.
24. As a reader, I want the page to look like the report at every tier, so that the site stays one site.
25. As a reader, I want a chapter rail on a desktop, so that I jump to a chapter as on the week page.
26. As a reader on a phone at 390px, I want every chapter to fit with no horizontal scroll, so that the page reads whole.
27. As a reader in dark mode, I want the grade, the line, and the dots readable on the dark surfaces, so that the page works in both themes.
28. As a reader with reduced motion on, I want the grade, the odds, and the line shown at once, so that nothing moves.
29. As a reader with motion on, I want the grade to settle in and the slot ranks to follow, so that the grade reveal has a beat.
30. As a reader with motion on, I want the odds to count up once, so that the number lands.
31. As a reader with motion on, I want the points line to draw from week 1 to now, so that the season plays once.
32. As a reader with motion on, I want nothing to loop, bounce, or move on scroll beyond the reveal, so that the page stays calm.
33. As a manager, I want a player I traded away to count for the games he started for me, so that my performers are mine.
34. As a manager, I want an add that scored for a few games to count as a best add, so that a short stint still shows.
35. As a manager, I want a player I dropped and added again to count from the last add, so that the span is honest.
36. As a manager, I want a free agent pickup to count as an add, so that a wire move without a bid shows too.
37. As a manager, I want the grade to read my roster now, so that a trade this week shows next Tuesday.
38. As the commissioner, I want one managers file per season, rebuilt each week, so that one publish carries all twelve pages.
39. As the commissioner, I want the file built from the saved weeks, so that the first publish shows the whole season.
40. As the commissioner, I want the 0 to 100 score and the letter bands in the pipeline, so that the site never sees the number.
41. As the commissioner, I want the bands in one place, so that a change to a band is one edit.
42. As the commissioner, I want publish to copy the managers file as it copies the rankings file, so that no new step exists.
43. As the commissioner, I want a schema version on the file, so that a shape change fails the site build loud.
44. As the commissioner, I want no "Managers" entry and no links when the file is missing, so that the site ships before the file exists.
45. As the commissioner, I want the build to log one line and write no file when the history is thin, so that the Tuesday build never fails on a manager.
46. As the commissioner, I want the odds and the rank read from the rankings file, so that one number has one source.
47. As Brian, I want to read the week 7 build on the local dev server, so that I judge the page on real data before the merge.
48. As Brian, I want the feature in the week 8 build with no manual step, so that the launchd job carries it.
49. As Brian, I want two or three design passes from screenshots, so that the page earns "best-looking".

## Implementation Decisions

### The managers file, in the pipeline

- **One file per season**: `site/<season>/managers.json` with a schema version, the season, the week
  it was built through, and one entry per roster. The build writes it after the rankings file, from the
  same history. A thin history, under two saved weeks, writes no file and logs one line.
- **The entry**: the roster id, the team, the grade, the slot ranks, the points per week with the
  median and the result, the bench points, the awards shelf, the moves by week, the best adds, and the
  top performers. No odds and no power rank: those stay in the rankings file, and the site joins on the
  roster id.
- **The roster grade**: a 0 to 100 score from the analyzer's snapshot of the current week, mapped to a
  letter. The parts: each starting slot's player against the line, holes, depth above the line per
  position, and the best lineup's lineup value against the league. The bands: A+ at 90, A at 80, B at
  65, C at 50, D under 50. The score and the bands are tunables. The file carries the letter only.
- **Slot ranks**: one per position the league starts at QB, RB, WR, and TE. The team's rank, 1 to 12,
  by the sum of lineup value of its best starters at that position, with the FLEX filled by the best
  lineup. One depth word: "deep" when the team has more players above the line than slots, "fine" when
  it fills its slots above the line, "thin" when a slot is a hole.
- **Points per week**: the team's score per saved week, the league median of that week, and the
  head-to-head result. The dot marks the head-to-head game. The median game shows as the line itself.
- **Bench points**: per saved week, the best lineup from the roster's players and their real points
  minus the points of the lineup it started. The roster slots come from the current league file; they
  do not change in a season. The file carries the season total and the worst week with the player
  that sat and his points.
- **The past week model grows**: it keeps each roster's players per week and their points, read from
  the saved matchups that already hold them, as the byes feature did for the starters. No new fetch
  and no change to the saved files.
- **Moves**: per week, the adds with the bid, the drops, and the trades. The move model gains the
  drops, read from the saved transactions, which hold them. A trade shows both sides with the players
  each gave. The file carries the season totals of adds, drops, and trades.
- **Best adds**: the top three adds by points scored for the team after the add, in any number of
  games, with the projection over the same span. A free agent pickup is an add. A drop and a re-add
  counts from the last add. Ties break by the earlier add.
- **Top performers**: the top five players by points scored while started for the team, year to
  date, with the games started and the points per game started. A player traded away keeps his starts.
- **Awards shelf**: the counts of Top Scorer, Most Valuable Benchwarmer, Game Changer, and
  Underperformer from the saved facts of the weeks a report ran. A week with no report adds nothing.
- **Where it lives**: a managers module next to the power rankings module, with one pure function
  from the history, the snapshot, the league file, and the saved awards to the entries. The render
  module writes the file as it writes the rankings file. The build and the rankings command call it.
- **Publish**: the publish command copies the managers file as it copies the rankings file. A missing
  file logs a warning only.

### The site

- **Routes**: `/<season>/managers/` and `/<season>/managers/<roster_id>/`, static, one page per entry
  in the file. A season with no file has no managers routes.
- **The loader**: one loader reads the managers file for the latest season with a schema check that
  fails the build loud, and joins each entry with the last week of the rankings file for the odds, the
  rank, the record, and the moves since last week. The change in odds is the last week's playoff
  percent minus the week before, or none when the week before has no odds. A missing file is the
  empty state. The avatars come from the latest published week, as the rankings page reads them.
- **The menu**: a "Managers" entry after "Power Rankings" when the file exists, gated as the waiver
  entry is.
- **The hero**: the avatar large, the team name as the page heading, the owner, the record, and the
  standing in words: "4th of 12". Under it, three numbers in one row: the grade letter, the odds
  percent, and the power rank. One quiet line of context under each: the depth words in short form,
  the change in odds, the move in rank. No third line.
- **Chapters**: Season So Far with the points line, the bench points, and the awards shelf. Roster with
  the slot ranks. Moves by week, newest first. Best Adds. Top Performers. Each is a chapter with an id,
  and the rail lists the five.
- **The index**: twelve cards in standings order with the avatar, the name, the owner, the record, and
  the grade letter. A card is one link.
- **Links from team names**: the standings, the rankings rows, the matchup cards, and the trade cards
  render a team name as a link to the manager page when the managers file exists. The link style is
  the text with no underline and a hover underline, as the given player links in the analyzer. With no
  file the name renders as today.
- **The points line**: an inline SVG. The team line in the ink color, the median line in the mute
  color, a dot per week filled for a win and hollow for a loss. The first and the last week are the only
  axis labels. The line scales to the column width at each tier.
- **Motion**: the grade letter fades and settles with the hero timing, and the slot ranks follow at the
  reveal stagger. The odds count from zero to the percent once, over the decision timing. The points
  line draws by its path length over the reveal timing. Every one reads the motion-off switch and shows
  the final state at once with motion off. Nothing loops. Nothing moves on scroll beyond the reveal.
- **The look**: the report's look at every tier. Labels in Title Case. One quiet label per group, one
  emphasis per line, air between groups. No tag that repeats per row. The type scale and the tokens of
  the site, no new color. Both themes through the one override block.
- **Manager types**: one types file for the managers file shape, as the rankings types.

### Thin data

- Under two saved weeks: no file, one log line. A roster with no moves: an empty list per week. A
  roster with no adds: an empty best adds list, and the chapter reads "No adds yet." A week with no
  report: no awards counted. A season with no odds yet: the odds number reads "—" with no context line.

## Testing Decisions

A good test reads what a reader sees: the file, the loader's result, the rendered page. No test reads
a private helper, a class name, or a motion internal. Fixtures are built in the test with spread or
from the fixture folders, never from a published page.

### Pipeline

- **Seam 1, the build**: the build on the week 6 fixture with the fixture history writes the managers
  file. Tests read the file: twelve entries, the schema version, a grade letter in the bands, the slot
  ranks with a depth word, the moves per week, the top performers in order, and the best adds. Prior
  art: the rankings file tests in the build tests and the render tests.
- **Seam 2, the managers module**: the pure function on the fixture history and snapshot. Tests cover
  each grade band at its edge, bench points for a week with a known best lineup, a traded player's
  starts, a dropped and re-added player's span, a free agent add, a roster with no moves, and a season
  with no awards. Prior art: the power rankings tests.
- **Publish**: the publish test gains one assertion, the managers file lands in the site's public
  folder, and a missing file warns and does not fail.

### Site

- **Seam 1, the loader**: a temp public folder with the fixture managers file and the fixture rankings
  file. Tests read one manager joined with its odds, rank, and changes, the empty state with no file,
  the odds change with one week of odds, and the loud failure on a schema change. Prior art: the
  rankings loader tests.
- **Seam 2, the rendered page**: the manager page component with the fixture entry. Tests read the
  hero text, the three numbers and their context lines, the five chapter headings, the moves rows
  newest first with "No moves." for an empty week, the best adds and performers rows, and the
  motion-off path with the final state shown at once. Prior art: the Next Week and Power Rankings
  component tests, and the reduced motion tests.
- **The index and the links**: the index test reads twelve links in standings order. The standings,
  rankings, matchups, and trades tests gain one assertion each: the team name is a link with the file
  and plain text without. The masthead test gains one: the entry shows with the file and not without.

### The look

- No automated test. Brian reads the week 7 build on the local dev server at 390 by 844, 768 by 1024,
  and 1280 by 800, both themes, reduced motion on and off, and reacts to screenshots.

## Out of Scope

- Team name history. Sleeper serves no past names and the history keeps none.
- Luck, as the all-play record. Dropped in the grill.
- The power rank path across weeks, a trade ledger with verdicts, and FAAB spent and left. Later
  tickets if the page wants them.
- A writer blurb per manager. A later ticket can add one with facts and the verifier.
- A republish of week 7. The feature ships with the week 8 build.
- A change to the rankings file shape.
- Odds for weeks before week 6.

## Further Notes

- The rankings file already holds the playoff odds and the rank per week from week 6, with the bye
  odds, the seed, and the status. The hero can show the status word later with no new data.
- The saved history has weeks 1 to 7 with matchups, transactions, stats, and projections. Awards sit
  in the saved facts of weeks 6 and 7 only, so the shelf starts there.
- The saved matchups hold every player on a roster with his points, bench included, so bench points
  and the span of an add need no new fetch.
- Design passes: expect two or three. The handoff records what Brian rejected last time: a red tag
  that repeated per card and a subtitle at 0.8 of the body size. He liked one quiet label, one
  emphasis per line, and air between groups.
- The site's dev server writes an untracked `AGENTS.md`. Do not commit it. The publish command stages
  every file in the site repo, so nothing uncommitted may sit on its `main`.
- Other sessions work on both repos. Work in worktrees under the scratchpad and merge to `main` from
  the main checkout with `--no-ff`.
