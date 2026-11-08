# Card polish

Status: ready-for-agent
Date: 2026-11-07
Apps: site. The site builds five parts from the methods of Scrolltide items. The pipeline does not change.
Spec branch: `card-polish`.
Source: the map `.scratch/card-polish/MAP.md` and decision tickets 01 to 09, from the session of 2026-11-07. ADR 0024, ADR 0025, ADR 0028.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

A reader of the site, most often a league manager on a phone, gets the story of a week from the hero and then from plain cards and tiles. The cards and tiles show one number or one line each, so the reader must open many pages to see why a team ranks where it does. Two cards build the same open and close in two different ways, and the rest of the site has no shared pattern for it. The submit button of the Trade Analyzer gives no sign of how close a trade is to ready. The Managers index is a grid of tall cards that does not answer the question a manager asks in midseason: who am I in a race with?

## Solution

Five parts upgrade the cards, the tiles, the analyzer, and the Managers index. Each part follows the method of one Scrolltide item as far as the hard rules allow (ADR 0028). The team writes its own code from each method. No Scrolltide source enters the repo.

1. The **Open card**, from the Showcase Card item. One part opens and closes every card that holds more detail. It opens with a height change on a spring, and its details come into focus from a blur. GameCard and LadderCard use it first, then ManagerCard, AwardTile, and TradeCard.
2. The **Grade dial**, from the Health Tracker item. Four equal arcs, one for each part of the Roster grade, each lit by its rank among the teams.
3. The **Trend tile**, from the Lime Metrics item. Seven tiles add a small chart of the same number from week 1 to the page week.
4. The **Ready halo**, from the Send Halo item. The submit button of the Stack glows brighter as each side of the trade fills.
5. The **Index list**, from the Team Roster item. The Managers index becomes a ledger of the teams, filtered by chips of the playoff race. On a phone a tap opens a row in place. On desktop the ledger sits beside a sticky stage.

The hero stays the one loud surface of each page (ADR 0024). The desktop stage is the hero of the Managers index, built from the slots of the `hero-slots` spec.

## User Stories

### Open card

1. As a reader on a phone, I want to tap a game card to see its recap, so that I learn how the game went without a new page.
2. As a reader, I want the open card to grow in place, so that I keep my place in the list.
3. As a reader, I want the details of an open card to come into focus after the card grows, so that I never see half-drawn text.
4. As a reader, I want a chevron under each card that turns when the card opens, so that I know the card holds more and how to close it.
5. As a reader, I want a closed game card to keep both teams, both avatars, both scores, and the share bar, so that the list still reads as a scoreboard.
6. As a reader, I want an open game card to show the best player of each team with the avatar of that team, so that I see who carried each side.
7. As a reader, I want an open game card to show both records, so that I see what the result means for the season.
8. As a reader, I want an open game card to show the recap text and a link to the manager page, so that I can read more about the team that won.
9. As a reader on the rankings page, I want each ladder card to show the rank large, so that the order reads at a glance.
10. As a reader, I want a closed ladder card to show the team, the record, the move, the odds bar, and the playoff chip, so that I see the race without a tap.
11. As a reader, I want an open ladder card to show Stand, Form, Sched, Pts, Move, Bye, and Seed as chips and the blurb as text, so that I see why the team sits at that rank.
12. As a reader, I want the manager, award, and trade cards to open in the same way, so that every card on the site behaves the same.
13. As a reader who uses find-in-page, I want the text of a closed card to stay findable, so that a search finds a recap or a blurb.
14. As a reader with a screen reader, I want each card toggle to say if it is open and which panel it controls, so that I can use the cards without sight.
15. As a reader who sets reduced motion, I want each card to open and close at once, so that no motion makes me unwell.
16. As a reader on a slow phone, I want the open card to stay smooth, so that the motion feels finished and not broken.

### Grade dial

17. As a manager, I want to see the four parts of the Roster grade of a team, so that I know why the team has its letter.
18. As a manager, I want each part to have its own arc, its name, and its weight, so that I know which part counts most.
19. As a manager, I want each arc lit by the rank of the team, so that a full arc means the best team in that part.
20. As a manager, I want the rank as text in each arc, for example "4th", so that I can read it without a count of blades.
21. As a manager on a manager page, I want the letter, the grade read, and the four arcs in Season So Far, so that the grade story sits with the season story.
22. As a reader with a screen reader, I want each arc to read as its part, rank, and weight, so that the dial is not only color.
23. As a reader who sets reduced motion, I want the arcs to appear lit at once, so that no fill animation plays.

### Trend tile

24. As a reader of a week page, I want the top score tile to show the top score of each week of the season, so that I see if this week was a big one.
25. As a reader, I want the median tile to show the league median of each week as a stepped area, so that I see if scoring rises or falls.
26. As a reader, I want the closest tile to show the margin of the closest game of each week, so that I see how tight this week was.
27. As a reader, I want the Game Changer tile to show the points over projection of each Game Changer, so that I see how big this week's surprise was.
28. As a reader, I want the bar of the page week lit, so that I find this week in the trend.
29. As a reader of an older week page, I want the trend to stop at that week, so that the page never shows a later week.
30. As a manager, I want the Adds and Drops tiles on a manager page to show the adds and drops of each week as bars, so that I see when a team was active.
31. As a manager, I want the Trades tile to show each week with a trade as a dot, so that the rare trade stands out.
32. As a reader with a screen reader, I want each Trend tile to read its number and a short text of the trend, so that the chart is not the only source.

### Ready halo

33. As a manager on the Trade Analyzer, I want the submit button to glow brighter as I fill the trade, so that I know how close the trade is to ready.
34. As a manager, I want the halo at full only when every side has a team, gets a player, and gives a player, so that full glow means the trade can be graded.
35. As a manager, I want the halo to dim if I remove a player, so that the glow always tells the truth.
36. As a manager in the light theme, I want the halo to read on a light page, so that the sign works in both themes.
37. As a manager who sets reduced motion, I want the halo to change brightness with no pulse, so that no motion plays.

### Index list

38. As a manager on a phone, I want the Managers index as a ledger of all teams on one screen, so that I see the whole league at once.
39. As a manager, I want each row to show the place, a small avatar, the team name, and the playoff odds, so that I can find a team fast.
40. As a manager, I want chips for All, In, Bubble, and Out, so that I can see only the teams in my race.
41. As a manager, I want In to mean clinched or odds of 75% or more, Bubble 25% to 75%, and Out eliminated or under 25%, so that each chip has one meaning.
42. As a manager, I want each chip to show its count, so that I know the size of each group before a tap.
43. As a manager, I want a tap on a row to open it in place with the letter, the grade read, the four arcs, and a link to the manager page, so that I can compare teams without a new page.
44. As a manager, I want one row open at a time, so that the ledger stays short.
45. As a manager, I want the name of the open row to roll its letters, so that I see which row I chose.
46. As a manager on desktop, I want the ledger beside a sticky stage, so that a hover on a row shows its detail in one fixed place.
47. As a manager on desktop, I want the stage in the hero look with the same slots as every hero, so that the page feels like the rest of the site.
48. As a keyboard user on desktop, I want a focus on a row to swap the stage, so that the stage works without a mouse.
49. As a reader who sets reduced motion, I want the rows to open and the stage to swap at once, so that no motion plays.
50. As a reader of the NorCal site, I want the Index list to work with the NorCal data and brand, so that both clients get the upgrade.

### Both clients and the floor

51. As a reader in either theme, I want every new part to pass the readability floor, so that the text stays readable.
52. As a reader on a phone, I want no new part to scroll the page sideways at 390px, so that the page fits my screen.
53. As a reader on a phone, I want every new control to be at least 44px, so that I can tap it with a thumb.

## Implementation Decisions

### The rule of the five parts

- Each part follows the method of its Scrolltide item: its structure, its motion, and its easing. Only a hard rule of ADR 0028 overrules the item: the readability floor, reduced motion, the phone layout first, and the hero as the one loud surface.
- The team reads the Scrolltide prompts only from the session scratchpad. The repo is public, and the prompts are paid source. No file of the repo copies their source.

### Open card

- One shared design part. It takes a head, the panel content (an overview line, chips, a rule line, and a text), an optional action link, and a controlled or uncontrolled open state.
- The head is the only part that differs per card. GameCard keeps the closed layout it has now. LadderCard takes the full Showcase shell: a plain raised media panel with the rank large, then the team, the record, the move, the odds bar, and the playoff chip.
- The height animates with `grid-template-rows` from `0fr` to `1fr`, the one height method of the site. The closed panel stays in the DOM with `inert`.
- The panel comes into focus from a 6px `filter: blur`, a short rise, and an opacity change, about 0.1s behind the height.
- The motion uses a damped spring sampled into a CSS `linear()` curve, with a small overshoot, over about 0.45s. A small design helper builds the curve. The chevron turns 180 degrees on the same curve.
- The action link is a pill with a solid fill under its label, because text on a frosted blur fails the axe floor. Its label rolls up to a copy of itself on a fine-pointer hover.
- The GameCard chips are three: the best player of the winner, the best player of the loser, and both records. Each best-player chip starts with the small avatar of its team, then "Best", the player, and the points. Margin and vs projection are not chips.
- The LadderCard chips are Stand, Form, Sched, Pts, Move, Bye, and Seed. The overview line is the rank, the record, and the move. The text is the blurb.
- ManagerCard, AwardTile, and TradeCard use the same part with a head of their own. Their chips come from the fields they show now. No new prototype is needed.
- The two accordions of GameCard and LadderCard go, and the shared part replaces them.

### Grade dial

- One design part in two sizes, small and large. It takes the four parts of the Roster grade, each with its key, its rank, and its weight, and the count of teams.
- Each arc follows the Health Tracker dial: pill blades on a 210 degree arc, 12 blades per arc, one per team. The lit count is the count of teams plus one, minus the rank, so rank 1 lights every blade.
- The rank sits in the center of the arc as text. The part name and "N% of the grade" sit under the arc as text.
- The fill plays once when the dial enters the view, with the stagger and easing of the item. Reduced motion shows it lit at once.
- Season So Far on the manager page shows the letter and the grade read on top, then the four arcs in a 2x2 grid.
- The Index list shows the four arcs in the open row and in the stage. The cards of the Managers index go, so the dial does not sit on a card.
- The weights (decision 09): a site constant of the managers package holds 45, 30, 10, and 15 for projection, production, trade value, and depth. A site test reads `GRADE_WEIGHTS` from the pipeline tunables file and fails if the two differ. This keeps the spec on the site only and stops a silent drift.

### Trend tile

- `Tile` takes an optional trend: a list of week points, the page week, and a chart kind of `bars`, `step`, or `dots`. A tile with no trend renders as it does now.
- The charts follow the Lime Metrics item: a bar series and a stepped area. The donut is not used, because none of the seven numbers has parts of a whole.
- The trends are these. Top score: the top score of each week, bars. Median: the league median of each week, a stepped area. Closest: the margin of the closest game of each week, bars. Game Changer: the points over projection of each week's Game Changer, bars. Adds and Drops: the adds and drops of the manager each week, bars. Trades: the trades of the manager each week, dots.
- The bar of the page week is lit. Each trend runs from week 1 to the page week, so an older week page shows no later week.
- The week route loads the earlier weeks of the season at build time with the week data module it already uses. A pure function turns the weeks into the four series. The component gets the series as props (ADR 0012).
- The Moves tiles read the week list of moves that `managers.json` already holds.
- Each Trend tile has a text alternative: the number, and one short sentence of the trend, for example "Highest since week 3".

### Ready halo

- The halo wraps the grade button of the Stack, the button the grade bar holds.
- The level comes from the three checks of each side that the ready rule already uses: the side has a team, the side gets at least one player, and the side gives at least one player. The level is the count of passed checks over three times the count of sides (decision 08).
- The glow brightens with the level, in the method of the Send Halo item. It reaches full only when the ready rule passes, which is also when the button can grade.
- The glow uses the accent role of the brand, so it works in both themes and for both clients. In the light theme the halo keeps its contrast against the page.
- Reduced motion keeps the change of brightness and drops any pulse or orbit.

### Index list

- The Managers index becomes a ledger of the teams in the order of the power ranking of the page week. Each row shows the place, a small avatar, the team name, and the playoff odds. The row adds nothing more.
- The chips above the ledger are All, In, Bubble, and Out, each with its count. In is clinched or odds of 75% or more. Bubble is 25% to 75%. Out is eliminated or under 25%. A pure function maps the odds and the status word to the group. A chip with no team stays visible, shows a count of 0, and cannot be pressed.
- The status word joins the type of the odds that the loader gives the page.
- On a phone and a tablet, a tap on a row opens it in place with the Open card drawer: the avatar, the facts, the grade letter, the grade read, the four arcs, and a link to the manager page. One row is open at a time.
- On desktop, from the desktop tier of 64rem, the ledger sits beside a sticky stage. A hover or a focus on a row swaps the stage with the wipe and the zoom of the Team Roster item.
- The stage is the hero of the Managers index. It is built from the six slots of the `hero-slots` spec: eyebrow is the race word, title is the team name, meta is the record, the place, and the playoff odds, feature is the four arcs, stats is the grade letter, and action is the link to the manager page. Its ticket waits for `hero-slots` to merge into `main`.
- The name of the open row, or the row in the stage, rolls its letters, after the item.

### Glossary

- The spec adds Open card, Grade dial, Trend tile, Ready halo, and Index list to the site section of `GLOSSARY.md`. The Grade dial entry says four arcs, one for each part of the Roster grade, each lit by its rank. The Index list entry names the chips and the stage.
- The spec adds In, Bubble, and Out as the race groups of the Index list.

## Testing Decisions

A good test checks what a reader sees or what a function returns, not how the part builds it. The tests use real published data: the `cpc` and `norcal` files under `clients/`. No test mocks a part of the site.

The seams, from the highest down:

1. **The readability floor on the built export.** The existing floor check runs each route at 390px and 1280px in both themes, for both clients. The spec adds the open states: an open game card, an open ladder card, an open Index list row, the stage on desktop, and the Season So Far dial. Prior art: the floor spec and its rules spec in the site e2e folder.
2. **The page render.** The existing page tests render a route with its real data and check the markup. They prove the Index list order, the chips and their counts, the trend series of an older week, and that a tile with no trend is unchanged. Prior art: the page test of the week route and of the home route.
3. **The part render.** A part test renders one part with real props and checks its behavior: the toggle states and `aria-expanded`, `inert` on a closed panel, the lit blade count of each arc, the text alternative of a Trend tile, the halo level for each count of filled checks. Prior art: the all-matchups, season-so-far, moves, and trade-form tests.
4. **The pure functions.** Unit tests cover the race group of a team, the four week series, the halo level, and the spring curve sampler. Prior art: the trade helpers test of the analyzer.
5. **Reduced motion.** The existing reduced-motion test proves each new part changes state at once under `prefers-reduced-motion`. Prior art: the site reduced-motion test.
6. **The weights.** One site test compares the weight constant to `GRADE_WEIGHTS` in the pipeline tunables file.
7. **The frame rate of the blur.** A new e2e check opens a game card on a phone viewport with 4x CPU throttle and records the frame rate. ADR 0028 keeps the blur unless this check fails. The check records evidence. It is not a gate of CI.

## Out of Scope

- The Grade dial in the manager hero. The `hero-slots` spec owns every hero, and this spec does not touch the manager page hero.
- A pipeline series for the trends, and the weights in `managers.json`. This spec changes the site only.
- A fetch of the 168px full-size avatar in place of the 80px thumb. It is a pipeline change.
- The tiles of Season So Far, Roster, the rankings, and every hero tile. Season So Far already has the points line. The others have no series.
- The other Scrolltide items: Morph Navbar, Wordmark Bleed, and the easter-egg ideas.
- A link variant of `Card`, one section wrapper in place of four, and a refresh of `apps/site/.impeccable.md`. Each is a cleanup with its own ticket.

## Further Notes

- Only the ticket of the desktop stage waits for `hero-slots`. Every other ticket can merge into the spec branch first.
- The Open card is the base part of the Index list rows, so its ticket comes before the Index list.
- The Showcase Card, Health Tracker, and Team Roster notes sit in the session scratchpad under `scrolltide/`. A new fetch of an item already opened is free within the plan. An agent that builds a part reads the item there or fetches it again, and never commits it.
- The prototypes of decisions 02, 03, and 07 ran on the live pages over the LAN on Brian's phone. The same check on a phone helps the review of each ticket.
