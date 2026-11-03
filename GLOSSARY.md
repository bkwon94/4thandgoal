# Cornerstone site

The public site of the Cornerstone Fantasy Football League. It renders the weekly report, the power rankings, and the trade analyzer that the pipeline repo publishes.

## Language

**Masthead**:
The black band at the top of every page with the brand link, the page line, the week line, and the menu.
_Avoid_: Header, nav bar, top bar, banner

**Menu**:
The list of site destinations that opens from the menu button and reaches every page.
_Avoid_: Drawer, nav, hamburger, navigation

**Menu button**:
The control in the masthead that opens and closes the menu.
_Avoid_: Hamburger, toggle, burger

**Page column**:
The centered column that holds every page's content.
_Avoid_: Container, wrapper, main column

**Tier**:
One of the three viewport ranges the site designs for: phone, tablet, and desktop.
_Avoid_: Breakpoint, screen size, device class

**Chapter rail**:
The list of the weekly report's chapters that sits beside the content on a desktop and marks the chapter in view.
_Avoid_: Sidebar, table of contents, TOC, outline

**Compact bar**:
The short black bar that shows at the top of the viewport once the masthead scrolls out, with the brand mark and the menu. Readers and screen readers know it as "Top bar".
_Avoid_: Sticky header, mini header, app bar, toolbar

**Chapter**:
One part of a page, such as the awards of the weekly report or the tools of the home page. On a tablet and a desktop each chapter is a card on the grey body. "Card" names that look and nothing else.
_Avoid_: Section, block, panel

**Sheet**:
The menu as it opens on a phone and a tablet, under the masthead, over the dimmed page.
_Avoid_: Drawer, modal, overlay

**Dark chapter**:
A chapter that sits on the brand black, such as the standings or the rankings table. It keeps the name in the dark theme, where it lifts one step to grey.
_Avoid_: Black card, dark section, dark card, panel, block

**Page**:
The surface behind the dark chapters. It is white in the light theme and black in the dark theme.
_Avoid_: Background, canvas, body

**Theme**:
The light or dark set of surface and text colors. The reader picks one with the theme button, and the choice holds across visits.
_Avoid_: Mode, scheme, skin, color mode

**Theme button**:
The control in the masthead and the compact bar that switches the theme.
_Avoid_: Toggle, switch, mode button, dark mode toggle

**Trade**:
A proposed swap of players between two to four teams that the analyzer grades before it happens.
_Avoid_: Deal, proposal, swap

**Side**:
One team in a trade, with the players it gives and the players it gets.
_Avoid_: Party, team slot, leg, participant

**Asker**:
The side that asks for the grade. The decision is for the asker. On the form the asker is the first side, "Your Team".
_Avoid_: My team, owner, requester, user

**Destination**:
The side that a given player goes to. With two sides it is the other side. With three or more sides the reader picks it per player.
_Avoid_: Target, recipient, receiver

**Picker**:
A select control on the trade form: one per side for the team, and one per side for the players it gives.
_Avoid_: Dropdown, chooser, selector, list

**Swap card**:
The chapter of the result that shows what every side gives and gets.
_Avoid_: Trade summary, exchange, ledger

**Good for both**:
The page word for the win-win state of the fairness when the trade has two sides. With three or more sides the page word is "Good for all". Use "win_win" in code. The finder shows two-side trades, so it always says "Good for both".
_Avoid_: win-win on the page

**Manager page**:
The page for one team of the league, for one season, with its grade, odds, moves, and performers.
_Avoid_: Team page, owner page, profile

**Managers index**:
The page that lists the twelve teams of a season and links to each manager page.
_Avoid_: Roster list, team list, directory

**Hero**:
The top of a manager page: the avatar, the team name, the owner, the record, and the standing.
_Avoid_: Header, banner, masthead, title block

**Roster grade**:
The letter, A to D, that says how good a roster is now, from a 0 to 100 score of four parts.
The parts are the projection ahead, the season production, the trade value, and the depth and holes.
_Avoid_: Score, rating, power score

**Playoff odds**:
The chance, as a percent, that a team makes the playoffs from where the season stands now.
_Avoid_: Playoff chances, probability, projection

**Bench points**:
The points a team left on its bench in a week: the best lineup's points minus the lineup it started.
_Avoid_: Lineup efficiency, optimal lineup gap, points lost

**Points line**:
The small chart on a manager page with the team's points per week against the league median, a dot per week.
_Avoid_: Sparkline, trend, graph

**Slot rank**:
Where a team's starters at one position rank in the league, with one word for depth.
The depth words are stacked, deep, fine, and thin. A spare counts only inside the league's starter count.
_Avoid_: Position grade, position strength, tier

**Moves**:
A team's adds, drops, bids, and trades, listed by week on its manager page.
_Avoid_: Transactions, activity, log

**Best adds**:
The adds that scored the most points for the team after the add, in any number of games.
_Avoid_: Waiver wins, pickups, steals

**Top performers**:
The players that scored the most points for the team while they started for it, year to date.
_Avoid_: Studs, stars, leaders

**Season numbers**:
The four numbers under the points line: the season high, the season low, the streak, and the record against the median.
_Avoid_: Stats row, shelf, summary

### The code

**Part**:
A component that takes data and returns markup, shared across pages: the chapter card, the team name, the player row, the points line. A part never reads a file, the env, or a route.
_Avoid_: Widget, shared component, common component, block

**Primitive**:
A shadcn control under the parts: a button, a select, a dialog, a popover. A primitive knows nothing of the league.
_Avoid_: Base component, atom, ui element

**Shell**:
The parts that frame every page: the masthead, the menu, the compact bar, and the theme button.
_Avoid_: Layout, chrome, frame, nav

**Published file**:
One JSON file the pipeline publishes into `public/`, such as a week page, the rankings, or the managers file. The pipeline owns its shape, and the site reads it with one loader.
_Avoid_: Snapshot, data file, feed, export

**Loader**:
The one build-time reader of a published file. It checks the shape and hands typed data to the app layer. Only the app layer calls a loader.
_Avoid_: Fetcher, reader, data module

## Workflow

**Map**:
The optional page that sets the destination of a feature, what is decided, what is not yet specified, and what is out of scope.
_Avoid_: Roadmap, overview, brief

**Fog**:
A part of a feature that is not yet specified. It stays on the map until a decision ticket clears it.
_Avoid_: Unknowns, TBD, open questions

**Decision ticket**:
A note that records one choice of a feature and how it was reached, by a grill, a research, a prototype, or a spec.
_Avoid_: ADR, decision log, design note

**Spec**:
The statement of one feature: what it does and how a reader proves it works.
_Avoid_: PRD, requirements, design doc

**Spec branch**:
The branch that holds all the work of one spec. It merges into the record branch as one squashed pull request.
_Avoid_: Feature branch, topic branch, epic branch

**Ticket branch**:
The short-lived local branch for one ticket of a spec. It merges into its spec branch.
_Avoid_: Task branch, sub-branch, work branch

**Record branch**:
The branch that holds only work that passed its acceptance tests. No agent commits on it, except to publish a week.
_Avoid_: Trunk, master, default branch, release branch

**Acceptance test**:
A statement of behavior that a reader checks on the finished work, with evidence, to decide if the spec is met.
_Avoid_: Test case, QA step, check, criterion

**Verdict**:
The word PASS, FAIL, or BLOCKED that Brian gives to one acceptance test. Only a verdict counts toward a merge.
_Avoid_: Result, approval, sign-off, status
