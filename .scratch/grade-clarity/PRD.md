# Grade clarity: a trade grade that a manager reads in under a minute

Status: ready-for-agent
Date: 2026-11-04
Apps: both. The pipeline packages `league` and `analyzer` change the rank measure, the facts, the prompt, the checks, and the result document. The API serves the new document. The site renders the new result view of layout A.
Spec branch: `grade-clarity`.
Source: the map `.scratch/grade-clarity/MAP.md` and decision tickets 01 to 05. ADR 0003, ADR 0004, ADR 0009.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

A manager opens the analyze route and gets a grade that takes minutes to read. Each side has a paragraph of three to five sentences, then "The Data", then seven adjuster rows that all show. The rows say "one step up" and "no step", and they use inner words such as "trade value", "the line", "hole", and "best lineup". The as-of line names the chart week. The manager cannot see fast why a side wins or loses.

The manager also cannot trust some numbers. The grade ranks a player by his points per game over his last 4 games. One big game in a short window moves a player about 40 spots. Omar Cooper Jr. reads as WR18 in the grade, while Sleeper shows him at WR60. The slot fact says "takes RB1" or "sits on the bench", and that does not match the lineup the manager sets.

The grade says nothing about this week. A contender wants to know who plays in the trade week and the next week, who has a bye, who is Out, and who steps up when a starter is out.

## Solution

The result view leads with the decision and one "why" sentence. Each side gets one card with its players, 2 or 3 short bullets, and a Week line for the trade week and the next week. The adjuster rows sit in one closed fold for each side. A row that says nothing hides, and each row is one plain sentence with a mark.

Each rank in the text is the Season rank, as Sleeper sorts it. A Recent rank shows beside it, with its label, only when the two differ by a large gap. The Position rank inside the grade sorts by season points per game, so one big game no longer moves a player 40 spots.

The Week line counts, for each position the trade touches, the players of the side who play that week, are not out, and rank above the line. It names each bye, each player who is Out or on IR, each player who steps up, and the opponent with its rank at the position. It never moves the letter. The verdict can name it.

No text names the value chart or another inner part of the grade.

## User Stories

1. As a manager, I want the decision and one "why" sentence at the top, so that I know the answer before I read more.
2. As a manager, I want the trade card under the decision, so that I see who goes where.
3. As a manager, I want one card for each side, so that I read one side at a time.
4. As a manager, I want my own side marked "Your Side", so that I find it fast.
5. As a manager, I want each side card to show the players the side gets and gives, with a headshot, the position, and the NFL team, so that I know each player.
6. As a manager, I want each player to show his Season rank, such as WR60, so that the number matches Sleeper.
7. As a manager, I want a Recent rank beside the Season rank only when the gap is large, with its label, so that I see a hot or cold player without noise.
8. As a manager, I want 2 or 3 short bullets for each side, so that I read the case in seconds.
9. As a manager, I want each bullet to make one claim in plain words, so that I do not parse a paragraph.
10. As a manager, I want a "This week and next" box on each side card, so that I see the effect on my next two games.
11. As a contender, I want the Week line to count my players above the line who play at each position the trade touches, before and after the trade, so that I know if my lineup gets weaker this week.
12. As a manager, I want the Week line to name each player with a bye that week, so that I am not caught short.
13. As a manager, I want the Week line to name each player listed Out or on IR, so that I see who cannot play.
14. As a manager, I want the Week line to name a player who steps up because the player ahead of him is out, so that I see a short-term gain.
15. As a manager, I want the Week line to name the opponent of each player the side gets, with its rank at the position, so that I see if the matchup is soft or hard.
16. As a manager on a Tuesday or a Wednesday, I want the text to say "listed Out last week", so that I know the status is from the last game.
17. As a manager, I want no step-up named when the depth chart is old, so that I never act on a stale depth chart.
18. As a manager, I want the Week line to never change the letter, so that the grade of the season stays stable.
19. As a manager, I want the verdict to be able to name the Week line, so that a contender hears about this week when it matters.
20. As a manager, I want the adjuster rows in one closed fold under the Week line, so that the card stays short.
21. As a manager, I want the fold summary to say "How the grade adds up" with the count of rows, so that I know what opens.
22. As a manager, I want a row that says nothing to hide, so that I read only rows that matter.
23. As a manager, I want each row to show its effect as a mark, up, down, or even, so that I do not read "one step up".
24. As a manager, I want each row to be one short sentence in a manager's words, so that I understand it at once.
25. As a manager, I want the deal row to say how much I get against what I give, with no source named, so that I see the start of the grade in plain words.
26. As a manager, I want the roster row to count my players in the top N at each position before and after, so that I see the depth change as a plain rank.
27. As a manager, I want the standing row to say my race, my need, and if the trade meets it, so that I see why the grade fits my team.
28. As a manager, I want the usage row to give the snap share, the target share, the air yards per target, and the carry share by position, so that I see the role of each player.
29. As a manager, I want the injury row to say the return week and the count of weeks on the injury report, so that I see the risk.
30. As a manager, I want the upside row in plain words, such as "gets more work while Pollard is out", so that I see the bet.
31. As a manager, I want the handcuff row to name the starter that the player backs up, so that I see the insurance.
32. As a manager, I want the schedule row to name each playoff opponent with its rank at the position, so that I see the playoff matchups.
33. As a manager, I want the as-of line to stop at the stats and the fetch time, so that it names no chart.
34. As a manager in a week with no values yet, I want the note "This week's player values are not out yet, so both sides start even.", so that I know why the grade starts even.
35. As a manager, I want no text to say "trade value", "best lineup", "the line", "hole", "star", or the other inner words, so that the grade reads as plain advice.
36. As a manager, I want no text to say "takes RB1" or "sits on the bench", so that the grade never claims my lineup.
37. As a manager, I want a player with a few big games to rank by his season points per game inside the grade, so that a small sample does not swing the letter.
38. As a manager, I want a cached grade to change when the depth chart or a status changes, so that a Week line is never stale.
39. As a manager on a phone, I want the two players of a side to stack, so that each fits the width.
40. As a manager on a tablet or a desktop, I want the two players of a side side by side, so that the card is short.
41. As a manager, I want a trade of three or four sides to show one card for each side in the same form, so that every trade reads the same.
42. As a manager who uses the trade finder, I want its facts to use the same Season rank and the same plain words, so that the numbers match the grade.
43. As Brian, I want the weekly report to keep its own Position rank, so that this spec changes the grade only.
44. As Brian, I want the gap of the Recent rank in `tunables.py`, so that I can tune it.

## Implementation Decisions

### The rank measure

- The Position rank inside the grade sorts by season points per game, games played only. Decision 01.
- The `league` package gives this measure next to the 4-week measure. The grade, the finder, roster fit, and the best lineup that the grade reads use the season measure.
- The weekly report and the manager grade keep the 4-week measure. Their packages `week` and `managers` read the same rank code today, so the change must not reach them.
- The due-back step and the out-for-season step of the lineup value stay.
- `GLOSSARY.md` changes "Lineup value" and "Position rank" to say that the grade reads season points per game.

### The ranks in the text

- The text of a grade shows the Season rank: the place at the position by total points this season, as Sleeper sorts it, such as WR60.
- The Recent rank is the place at the position by points per game over the last 4 games.
- **Decision 05:** the Recent rank shows only when it differs from the Season rank by 12 spots or more. The tunable is `RECENT_RANK_GAP = 12` in `tunables.py` of the analyzer. One number holds for every position.
- The facts of a traded player give the Season rank in the form "WR60", and the Recent rank with its label when the gap holds. The facts no longer give the Position rank as a number.
- Each player in the result document carries `season_rank` and `recent_rank`. `recent_rank` is null when the gap does not hold.

### The facts

- The slot fact goes. No fact says "takes RB1" or "sits on the bench". The best lineup stays inside the code as a measure of depth.
- A Week line fact for each side holds the text of its Week lines, so the verdict and the bullets can name it.

### The Week line

- The code writes each Week line. Claude does not write it.
- Each side gets one Week line for the trade week and one for the next week.
- For each position the trade touches, the line counts the players of the side who play that week, are not out, and rank above the line by the Position rank. It gives the count before and after the trade. It assigns no lineup slot.
- The line names each bye, each player who is out, each player who steps up, and the opponent of each player the side gets with its rank at the position. Example: "Week 9: Washington plays at TEN, 3rd most points to WRs." The rank is the points allowed per game at the position. Rank 1 gives up the most.
- **Out:** Out counts for the trade week only. IR, PUP, NA, and Sus count for both weeks. Out for the season, and a return week in the Returns file after the next week, count for both weeks. Questionable and Doubtful never count. Decision 02.
- On a Tuesday and a Wednesday, the text says "listed Out last week".
- **Steps up:** a player steps up for a week when the player directly ahead of him on his NFL team's depth chart, at his position, is out for that week. QB, RB, WR, and TE only.
- The rule reads the full Sleeper players file, because the player ahead is often on no roster.
- `read_depth_charts` gives back the newest `dt` with the charts.
- The Week line names no step-up when the newest `dt` is more than 48 hours before the grade.
- The Week line shows for every side. ADR 0004 still holds for the roster fit adjuster. The race of the side weighs the Week line in the verdict only.

### The adjuster rows

The form of each row comes from decision 03:

1. A row shows only when it moves the grade or says something new. The code drops a row that says nothing from the document.
2. The mark shows the step. The text never says "one step up" or "no step".
3. Each row is one short sentence. The text never says "trade value", "highest-value", "best lineup", "the line", "hole", "win-now move", "return bet", "star", or "opportunity". "The better player" replaces "the highest-value player".

The rows and their page names:

- **The deal:** the start letter, such as "You get far more than you give." It names no source. It replaces "The Data".
- **Roster:** "You keep 3 WRs in the top 36, and you get the better player."
- **Standing:** "Out of the playoff race, so you want the better player for the rest of the season, and you get him."
- **Usage:** one clause for each player, with the numbers and no weeks. WR and TE give the snap share, the target share, and the air yards per target. RB gives the snap share, the carry share, and the target share. QB gets no usage row.
- **Injury:** "Cooper is out until week 11. He was on the injury report in 5 of 8 weeks."
- **Upside:** "Spears gets more work while Pollard is out."
- **Handcuff:** "Spears backs up your RB, Pollard, on the Titans depth chart."
- **Schedule:** the players, the byes after the Week line, and each playoff opponent with its rank at the position. The sentence "The schedule leans for this side" goes.

The expected gap row stays off.

### The value chart

- "Chart week N" leaves the as-of line.
- The note for a week with no values reads "This week's player values are not out yet, so both sides start even."

### The Claude call

- Each side gets `bullets`, a list of 2 or 3 strings, in place of `analysis`. Each bullet is one sentence.
- The checks of the prose apply to each bullet: the numbers, the names, no letter, and no upside claim without the upside adjuster.
- A new check rejects each banned word of decision 03 in a bullet and in the verdict reason. The prompt lists the same words.
- Rule 10 of the analysis prompt goes. It tells Claude to say "position rank", "the line", and "hole", which decision 03 bans.
- The verdict reason is the one "why" sentence. It can name the Week line.
- The fallback, when the call fails twice, shows no bullets. The Week line and the rows still show.

### The result document

- Each side holds `bullets`, `week_lines` as a list of `{week, text}`, and `factors` with the rows that show only.
- The chart sentence moves into the factors as the deal row.
- Each player of `trade.sides` carries `season_rank` and `recent_rank`.
- `DOCUMENT_VERSION` goes up by one.

### The result cache

- The key holds the newest depth chart `dt` and a hash of each status that a Week line reads, including players on no roster. Without them, a cached grade keeps a stale Week line. Decision 02.

### The result view: layout A

Brian picked layout A on 2026-11-05. Decision 04.

The view is one column at each width. The parts, in this order:

1. The decision chapter: the label "Decision for <team>", the answer as the headline, and the "why" sentence. The no-values note and the fairness line stay under it as now.
2. The trade chapter: the swap card as now.
3. One chapter for each side. Its label is the team, plus " · Your Side" for the side of the manager.
4. The last chapter, with the as-of line.

Each side chapter shows these parts before a tap:

1. The player the side gets and the player the side gives. Each has a headshot, the name, the position and the NFL team, and the Season rank. The Recent rank follows only when it shows.
2. The 2 or 3 bullets.
3. A box "This week and next" with the two Week lines.

The fold is a closed `details` under the Week lines. Its summary reads "How the grade adds up · <n> rows". It holds the rows, each with its mark. On a tablet and wider, the two players of a side stand next to each other. On a phone, they stack. The sides never stand next to each other.

The view reads no query string. A prototype found that `useSearchParams` can keep the server fallback after hydration in this static export.

## Testing Decisions

A good test checks what the manager or the API caller sees: the result document, the rendered view, and the text. It does not check a private function or the order of calls.

The seams, from the highest down:

1. **The analyze route.** A request in, a result document out, on a snapshot of real saved data and the existing fake Claude call (ADR 0015). Most tests sit here: the bullets, the Week lines, the hidden rows, the Season rank, the Recent rank and its gap, the banned words, the as-of line, the no-values note, the fallback, and the cache key. Prior art: `apps/api/tests/test_api.py` and `apps/pipeline/tests/test_analysis.py`.
2. **The rubric.** The grade of a trade, for the rank measure and the step-up rule, where the route would hide the cause. Prior art: `apps/pipeline/tests/test_rubric.py` and `apps/pipeline/tests/test_snapshot.py`.
3. **The result view.** `AnalyzeResult` rendered from a document: the order of the parts, the closed fold, the Week line box, the ranks, and the stacked players at the phone width. Prior art: `packages/analyzer/site/form/analyze-result.test.tsx`.

Brian checks these seams with the spec.

Two guards:

- The weekly report and the manager grade give the same ranks before and after the change. Prior art: `apps/pipeline/tests/test_manager_grade.py`.
- The finder still returns trades on the same rosters, with the new facts. Prior art: `apps/pipeline/tests/test_finder.py`.

## Out of Scope

- The prompt and the view of the trade finder. The goal is about the grade, and only `norcal` turns on the finder. The finder gets the shared fixes of the facts.
- The Position rank of the weekly report and of the manager grade. Those pages have their own readers.
- A Week line past the next week. The letter already grades the rest of the season.
- Route share in the usage row. No cached nflverse file holds routes.
- The expected gap row. Its adjuster is off in the code.
- An audit of the other numbers of a grade. Brian sees no other wrong number now.
- The suggested counters. The slot stays as now.

## Further Notes

- Decision 05 sets the gap at 12 spots for every position. 12 spots is half the line at QB and TE, and a third at RB and WR. Omar Cooper Jr. shows the gap: WR60 by the Season rank, WR18 by the Recent rank.
- Layout A in the prototype had no fairness line and no counters slot. This spec keeps both as now. Brian can cut either one in the review of the spec.
- The Week line counts "above the line" by the Position rank, season points per game. The text shows the Season rank, total points. A player can be inside the line in the count and outside the top 36 by the Season rank. The prototype of decision 04 counted the same way.
- The nflverse injury file holds a game status for the trade week only from the Friday report on. The spec reads the Sleeper status only. A later spec can confirm Out with the Friday report.
- The `--no-claude` analyze run of the Makefile still calls Claude to read the value chart. A test needs the saved chart.
