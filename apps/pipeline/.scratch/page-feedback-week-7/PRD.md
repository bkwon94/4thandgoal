# Page feedback after week 6: Butterfingers, luck, position leaders, brand link

Status: ready-for-agent
Date: 2026-10-20
Glossary: `GLOSSARY.md`, see **Position leader**.

## Problem Statement

Brian read the week 6 page and gave four notes.

1. The Butterfingers award is not fun. It names one receiver for drops and the tile looks like
   a penalty box.
2. The page says "lucky" six times in one week. The word reads as a crutch, not a judgment.
3. The page shows one Top Scorer for the whole league. It never shows who led at each position,
   which is the question a manager asks first.
4. The logo in the masthead does nothing when tapped. There is no way home from a week page
   except the browser back button.

## Solution

The Butterfingers award leaves the page and the model. The writer keeps "lucky" for a recent
add that scored at least twice its projection, at most once per page. A Position Leaders
section shows the three started players with the most points at QB, RB, WR, TE, and DEF, with
a short blurb under the boards. The brand block in the masthead links to the season index on
every page.

## User Stories

1. As a league member, I want the Butterfingers award gone, so that the awards read as fun and not as a penalty box.
2. As a league member, I want the page free of a drop note under Awards, so that no sentence explains a tile that no longer exists.
3. As the commissioner, I want drop facts to stay in the matchup chapters, so that the writer can still say a drop was worth about N points.
4. As a reader, I want "lucky" to be rare, so that the word means something when it appears.
5. As a reader, I want "lucky" used only for a recent add that scored at least twice its projection, so that the word follows a real gap and not a feeling.
6. As a reader, I want "lucky" at most once per page, so that one page does not lean on one word.
7. As a reader, I want "recent add" to stay the label for a waiver, free agent, or trade pickup, so that the fact gate for those words does not change.
8. As a manager, I want to see the three top started players at QB, RB, WR, TE, and DEF, so that I know who led each position this week.
9. As a manager, I want each leader row to show rank, player name, NFL team, points, and the fantasy team that started him, so that one glance tells the story.
10. As a manager, I want the boards in the order QB, RB, WR, TE, DEF, so that the order matches a lineup.
11. As a manager, I want FLEX players counted at their real position, so that a flexed RB competes with the RBs.
12. As a manager, I want bench players left out of the boards, so that a leader is a player who scored for a team.
13. As a manager, I want DEF leaders shown by the defense's name and NFL team, so that a defense reads like a player row.
14. As a reader, I want a short blurb under the boards, so that the section has a voice like the rest of the page.
15. As the commissioner, I want the blurb to name only the leaders and the fantasy teams that started them, so that every claim in it comes from a fact.
16. As the commissioner, I want the blurb to use only numbers from its own facts, so that the verifier can reject a made-up gap.
17. As the commissioner, I want ties broken by name and three rows always, so that the board is stable and never grows.
18. As a reader, I want the Position Leaders section after Awards and before Trades, so that it reads as a league-wide stat block with the awards.
19. As a reader on a phone at 390px, I want the five boards to stack, so that no row wraps or clips.
20. As a reader on a wide screen, I want the five boards in a grid, so that the section does not run long.
21. As a reader, I want the Top Scorer award to stay in Awards, so that the one league-wide winner keeps a tile.
22. As a reader, I want the brand block in the masthead to link to the season index, so that one tap takes me home from any week.
23. As a reader on the index page, I want the brand link to point at the page itself, so that the masthead behaves the same on every page.
24. As a reader, I want the whole brand block to be the tap target and not just the small logo, so that the link is easy to hit on a phone.
25. As the commissioner, I want the glossary to carry **Position leader**, so that the term does not collide with the Top Scorer award or the per-team top scorer fact.
26. As the commissioner, I want the default test suite to pass with no network, so that the build stays safe for the Tuesday job.

## Implementation Decisions

### Butterfingers

- The award key leaves the award model, the award computation, the award titles, the tile keys,
  the render context, the writer vocabulary, and the tests that cover it.
- The drop lines, the drop source, the drop facts, the drop swing, and the nflverse drop fetch
  stay. The matchup chapters cite them today and the trade chapter cites the drop swing.
- The drop note under the Awards section goes. It described the estimate on the tile. The
  vocabulary entry for drop value stays, so the writer still writes "worth about".
- The Awards chapter facts stay as they are, minus the Butterfingers award fact and its rank and
  history facts. The `W.drops` fact stays in the Awards chapter.

### Lucky

- The tone rule changes from "allowed for a recent add that beat its projection" to "at most
  once per page, and only for a recent add that scored at least twice its projection".
- The writer rule 8 and the vocabulary entry for recent add carry the same limit.
- The verifier gate for "lucky" does not change. No code counts the word across chapters.
- A week with no projections lets no recent add be "lucky". That is the intended result.

### Position leaders

- A position leader is one of the three started players with the most points at one position,
  league wide. FLEX players count at their real position. Bench players do not count.
- The week data gains a list of leaders. Each leader holds the player line, the position, the
  rank 1 to 3, the count of started players at that position, and the roster id.
- The order of the positions is QB, RB, WR, TE, DEF. The sort inside a position is points
  descending, then name ascending. Three rows always. A position with fewer than three started
  players shows the rows it has.
- The fact sheet gains one fact per leader with the ID prefix `LEAD.`, such as
  `LEAD.RB.1`. The text names the player with position and NFL team, the points, the rank, the
  count at the position, and the fantasy team. The numbers list holds the points, the rank,
  and the count.
- A new chapter `position_leaders`, title "Position Leaders", cites the `LEAD.` facts only.
  Its sentence range is 2 to 4. Its scope teams are every roster. Its scope players are the
  leaders. It sits after `awards` and before the first `trade_` chapter in the chapter list.
- The page gains a section "Position Leaders" after Awards and before Trades. It shows five
  boards in the order above. Each board has the position as its label and three rows. Each
  row shows the rank, the player name, the NFL team, the points, and the fantasy team.
- The boards stack at phone width and sit in a grid at wider widths. The design pass uses the
  existing tokens in the stylesheet. Long fantasy team names must not wrap a row.
- The blurb for `position_leaders` renders under the boards, the same as the awards blurb.
- The Top Scorer award stays.

### Brand link

- The brand block in the shared shell becomes a link to the season index. The link target is
  the `root` the page already receives, so a week page goes up two levels and the index page
  points at itself.
- The link wraps the whole brand block. The link keeps the current look: no underline and the
  same colors.

### Glossary

- `GLOSSARY.md` carries **Position leader** under a new heading "The page". Done during the
  interview.

## Testing Decisions

A good test builds a bundle from the fixture raw directory, or renders a page from a bundle,
and asserts on what a reader or the writer sees. A test never reaches into a helper.

- The bundle seam, prior art in `tests/test_sheet.py` and `tests/test_facts_league.py`:
  - The awards hold no Butterfingers key, and the sheet has no `AW.butterfingers` fact.
  - The drop facts and the drop swing still exist for a bundle with drops.
  - The leaders list has three rows per position in the order QB, RB, WR, TE, DEF, sorted by
    points then name, started players only.
  - The sheet has one `LEAD.` fact per leader, and every number in its text is in its
    numbers list. The existing number tests cover this for free.
  - The chapter `position_leaders` exists, cites only `LEAD.` facts, has the range 2 to 4,
    and sits after `awards` and before any `trade_` chapter.
- The render seam, prior art in `tests/test_render.py`:
  - The awards context lists four tiles and no Butterfingers title.
  - The page has no drop note for any drop source.
  - The page has a Position Leaders section with five boards and 15 rows, with the rank,
    the name, the NFL team, the points, and the fantasy team on each row.
  - The week page and the index page each wrap the brand block in a link to the index.
- The verifier tests do not change. The lucky rule is prompt text.
- The default suite runs with no network. The existing fixtures cover one week with drops.

## Out of Scope

- A code count of "lucky" across the chapters.
- A gap fact between first and second place at a position.
- Leaders over the season, or for weeks before this one.
- A kicker board. The league has no kicker slot.
- Any change to the awards that stay.
- The design polish backlog item for long names on other cards.
- A rebuild or a publish of week 6. The first page with these changes is week 7.

## Further Notes

- Each build gains one writer call for the new chapter, about 18 in all.
- The design pass on the boards follows the handoff: `/emil-design-eng` and `/apple-design`,
  measured with `agent-browser` at a 390 by 844 viewport.
- The real week 6 sheet has 31 started RBs, so the count in a `LEAD.RB.` fact reads "of 31".
