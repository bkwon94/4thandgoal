# Analyzer: multi-team trades, select pickers, and the upside adjuster

Status: ready-for-agent
Date: 2026-10-27

This feature spans two repos. The pipeline repo `cornerstone-fantasy-sleeper-weekly-report` owns
the API, the rubric, and the prompt. This repo owns the form and the result. The pipeline work
lands first and ships a three-side fixture that the site tests read. The terms come from
`GLOSSARY.md` in each repo. The house rules are this repo's
`docs/adr/0008-a-given-player-names-its-destination.md` and the pipeline repo's
`docs/adr/0005-out-for-the-season-counts-zero-chart-value.md`.

## Problem Statement

A league member opens the trade analyzer with a three-team trade in mind and finds no way to enter
it. The form holds two sides, the API grades exactly two, and the prompt asks the model for exactly
two. The form itself reads as 24 identical team rows before a pick, two full lists of twelve, and
then two full player lists, so even a two-team trade is a long scroll. The grade also misses what a
manager calls upside. A star out with no return week counts against the side that gets him, when
that side trades for his return. A player with a role that just opened, because his teammate is
out for the season, gets no credit beyond his share trend. A player out for the season still
carries his full chart value, so the side that trades for him reads fair when it is not.

## Solution

The analyze route takes two to four sides. Each given player names its destination, so a three-
or four-team trade is one request, graded as one. The decision stays for the asker, the letter per
side stays the same ratio, and the fairness runs the same rule over every side. The form replaces
the two team lists and the two player lists with one Select per side for the team and one
multi-select per side for the players. The picked players show as rows under the picker, each with
a To picker once the trade has three or more sides. A reader adds a third and a fourth side with
one button and removes one with one control. The result keeps the arrow swap card for two sides and
renders one row per side, with from and to tags, for three or more. The rubric gains an upside
adjuster that steps a side up for a star return bet or an opportunity. A player out for the season
counts zero chart value for the side that gets him, and the injury adjuster steps that side down.
The returns file marks him with `season`.

## User Stories

### The trade shape, on the API

1. As a manager, I want to send a trade with three or four sides, so that the analyzer grades the whole trade as one.
2. As a manager, I want each given player to name the roster he goes to, so that a three-team trade is unambiguous.
3. As a manager, I want a two-team trade to use the same shape, so that one request shape works for every trade.
4. As a manager, I want the API to reject a side that gives nothing or gets nothing, so that a non-party cannot pad a trade.
5. As a manager, I want the API to reject a fifth side, so that the grade stays readable.
6. As a manager, I want the API to reject a destination that is not a side of the trade, so that a typo does not grade.
7. As a manager, I want the API to reject a player given to his own roster, so that a no-op move does not grade.
8. As a manager, I want the API to reject a player who appears twice, so that one player cannot go two places.
9. As a manager, I want the asker to be one of the sides, as today, so that the decision has a side.
10. As a site developer, I want the response to carry `to` on each given player and `from` on each got player, so that the swap card can tag players with three sides.
11. As a site developer, I want the response's `trade.sides`, `fairness.sides`, and `sides` to list every side in request order, so that the page joins them by roster id as today.

### The grade with many sides

12. As a manager, I want each side's letter to stay the ratio of what it gets over what it gives, so that a three-team grade reads like a two-team grade.
13. As a manager, I want the decision to stay for the asker only, so that the lead answer is still mine.
14. As a manager, I want the fairness to read win-win when every side clears the bar, so that a good three-team trade says so.
15. As a manager, I want the fairness to read lopsided and name the one side that gives more, so that a bad three-team trade names its loser.
16. As a manager, I want each side's read to see what it gets, what it gives, and which side each player comes from or goes to, so that the analysis speaks to the real move.
17. As a manager, I want the model to return exactly as many sides as the trade has, in order, so that no side is skipped or doubled.
18. As a manager, I want the adjusters to read a side's gets and gives with no care for the source, so that the rubric does not change for three sides.

### The upside adjuster

19. As a manager, I want an upside adjuster in the rubric, so that the grade credits potential and not only the chart.
20. As a manager, I want upside to step a side up or not at all, never down, so that the lack of upside is not a penalty.
21. As a manager, I want upside to read the players a side gets only, so that the side that gives a star return bet is not credited for him.
22. As a manager, I want a star to be a player in the top STAR_RANK of the chart, so that "star" has one meaning.
23. As a manager, I want a star who is out now and not out for the season to count as a star return bet, so that a trade for his return reads as the bet it is.
24. As a manager, I want the star return bet to count even when he has no return week, so that a missing timetable is not a penalty.
25. As a manager, I want the injury adjuster to leave a star return bet alone, so that upside and injury do not cancel each other.
26. As a manager, I want a player whose same-position teammate is out for the season, or out with no near return, and whose use points up, to count as an opportunity, so that an opened role reads as upside.
27. As a manager, I want the up signals to be snap share, target share, air yards share, and WOPR, so that a WR or TE with more air yards reads as up.
28. As a manager, I want a QB's up signals to skip snap share, so that a QB does not read as up for a snap count that never moves.
29. As a manager, I want the upside reason to name the player and the signal, so that I can check the claim.
30. As a manager, I want the upside factor to show on the result page as a factor like the rest, so that I see it with the other reads.
31. As a manager, I want the prompt to name the upside among what the model covers, so that the side read speaks to it.

### Out for the season

32. As the commissioner, I want to mark a player out for the season with the word `season` in the returns file, so that one edit tells the analyzer.
33. As a manager, I want a player out for the season to count zero chart value for the side that gets him, so that the start letter shows the loss.
34. As a manager, I want the side that gives him to keep his full chart value, so that the fairness reads lopsided on its own.
35. As a manager, I want the injury adjuster to step the side that gets him down with the reason "Name is out for the season.", so that the reason is plain.
36. As a manager, I want a player out for the season to count as no star return bet and no opportunity, so that upside never credits him.
37. As a manager, I want the IR status alone not to mean out for the season, so that a player due back from IR still reads as a return bet.

### The form: team pickers

38. As a reader, I want one Select per side for the team, with the avatar and the team name in each row, so that I pick a team from a short list and not a wall of rows.
39. As a reader, I want the first side labeled "Your Team", so that I know which side is mine.
40. As a reader, I want the asker to be the first side always, so that the decision is for my team.
41. As a reader, I want a team picked on one side to be absent from the other sides' pickers, so that one team cannot be two sides.
42. As a reader, I want the team picker trigger to show the picked team's avatar and name, so that the pick is visible after the list closes.
43. As a reader, I want a new team on a side to clear that side's picks and the result, so that a stale result never sits under a new trade.
44. As a reader, I want the pickers to lock while a grade runs, so that the result matches the trade on the screen.

### The form: player pickers

45. As a reader, I want one multi-select per side for the players it gives, labeled "<Team> Gives", so that the pick of players matches the pick of teams.
46. As a reader, I want the player picker trigger to read "Pick Players" when empty and the count, such as "2 Players", when not, so that I see the state at a glance.
47. As a reader, I want each row of the player list to show the headshot, the name, the position, and the NFL team, so that I pick the right player.
48. As a reader, I want the picked players to show as rows under the trigger, so that the trade is visible with the list closed.
49. As a reader, I want a remove control on each picked row, so that I can drop a player without the list.
50. As a reader, I want a failed headshot to swap to the default image, as today, so that a row never shows a broken image.
51. As a reader, I want a player picker to show only after its side has a team, so that the form reads top to bottom.

### The form: sides

52. As a reader, I want an "Add a Team" button after the last side, so that I can enter a three- or four-team trade.
53. As a reader, I want the button to show only when every side has a team and the trade has fewer than four sides, so that I fill one side before I open the next.
54. As a reader, I want a remove control on the third and fourth sides, so that I can go back to a two-team trade.
55. As a reader, I want the first two sides to have no remove control, so that a trade always has two sides.
56. As a reader, I want a removed side's players to leave the trade, and the players sent to it to fall back to the default destination, so that the form stays valid.
57. As a reader, I want the grade button on until every side gives and gets at least one player, so that I cannot send a trade the API rejects.
58. As a reader, I want the finder to hide once the trade has a third side, so that a two-team tool does not sit under a three-team trade.
59. As a reader, I want a trade opened from a finder card to fill two sides as today, so that the finder still works.

### The form: destinations

60. As a reader, I want no destination control with two sides, so that a two-team trade is as short as today.
61. As a reader, I want a small "To" Select on each picked row once the trade has three or more sides, so that I say where each player goes.
62. As a reader, I want the To picker to list the other sides' teams only, so that a player cannot go to his own roster.
63. As a reader, I want the default destination to be the next side in order, and the first side for the last, so that a ring trade needs few changes.
64. As a reader, I want the destination of a picked player to hold when another side changes its team, so that I do not redo my picks.
65. As a reader, I want the row to read "Name · To <Team>", so that the destination is plain with the picker closed.

### The form: layout and motion

66. As a reader on a phone, I want the sides in one column, in order, so that the form reads top to bottom.
67. As a reader on a tablet or a desktop, I want the sides in a two-column grid, with the third and fourth sides on a second row, so that the form uses the width.
68. As a reader on a desktop, I want the grid to stay two columns, so that the page column does not stretch.
69. As a screen reader user, I want the document order to be side by side, each side as one group with a heading, so that the form reads as a list of teams.
70. As a reader, I want the grade button and the status to span both columns, as today, so that the form ends in one place.
71. As a reader, I want a new side and a picked row to animate in, and a removed one to animate out, so that the form feels alive.
72. As a reader with reduced motion on, I want no movement, so that the form is still.
73. As a reader in the dark theme, I want every picker, row, and picked state to have a fill and readable text, so that the dark form matches the light one.
74. As a reader, I want every label and heading in title case, so that the form matches the site.

### The result

75. As a reader, I want a two-team result to keep the arrow swap card, so that the common case does not change.
76. As a reader, I want a three- or four-team result to render one row per side in the swap card, with what it gives and what it gets, so that the trade reads side by side.
77. As a reader, I want each player in a three-team swap card tagged with the team he goes to or comes from, so that I can trace every move.
78. As a reader, I want one side read per side, in order, so that each team gets its analysis.
79. As a reader, I want the decision and the fairness line to render as today, so that the lead of the result does not change.
80. As a reader, I want a document with no `to` or `from` fields to render the two-team swap card still, so that an old fixture does not break the page.

### Checks and fixtures

81. As a site developer, I want a three-side fixture next to the two-side one, so that the site tests cover both.
82. As a site developer, I want the two-side fixture to carry `to` and `from`, so that the types match the live API.
83. As a developer, I want every check to pass: the pipeline tests, and here `pnpm test`, `pnpm typecheck`, `pnpm build`, and `pnpm check:export`.
84. As a developer, I want a browser pass at 390, 768, and 1280 wide, both themes, reduced motion on, so that the form is seen before it merges.

## Implementation Decisions

### The API contract

- The request is `{ season, asker, sides }`. `sides` is a list of two to four sides in order, the asker first on the site. A side is `{ roster_id, gives }`. Each entry of `gives` is `{ player_id, to }`, `to` a roster id of another side of the trade. There is one shape, so a two-side trade sends `to` as well.
- The proposed trade model checks: two to four sides, distinct rosters, the asker among them, every side gives at least one player, every side gets at least one player, every `to` names another side, no player appears twice. Each check is an input error with a plain message, as today.
- A side's gets derive from the other sides' `to` fields. No caller sends gets.
- The response keeps its shape. Each player in `trade.sides[].gives` gains `to`, and each in `trade.sides[].gets` gains `from`, both roster ids, always present. `trade.sides`, `fairness.sides`, and `sides` list every side in request order.
- The finder stays a two-side tool. It builds its requests with `to` like any caller.

### The grade with many sides

- The letter per side is the ratio of the chart value it gets over the chart value it gives, as today. The adjusters read a side's gets and gives as flat lists, with no care for the source, as today. A side's "other" for the lineup reads is the union of the other sides.
- The fairness runs the same rule over every side: win-win when every letter is at or above the bar, lopsided when any letter is at or below the floor with `gives_more` the one lowest side by the same tie rule, else fair. The state names do not change.
- The decision is for the asker only, as today.
- The decision for the asker with three or more sides compares the asker's letter with the best other side. The reason then reads 'Another side does better, so ask for more.'
- The model output check asks for exactly N sides, one per roster, in the order of the user message. The prompt says the same, names each side's gives and gets with the source and destination of each player, and names the upside among what to cover.

### The upside adjuster

- Upside is the eighth adjuster, after injury and before handcuff. Its step is one or zero. It reads the players a side gets only.
- A star is a player with a chart value in the top `STAR_RANK` of the league's chart. `STAR_RANK` is a tunable with a start of 24.
- A star return bet is a star who is out now, by the Sleeper out statuses, and who is not out for the season. A missing return week does not matter. The injury adjuster exempts a star return bet, the same way it exempts the standing adjuster's return bet.
- An opportunity is a player whose same-position teammate, on the same NFL team, is out for the season or out with no near return, and whose use points up. The up signals are the snap share, target share, and air yards share directions and the WOPR direction that the trend adjuster already computes. A QB reads no snap share.
- The reason names the player and the signal: "Name is a star out now with a return in play." or "Name gains target share with Teammate out for the season."
- Upside has no site change. The result page renders a factor by its name.

### Out for the season

- The returns file accepts the word `season` in place of a week. The loader reads it as out for the season. The snapshot exposes the set of players out for the season.
- A player out for the season counts zero chart value for the side that gets him, in the start letter only. The side that gives him counts his full value.
- The injury adjuster steps the side that gets him down, with the reason "Name is out for the season." This check runs before the no-near-return check.
- Upside never credits a player out for the season.
- A player out for the season also counts zero lineup value on every side, because he cannot play.
- The Sleeper IR status alone is not the mark.

### The form

- The form state is a list of sides in order, each `{ rosterId, picks }`, a pick `{ playerId, toSide }`, where `toSide` is the id of the destination side. The first side is the asker.
- Each side renders as one group with a heading: the team picker, then the player picker once the side has a team, then the picked rows. From the tablet tier the sides sit in a two-column grid and wrap. The grid stays two columns at the desktop tier. The document order is side by side.
- The team picker is the shadcn Select on Base UI, added with the shadcn CLI, with the avatar and the team name in each row and in the trigger. A team picked on one side is absent from the other sides' lists. The first side's label is "Your Team". Later sides' labels are "Team Two", "Team Three", and "Team Four".
- The player picker is the same Select with `multiple`, labeled "<Team> Gives". The trigger reads "Pick Players" when empty and the count when not. Each row shows the headshot, the name, the position, and the NFL team. The picked players render as rows under the trigger with a remove control.
- With three or more sides each picked row gets a small Select labeled "To" that lists the other sides' teams. The default destination is the next side in order, the first side for the last. The row reads "Name · To <Team>". With two sides the destination is the other side and no control shows.
- "Add a Team" is a ghost button in the next grid cell after the last side. It shows when every side has a team and the trade has fewer than four sides. The third and fourth sides have a remove control in their heading. A removed side's players leave the trade. Players sent to it fall back to the default destination.
- The ready rule: every side gives at least one player and every side gets at least one player. A new team on a side clears its picks and the result. Destinations on other sides hold.
- The posted body follows the API contract. The finder opens a two-side trade as today and hides once the trade has a third side.
- A new side and a picked row use a Framer Motion layout animation in and out, under `useMotionOff`. The Select keeps the motion Base UI gives.
- The `TeamPicker` and `PlayerList` components and the `TeamPicker` test go. Issue 11 of site-pages closes as moot.

### The result

- Two sides render the arrow swap card as today. Three or more render one row per side with what it gives and what it gets. Each player chip carries a tag with the team he goes to or comes from, read from `to` and `from`.
- A document with no `to` and `from` renders the two-side swap card still.
- The types gain `to` on a given player and `from` on a got player, both optional in the type, so an old fixture type-checks.

### Order and worktrees

- The pipeline work lands first in a worktree from that repo's `main`. It ships the three-side fixture to this repo under `.scratch/site-react/fixtures/analyze-response-three.json` and adds `to` and `from` to the two-side fixture.
- The site work lands second in a worktree from this repo's `main`.
- Brian tests the whole feature on his machine before any merge: the pipeline `make api` on port 8080, and a new site `make dev-local` that runs the dev server against it. The pipeline `make analyze` takes two to four sides in the new shape.
- The pipeline merges, pushes, and deploys the API first. The site merges to `main` from the main checkout with `--no-ff` when its tree is clean and level with origin, and pushes right after. The live form is down for the minutes between, because the API accepts the new shape only.

## Testing Decisions

A good test reads what a manager or a reader gets: a breakdown, a response body, or the screen. No test reads a class name or a private function.

- Pipeline, the rubric seam: a trade and a snapshot in, a breakdown and a fairness out. Tests cover the destination shape and each input error, the four-side cap, a three-side start letter, a three-side fairness in each state, the star return bet, the opportunity, the season mark, the zero chart value, and the injury step. Prior art: the rubric tests with the `_trade` helper and the `snap` fixture.
- Pipeline, the analysis seam: the model output check with N sides. Tests cover a three-side output that passes and a two-side output for a three-side trade that fails. Prior art: the analysis tests.
- Pipeline, the API seam: the FastAPI test client posts to the analyze route with a fake analyzer. Tests cover a three-side request that grades, each input error as a 422 with its message, and the response fields `to` and `from`. Prior art: the API tests.
- Site, the form seam: the form renders with a fetch stub and each test reads the screen. Tests cover the team picker rows, a picked team absent from other pickers, the player picker and its rows, the remove control, the add and remove of a side, the To picker and its default, the ready rule, the posted body, and the finder hidden at three sides. Prior art: the trade form tests.
- Site, the result seam: a document in, the page out. Tests cover the two-side arrow swap card from the two-side fixture, the row-per-side swap card from the three-side fixture with its tags, and a document with no `to` and `from`. Prior art: the analyze result tests.
- The browser pass runs with agent-browser in a named session at 390 by 844, 768 by 1024, and 1280 by 800, reduced motion on, both themes, with the dev server on a dead API URL and a teams list in session storage.

## Out of Scope

- Draft picks in a trade.
- A fifth side.
- A finder for three-team trades.
- A search box in the team picker.
- Route share, which the data does not hold.
- A season-ending flag from any source but the returns file.
- The rankings table at a laptop width, and issues 07 to 10 of site-pages.

## Further Notes

- Title case for every label and heading. Never a mock mode. Never remove a comment unless it is false. Smallest change to the two-team view.
- The pipeline repo has uncommitted changes from another session. Work in a worktree there and never touch that checkout.
- The dev server writes an untracked `AGENTS.md`. Do not commit it.
- `cornerstone publish` stages every file in this repo, so nothing uncommitted may sit on `main` here.
- The shadcn parts land on Base UI, not Radix. Read the Base UI Select docs for `multiple` and the item render.
