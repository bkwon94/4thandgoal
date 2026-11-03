# Cornerstone Weekly: design

Date: 2026-10-20
Status: draft, waits for Brian's approval
Mockups: `~/plans/cornerstone-weekly-mockups/phone-week6-v4.html` is the approved page shape. `layout.html` shows the three structures we compared.

## Intent

Sleeper's Tuesday report shows top scores and little else. Brian wants a weekly report for the Cornerstone League that tells the story of the week: the matchup that mattered, the player that swung a game, the awards, the standings, and a look at next week. Every number must be right. Every claim must trace to data. The tone is dry and a little mean, with the numbers doing the work.

The result is a static website with one page per week and a shareable link. League mates open it on a phone.

## Goals

1. Publish one page per NFL week at a stable public URL.
2. Make every fact on the page true to the Sleeper data for that week.
3. Write blurbs in Claude's voice from a computed fact sheet, with humor, with team names.
4. Keep the Tuesday job to one command plus a two-minute skim by Brian.
5. Match the Cornerstone Presbyterian Church brand: black, red, light gray, white, the logo in the masthead.

## Non-goals

- No live scores or mid-week updates. The page is a Tuesday snapshot.
- No user accounts, no comments, no app.
- No playoff odds in version 1. That needs a simulation and waits.
- No playoff weeks in version 1. See Scope decisions.
- No auction values or draft recap. Sleeper's public API does not give auction values.

## Anti-goals

These make the project a failure even if it runs.

- A blurb that states a cause the data does not support. Example from the mockup review: "decided by a quarterback" when the quarterback was on the losing team.
- A blurb that uses a loose word for a defined stat. "Best starter" is not a stat. "Top scorer" is.
- A page that publishes without Brian's approval.
- A fact that comes from Claude instead of code.

## Constraints

- League: Cornerstone League 2026, Sleeper league ID `1386167364424318976`, 12 teams, half PPR, 4-point passing touchdowns, 6 playoff teams, playoffs start week 15.
- The league plays against the median. Every week gives each team two results: one against the opponent, one against the league median score. Season records count both.
- The build runs on Brian's Mac. Brian's Mac is available on Tuesdays.
- Publish target is GitHub Pages under the GitHub user `bkwon94`, from a public site-only repo. Source stays in a private repo. `gh` is logged in on this Mac.
- Claude calls go through the Anthropic Python SDK with the key already in Brian's environment. The key never leaves the Mac.
- Sleeper's projections, stats, and news endpoints are unofficial. The build must degrade when one breaks. See Data.
- House style for all prose, code comments, and docs is Simplified Technical English. Blurbs are exempt. They are the product.

## The page

One column, phone first, scrolls like a story. Chapters alternate light and dark. The approved mockup is the reference for layout, spacing, and color. This list is the contract.

1. **Masthead.** Logo, "Cornerstone League Weekly", the week number large with the number in red, the date range of the NFL week, the publish date.
2. **Matchup of the Week.** A tag with the reason it was picked. Both team avatars, names, and scores, loser's score in red. A blurb of four to six sentences.
3. **Game Changer.** One player: name, position, NFL team, fantasy team, points, projection. A blurb of three to five sentences.
4. **Awards.** Four tiles: Top Scorer, MVB (Most Valuable Benchwarmer), Underperformer, Overachiever. Each tile has the player, the points, and one line of context. One blurb of two to four sentences under the tiles.
5. **All Matchups.** Six rows. Each row has both team avatars and the winner in red with both scores and a full-width "Read recap" button. The button opens a panel with a slide animation. The panel shows each team's top scorer and a blurb of two to three sentences. The button reads "Hide recap" while open. The Matchup of the Week row has a short blurb that points to the top of the page.
6. **The Median Game.** Three numbers: the median, the closest team above it, the closest team below it. A bar per team sorted by score, red above the median, gray below, with a dashed median line. A blurb of two to four sentences.
7. **Standings.** Rank, avatar, team, record, points for. Brian's team is marked. A dashed line marks the playoff cut after sixth place. One line under the table explains the median game.
8. **Next Week.** Every matchup for the coming week with avatars and records. One or two are tagged "Must Watch" with a one-line reason.
9. **Footer.** "Cornerstone League 2026 · Built from Sleeper data".

Each season also has a home page. It lists every published week, newest first, with the week number, the dates, and the Matchup of the Week teams. The home page is the shareable link that never changes.

### Branding

Colors: black `#141414`, red `#b8342a`, light gray `#ececec`, white. The logo is at `~/plans/cornerstone-weekly-mockups/logo.png`: a black circle with a white and red house shape, a vertical rule, then the church name. The masthead uses the circle mark and the wordmark on black.

Team avatars come from Sleeper. Seven of the twelve teams set a custom one. The rest fall back to the manager's user avatar. Every team ends up with an image. Render them as small circles next to the team name.

### Tone

Dry, specific, a little mean, numbers in every sentence. Roast losers by team name. No profanity. No jokes about real-world injuries. The humor comes from the facts, like a team named To Infinity and Bijan whose Bijan scored 6.3.

## Data

All data comes from the Sleeper API. Confirmed by real pulls on 2026-10-20.

| Need | Endpoint | Notes |
| --- | --- | --- |
| NFL week and season | `GET /v1/state/nfl` | `display_week` is the last scored week. `season_start_date` gives the week's dates. |
| League settings | `GET /v1/league/{id}` | `league_average_match: 1` confirms the median game. Playoff settings, roster slots, scoring. |
| Teams | `GET /v1/league/{id}/users` | `metadata.team_name` is the team name. `display_name` is the fallback. |
| Avatars | same `users` call | `metadata.avatar` is a full URL when the team set one. Else `https://sleepercdn.com/avatars/thumbs/{avatar}` from the user's `avatar` field. Download once per build into the site folder. |
| Records and rosters | `GET /v1/league/{id}/rosters` | Wins, losses, points for, full player list. |
| Weekly scores | `GET /v1/league/{id}/matchups/{week}` | Per team: starters, bench, points per player, `matchup_id` pairs the two sides. |
| Moves | `GET /v1/league/{id}/transactions/{week}` | Waivers, free agents, trades, with the week they happened. |
| Player names | `GET /v1/players/nfl` | 5 MB. Cache to disk, refresh once a week. |
| Projections | `GET /projections/nfl/{season}/{week}?season_type=regular&position[]=...` | Unofficial. `stats.pts_half_ppr` per player. |
| Weekly stats | `GET /stats/nfl/{season}/{week}?season_type=regular&position[]=...` | Unofficial. Box score lines per player. |
| Player news | `GET /players/nfl/{player_id}/news` | Unofficial. Short text items, used only as context for Game Changer. |

Unofficial endpoints have fallbacks:

- Projections down: Underperformer and Overachiever switch to "versus season average". The page says which one it used.
- Stats down: blurbs lose box score detail. No chapter is lost.
- News down: Game Changer uses only the transaction and points data.

The build saves every raw response under `data/{season}/week-{NN}/raw/`. A rebuild of a past week reads from disk and never refetches.

## Pipeline

One command, `cornerstone build`, runs these steps in order. Each step writes a file. A later step can run alone from the files of the earlier steps.

1. **Fetch.** Pull every endpoint above for the last scored week. Write raw JSON.
2. **Facts.** Compute the fact sheet. Write `facts.json`. No Claude call in this step.
3. **Write.** Call Claude once per chapter that has a blurb. Write `blurbs.json`.
4. **Verify.** Check every blurb in code, then with a second Claude call. Rewrite or fall back. Write `verify.json`.
5. **Render.** Build the week page and the home page from templates. Write to the site folder.
6. **Preview.** Open the week page in the browser. Send a macOS notification. Stop.

Brian reads the page. Then:

7. **Publish.** `cornerstone publish` commits the site folder and pushes. GitHub Pages serves it within a minute. Nothing reaches GitHub before this command.

A fix after the skim: `cornerstone rewrite --chapter matchup-4` regenerates the blurbs for one chapter and re-renders. Then publish again.

## The fact sheet

The fact sheet is the only input Claude sees. Every fact has an ID. Every fact is computed in code from the raw data. Definitions below are the vocabulary. Claude gets these definitions in the prompt and may use only these terms.

Per week:

- `week`, `dates`, `median`, `publish_date`.
- Standings: rank, team, record, points for, playoff position, games above or below the cut.
- Median results: per team, score, gap to median, win or loss.

Per matchup:

- Winner, loser, both scores, margin.
- Top scorer per side: the starter with the most points.
- Every starter per side: name, position, NFL team, points, projection, gap to projection, season average.
- Margin drivers: every player on either side whose absolute gap to projection is at least the margin. These are the only players a blurb may call a decider.
- Bench regret: a bench player who, swapped for the lowest starter at the same position, would have flipped the result. Same-position swaps only.
- Recent moves: any starter added by waiver, free agency, or trade in this week or the week before, with the move type and the week.
- Records after this week for both teams, and each team's playoff position after this week.
- Swing players: every player on the winning side whose points exceed the margin. A blurb may say "without X, that is a loss" only for a swing player.

League-wide:

- Top Scorer: the starter with the most points, all teams.
- MVB: the bench player with the most points, all teams.
- Underperformer: the starter with the largest gap below projection, among starters projected at 10 or more.
- Overachiever: the starter with the largest gap above projection.
- One player holds one spot. Pick in this order: Game Changer, Top Scorer, MVB, Underperformer, Overachiever. Each pick skips players already picked and takes the next best. The fact sheet records each pick and the skip. Recap top scorers inside All Matchups may repeat any player.
- Game Changer candidates: every starter on a winning side whose points exceed the margin, ranked by gap to projection, with a bonus for a recent move. The top one is the Game Changer. The fact sheet records why.
- Matchup of the Week: every matchup scored on four signals, closest margin, biggest upset by standing, highest combined standing, and nearness to the playoff cut. The top score wins. The fact sheet records the reason as one of "Closest Finish", "Upset", "Top of the Table", or "Playoff Stakes". The builder sets the weights. Ties go to closest margin.
- Next week: every matchup with records. Must Watch is the top one or two by the same four signals, computed from records and standings only.
- Remaining schedule strength per team: mean opponent win rate over the weeks left before the playoffs, with the league rank of that number.
- Position ranks: every starter's rank among all starters at the same position this week.
- Season history: per team, the season high and low total, the count of weeks over 100, 110, and 120, and whether this week set a new high or low. Per week, the league high and low total so far this season.

Not on the sheet, and so not in any blurb: playoff odds, streaks longer than the data on hand, anything about a player's real-life situation beyond the news items.

## Blurb accuracy

Four layers. None is optional.

1. **Facts in code.** Claude never computes. The fact sheet is complete before the first Claude call.
2. **Citations.** The writer prompt requires a fact ID after every sentence, like `[M4.3]`. The render step strips the IDs. A sentence with no ID fails. An ID that does not exist fails.
3. **Checks.** In code: every number in a blurb appears in the cited facts, every team name is a league team, every player name is on one of the rosters involved, every stat term is from the vocabulary. Then a second Claude call reads the fact sheet and the blurb and marks each sentence supported or unsupported with a reason.
4. **Fail soft.** An unsupported sentence sends the whole blurb back to the writer once, with the verifier's reason attached. A second failure replaces the blurb with a template sentence built from facts, like "behold the lamb beat Bo Girds 114.95 to 109.61." A boring sentence beats a wrong one. The page marks nothing. The log records it.

Every week's fact sheet, prompts, blurbs, and verifier output stay on disk under `data/{season}/week-{NN}/`.

## Claude calls

- Model: `claude-opus-5-5` for both the writer and the verifier. About 12 blurbs a week. Cost is cents.
- Writer: one call per chapter. Input: the vocabulary, the tone guide, the fact sheet slice for that chapter, the citation rule. Output: structured JSON with the blurb text. Use structured outputs so the parse never fails.
- Verifier: one call per blurb. A separate prompt with no instruction about tone. Output: structured JSON, one verdict per sentence.
- Adaptive thinking on, effort high. Include the server-side refusal fallback as the SDK guide recommends.
- Prompts live in files, not in code, so Brian can tune the voice without a code change.

## Publish

- Two repos. The source repo is private. The site repo is public and holds only the built HTML.
- Source: `~/repos/cornerstone-fantasy-sleeper-weekly-report`, GitHub `bkwon94/cornerstone-fantasy-sleeper-weekly-report`, private. Code, prompts, templates, raw data, fact sheets, blurbs, and tests live here.
- Site: `~/repos/cornerstone-fantasy-sleeper-weekly-report-site`, GitHub `bkwon94/cornerstone-fantasy-sleeper-weekly-report-site`, public. GitHub Pages serves `main` from the repo root.
- The build writes into `site/` inside the source repo. `cornerstone publish` copies `site/` over the site repo checkout, commits, and pushes.
- URL shape: `https://bkwon94.github.io/cornerstone-fantasy-sleeper-weekly-report-site/` for the home page, `/2026/week-06/` for a week.
- Nothing secret is in either repo. The API key stays in Brian's shell environment.
- No GitHub Actions. The Mac builds, GitHub only serves.

## Schedule

- A launchd job runs `cornerstone build` every Tuesday at 8:00 local time. It follows the pattern of the existing jobs in `~/repos/scripts/launchagents/`.
- The job ends with a preview in the browser and a notification. It never publishes.
- If the Mac is asleep or the job fails, Brian runs `cornerstone build` by hand. Same result.
- "Final" means `league.settings.last_scored_leg` equals the target week. Sleeper sets it when the week's games are done. If it is behind, the build stops and says so. The launchd job does not retry. Brian reruns by hand.
- The Tuesday page is a snapshot. Later stat corrections from Sleeper do not trigger a rebuild. A published week changes only when Brian runs a rebuild on purpose.

## Decided by Brian

- Scroll story layout, phone first.
- Chapter list and order above.
- "Read recap" as a full-width button per matchup, slide animation.
- The Median Game chapter.
- Tone: dry, numbers first, roast by team name, a little more humor than the first draft.
- Local build on his Mac, every Tuesday.
- Publish only after his approval.
- Cornerstone church brand colors and logo.

## My calls

Each of these is a default Brian can override.

- Python 3.11 with `uv`, matching `~/repos/scripts`. Jinja2 templates. One CSS file. A few lines of plain JavaScript for the recap buttons. No framework.
- Private source repo plus a public site-only repo for GitHub Pages.
- `claude-opus-5-5` for both Claude calls.
- The four-signal scoring for Matchup of the Week and the "exceeds the margin" rule for Game Changer.
- Projection threshold of 10 points for Underperformer, so a kicker-sized projection never wins the award.
- 8:00 Tuesday local time.
- Raw data committed to the repo.

## Left to the builder

- Exact weights in the four-signal scoring.
- Prompt wording for writer and verifier.
- CSS details beyond the mockup. The mockup is the reference, not pixel law.
- How the launchd job gets the API key. The existing jobs show the pattern.
- The CLI framework, if any.
- Template structure.

## Scope decisions

Settled with Brian on 2026-10-20.

1. **First page is week 6.** It recaps week 6 and previews week 7. Version 1 reads records straight from the rosters endpoint. Weeks 1 to 5 are a backfill after launch, which adds an "as of week N" layer that recomputes standings from matchup history.
2. **Regular season only.** Version 1 covers weeks 6 to 14. A build for week 15 or later stops with a clear message. A playoff chapter set is version 2 and ships before week 15.
