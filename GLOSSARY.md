# Cornerstone

The terms of the site in `apps/site/` and the pipeline in `apps/pipeline/`. Each term has one meaning.
A term sits in the section of the app that owns it. The workflow terms hold for both apps.

## Site language

The public site of the Cornerstone Fantasy Football League. It renders the weekly report, the power rankings, and the trade analyzer that the pipeline publishes.

**Top band**:
The band at the top of every page with the brand mark, the week chip, and the theme button. On a desktop it also holds the pill bar.
_Avoid_: Masthead, header, nav bar, top bar, banner

**Menu**:
The list of the destinations of a client. It shows as the dock on a phone and a tablet, and as the pill bar on a desktop.
_Avoid_: Drawer, nav, hamburger, navigation

**Pill bar**:
The row of destinations with full labels in the top band of a desktop.
_Avoid_: Tab bar, nav bar, link row

**Dock**:
The bar of destinations that floats at the bottom of the viewport on a phone and a tablet, and stays on screen at every scroll.
_Avoid_: Tab bar, bottom nav, footer

**Week chip**:
The control in the top band that shows the current week and opens the strip of the weeks of the season.
_Avoid_: Week picker, week dropdown, week selector

**Page column**:
The centered column that holds every page's content.
_Avoid_: Container, wrapper, main column

**Tier**:
One of the three viewport ranges the site designs for: phone, tablet, and desktop.
_Avoid_: Breakpoint, screen size, device class

**Chapter rail**:
The list of the weekly report's chapters that sits beside the content on a desktop and marks the chapter in view.
_Avoid_: Sidebar, table of contents, TOC, outline

**Chapter**:
One part of a page under its heading, such as Awards of the week page. "Card" names a plain surface, and "Tile" names a small card with one number.
_Avoid_: Section, block, panel, black chapter, dark chapter

**Sheet**:
The short panel that rises from the bottom over the dimmed page, such as the team list and the player picker of the analyzer. The pipeline term is "Fact sheet".
_Avoid_: Drawer, modal, overlay

**Page**:
The surface behind the cards. It is dark in the dark theme and light in the light theme.
_Avoid_: Background, canvas, body

**Theme**:
The light or dark set of surface and text colors, inside the brand of the client. The reader picks one with the theme button, and the choice holds across visits.
_Avoid_: Mode, scheme, skin, color mode

**Theme button**:
The control in the top band that switches the theme.
_Avoid_: Toggle, switch, mode button, dark mode toggle

**Side**:
One team in a proposed trade, with the players it gives and the players it gets.
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

**Manager page**:
The page for one team of the league, for one season, with its grade, odds, moves, and performers.
_Avoid_: Team page, owner page, profile

**Managers index**:
The page that lists the twelve teams of a season and links to each manager page.
_Avoid_: Roster list, team list, directory

**Hero**:
The loud top surface of each page, with the grid texture and the brand glow. It stays dark in both themes. On a manager page it holds the avatar, the team name, the grade, and the record.
_Avoid_: Header, banner, masthead, title block

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
_Avoid_: Waiver wins, steals. Top pickups is a different term: the waiver bucket of the pool.

**Top performers**:
The players that scored the most points for the team while they started for it, year to date.
_Avoid_: Studs, stars, leaders

**Season numbers**:
The four numbers under the points line: the season high, the season low, the streak, and the record against the median.
_Avoid_: Stats row, shelf, summary

**Ladder**:
The layout of the rankings page: a hero for the team at rank 1 and one card for each other team.
_Avoid_: Rankings table, leaderboard, list

**Stack**:
The layout of the analyzer page: one scroll with the teams row and one card for each team of the trade.
_Avoid_: Trade form layout, wizard, steps

### The code

**Part**:
A React component that takes data and returns markup, shared across pages: the chapter card, the team name, the player row, the points line. A part never reads a file, the env, or a route.
_Avoid_: Widget, shared component, common component, block

**Primitive**:
A shadcn control under the parts: a button, a select, a dialog, a popover. A primitive knows nothing of the league.
_Avoid_: Base component, atom, ui element

**Shell**:
The parts that frame every page: the top band, the dock, the pill bar, the week chip, and the theme button.
_Avoid_: Layout, chrome, frame, nav

**Loader**:
The one build-time reader of a published file. It checks the shape and hands typed data to the app layer. Only the app layer calls a loader.
_Avoid_: Fetcher, reader, data module

## Pipeline language

The pipeline builds the weekly report page for the Cornerstone fantasy football league. It turns Sleeper and nflverse
data into facts, the facts into prose blocks, and the prose blocks into page data for the site.

### The fact sheet

**Fact**:
One sentence of true data with an ID, the numbers it holds, and the teams and players it names.
_Avoid_: stat, data point

**Fact sheet**:
Every fact of one week plus the prose blocks that cite them.

**Fact group**:
One module of the fact sheet that builds the facts of one subject, such as the standings or the awards, and feeds the prose blocks that cite them. A fact group is not a prose block.
_Avoid_: fact chapter, section, builder

**Prose block**:
One unit of prose on the page, with the fact IDs it may cite and the sentence range it must fit.
The pipeline code still names it `chapter`. A later ticket renames the code.
_Avoid_: chapter (that is the site card), section, blurb (a blurb is the written output, a prose block is the brief)

**Blurb**:
The sentences the writer wrote for one prose block, each with the fact IDs it cites.

**Reaction sentence**:
One sentence per blurb that reacts to the sentence before it and cites no fact ID. It has no digit,
no team or player name, and fewer than 8 words, and it counts in the sentence range.
The last-name match is case-sensitive, so "that hurts" passes when Jalen Hurts is in scope.
_Avoid_: aside, uncited sentence

**Banned word**:
A word on the "Banned words" line of the vocabulary file. The code check fails a sentence that
has one, after the names are removed.

**Banned phrase**:
A phrase on the "Banned phrases" line of the vocabulary file. The code check fails it the same way
as a banned word, matched as whole words.

**Writer**:
The Claude call that turns one prose block and its facts into a blurb.

**Verifier**:
The code check and the Claude check that reject a blurb with an uncited number or claim.
The code check does not match the last name of an out-of-scope player when that name is a word of
a scope team name. So a bare "London" passes when London Cooking is in scope.
The full name "Drake London" still fails.

**Game time**:
The NFL games of the week that kick off together, by the Eastern kickoff: Thursday, the early Sunday
games, the late Sunday games, Sunday night, and Monday. Every day but Sunday is one game time.
_Avoid_: slot (that is a lineup slot), window, time slot

**Lead by game time**:
The margin of one matchup after each game time in which one of its starters played, and the count of
lead changes. The `M<n>.lead` fact gives it.

**Turn**:
A matchup whose leader before its last game time lost the game. The `M<n>.turn` fact names the
starters of that last game time and their points.
_Avoid_: comeback, collapse

**Injury play**:
The first play of the week where the nflverse play by play says a carrier was hurt. The
`M<n>.hurt.<pid>` fact gives its quarter and its clock for a starter.

### The season

**Remaining schedule**:
The pairs of every regular-season week after next week, weeks N+2 to 14, saved with the week's raw
data as `schedule.json`. Next week's pairs stay in the next-week fetch. The odds engine reads both.
_Avoid_: schedule (alone; that is the schedule played component), fixtures

**Playoff odds**:
The share of the engine's runs in which a team ends in a playoff spot, as a whole percent from 1 to 99.
A clinched team shows 100 and a team that is out shows 0. Each run plays every remaining week with
the head-to-head game and the median game. The `ODDS.` fact also gives the bye odds and the most likely seed. Use "odds" in code and
"Playoff %" on the page. The fact says "about" before the number.
_Avoid_: playoff chances, chance, probability, projection (that is a player's projected points)

**Must Watch**:
One of the two next-week games with the highest storyline score. The page marks it and gives its reason.
_Avoid_: game of the week (that is this week's matchup of the week), featured game

**Storyline**:
One data-backed reason a next-week game matters, from a fixed set: streak on the line, projected shootout,
rematch, revenge, near the cut, top of the table. Each has a weight. A game's storyline score is the sum.
_Avoid_: angle, narrative, hook

**Key starter**:
A player a team started in at least 3 of its last 4 completed weeks, at QB, RB, WR, or TE. With fewer than 4
played weeks, 2 of 3, then 2 of 2. The rule reads real starts, not the best lineup. A kicker or a defense is never one.
_Avoid_: star (that is a chart rank), stud, core player, regular

**Bye line**:
The line under a team in a next-week game card that names every rostered player of that team on bye next
week, key starters first and marked. A team with nobody on bye has no bye line. The prose about the byes is
part of the Next Week blurb, not of the line.
_Avoid_: bye note, bye alert, bye hole (that is a trade term)

**Thin data**:
A build with no NFL schedule, or with fewer than 2 completed weeks of history. The bye lists are empty, and the
build makes no bye fact, not even a "nobody on bye" fact.
_Avoid_: missing data, sparse data, partial data

**Bye cover**:
The bench player with the highest lineup value who can fill the slot a key starter on bye leaves open. A slot
with no such bench player has no cover.
_Avoid_: backup, replacement, fill-in

**Streak on the line**:
A storyline: a team enters next week on 3 or more head-to-head wins or losses in a row. The median game
does not count. The storyline names the length and the kind.

**Projected shootout**:
A storyline: both teams' best projected lineups for next week rank in the top four of the league. Not the
NFL shootout, which is a real game with a high total.
_Avoid_: shootout (alone, for the storyline), high-scoring game, track meet

**Rematch**:
A storyline: the two teams met earlier this season. The storyline names the week and the result. The
loser of that game also gets the revenge storyline.

**Swing**:
The playoff odds of both sides of one Must Watch game of next week: each side's odds after a win and
after a loss. The `SW.` fact gives it as "A win puts X at 71%, a loss at 38%."
An open side with a gap under `SWING_FLAT` reads "X stays near 60% either way." A side that is in or out
reads "X is in either way." or "X is out either way."
_Avoid_: swing player (that is a player who outscored the margin), leverage

**Impact fact**:
The `M<n>.impact` fact. It gives what this week did to each team of one matchup: the standings place
before and after, the cut, the playoff odds before and after, the median result, the streak, and a
clinch or an out. It lists only the parts that apply this week. The odds change is for the whole
week, not for the one game, so the text says "this week".
_Avoid_: stakes (that is before the game), swing (that is the Must Watch line), movement (that is the power rank)

**Standings place**:
The place of a team in the standings, from 1 to 12. It is not the power rank. A fact writes "rose
from 5th to 3rd in the standings", never "moved".
_Avoid_: rank (alone), move, movement

**Clinched**:
A team that is sure of a playoff spot by a plain check on wins. No team outside the playoff spots can
reach its wins, even with 2 wins in every week left. Use "in" in code and "In" on the page.
_Avoid_: locked, safe

**Out**:
A team that cannot reach the wins of the last playoff spot with 2 wins every week left. Use "out" in
code and "Out" on the page.
For a player, the page writes "listed Out" or names the injury.
_Avoid_: eliminated, dead

### The page

**Position leader**:
One of the three started players with the most points at one position this week, league wide.
_Avoid_: top scorer (that is the award and the per-team matchup fact)

**Headshot**:
The portrait of a player from the Sleeper image CDN, or the NFL team logo for a DEF. Fetched at
build time; a missing one shows the default silhouette.
_Avoid_: photo, avatar (that is the team image)

### Power rankings

**Power rank**:
The place from 1 to 12 by power score, for one week.

**Power score**:
The weighted mean of the four components, with the weights in `POWER_WEIGHTS`.

**Component**:
One of the four ranked inputs of the power score: standing, form, schedule played, scoring. Each has a rank of 1 to 12.
It is not a React component. The site names those a part or a primitive.
_Avoid_: schedule strength (for schedule played). Schedule played is distinct from the next
opponent win rate, which covers next week only.

**Form**:
The component for how a team plays now. It reads the last 3 weeks: the head-to-head game at double the
weight of the median game, and the all-play record.
_Avoid_: momentum, results (alone)

**All-play record**:
Wins and losses as if a team played every other team that week.

**Form streak**:
Wins or losses in a row over the last 3 weeks, newest game back, with the median game counted. A
head-to-head game counts 2 and a median game counts 1. The median game is the newer game of its week.
A tie ends it. It feeds the form component only.
_Avoid_: streak (alone). The streak fact on the page is head to head only.

**Quality win**:
A head-to-head win against a team in the top 4 of the standings of that week.

**Movement**:
Last week's power rank minus this week's. Positive is up.

**Rank why**:
The `PR.{rid}.why` fact. For a team that moved, it names this week's game and the component whose
rank changed most. For a team that held, it names its best and its worst component. The writer cites
it for every team that moved `WHY_MOVE_AT` or more places either way.

**Odds why**:
The `ODDS.{rid}.why` fact. It gives the projected pace, the season pace, and the rank of the
remaining schedule, the inputs behind the playoff odds. The writer cites it for a team under .500
with odds at or above `WHY_ODDS_AT` percent, and for a team over .500 with odds under it.

**Required fact**:
A fact id a prose block must cite, listed on the prose block and named in the writer prompt. The rankings
prose block requires the rank why of every mover and the odds why of a team whose odds and record disagree.
The code check fails a blurb that leaves one uncited by that team's sentences.
_Avoid_: mandatory fact, forced citation

**Projected pace**:
The mean of a team's projected best-lineup totals over the weeks left, rounded to a whole point.
_Avoid_: projection (alone).

**Season pace**:
The mean of a team's scores over the weeks played, rounded to a whole point. The rank of the
remaining schedule reads the season pace of the opponents left.

**Roster tag**:
The roster ID on a sentence of the rankings prose block. It names the team the sentence is about, so
the season file puts the sentence in that team's row. Other prose blocks leave it empty.

**Opener**:
The first sentence of a team in the rankings prose block. The code check compares its first 3 words,
with case and edge punctuation ignored.

**The cut**:
The last playoff spot. A standing fact for a team with the wins of that spot ends in one fixed
phrase: "in the last playoff spot" for the team in it, "level with the last playoff spot" for a
tied team above it, and "1 spot outside the playoff spots" or "2 spots outside the playoff
spots", and so on, for a tied team below it.

### Trades

**Trade**:
A Sleeper transaction that moves players or picks between two or more rosters.
_Avoid_: deal, swap (a swap the analyzer grades before it happens is a proposed trade)

**Trade window**:
The span of time whose trades belong to one week's page: from the Tuesday cutoff that opens the
week to the Tuesday cutoff that opens the next. Build time plays no part.

**Tuesday cutoff**:
08:00 Eastern on the Tuesday after a week's games. It opens the next week's trade window, so a
Tuesday or Wednesday trade belongs to the week whose games come next.

**Late trade**:
A trade made after the lineups locked, so the lineup shows the roster from before it.

**Trade card**:
The page element for one trade: one column per side with the team and the players it got, a FOR tag
between two sides.

### The analyzer

**Proposed trade**:
A proposed swap of players between two to four teams that the analyzer grades before it happens: the sides,
the players each gives, the destination of each given player, and which side asked.
_Avoid_: Trade (alone; that is the Sleeper transaction), deal, proposal, swap

**Rubric**:
The criteria the grade follows, their order, their caps, and what each letter means.
_Avoid_: criteria (alone), system, scoring

**Grade**:
The analyzer's letter, A to F, for one side of a proposed trade, formed by the rubric. The weekly
page shows no grade.
_Avoid_: score, rating

**Grade limit**:
The cap on analyze calls that reach Claude, per client address: 5 per minute and 20 per day.
A finder call counts one grade too. A cached repeat does not count.
_Avoid_: quota, rate limit (alone)

**Start letter**:
The letter the chart ratio gives one side before any adjuster.
_Avoid_: anchor, base grade

**Adjuster**:
One named criterion of the rubric that moves a grade by at most one step: roster fit, standing,
trend and usage, injury history, handcuff, schedule, or expected gap.

**Lineup**:
The best set of starters of one roster: which starting slot takes which player, who is out, and who covers a bye. It is a term of the league package, so every package reads the same lineup.
_Avoid_: Starters (alone), depth, best ball

**Lineup value**:
The points per game a player counts for in a side's best lineup, or his projection ahead when he is due back.
Inside the grade, the points per game are his season points per game, over the games he played. The weekly
report reads his points per game over the last 4 weeks. A player out for the season counts for 0.
_Avoid_: value (alone), worth

**Due back**:
A player the returns file lists with a return week after the last completed week, so he is out now and returns later.
_Avoid_: injured (alone), on the mend

**Breakdown**:
The start letter, every adjuster with its step, and the final letter, for one side.

**Contender**:
A team in a playoff spot by record.

**Seller**:
A team more than two games out of the last playoff spot.
_Avoid_: rebuilder, tanker

**Middle team**:
A team that is neither a contender nor a seller. The standing adjuster gives it no step.

**Highest-value player**:
The one player in a proposed trade with the most trade value, or the most recent points per game
when trade value does not compare.
_Avoid_: best player, top player

**Verdict**:
Accept, counter, or decline, for the side that asked, with one reason.
_Avoid_: recommendation, advice

**Decision**:
The page word for the verdict. The result document leads with it. Use "verdict" in code and
"decision" on the page.
_Avoid_: call, recommendation

**Answer**:
The decision as the page shows it: yes, no, or not as is. It maps from the verdict choice: accept
to yes, decline to no, counter to not as is. Use "choice" in code and "answer" on the page.

**Fairness**:
Whether a proposed trade is good for both sides, with one reason per side. It reads the final
letters that stand and has three states: good for both, fair, and lopsided. The rubric file sets
the bounds of each state. A lopsided trade names the side that gives more.
_Avoid_: balance, even trade

**Good for both**:
The page word for the win-win state of the fairness when the trade has two sides. With three or more sides the page word is "Good for all". Use "win_win" in code. The finder shows two-side trades, so it always says "Good for both".
_Avoid_: win-win on the page

**Finder**:
The code that grades every one-for-one and two-for-one trade between the asker's roster and one
partner roster, and returns the top three that are good for both. The rank is the net sum of the
adjuster steps on both sides, then the higher of the two lower final letters, then the smaller gap
between the two final letters, then the asker's letter. The three trades share no player. A handcuff,
a player out with no return week, and an unlisted player are never in a trade. The chart lists no
kicker and no defense, so they are always unlisted.
_Avoid_: suggested trades, counters (a counter changes one trade for one side)

**Finder document**:
The answer of the find route that the site renders: the season, the two teams, the as-of stamps, and up to
three trades. Each trade holds its two sides, its fairness block, and one reason that Claude writes. When the
Claude call fails twice, each reason is empty, the fairness block stands, and the document flags the fallback.
An empty list carries the line that no swap between these rosters is good for both.
_Avoid_: finder result, suggestions

**Factor**:
The page word for an adjuster. Use "adjuster" in code and "factor" on the page.
_Avoid_: criterion (alone)

**Deal row**:
The first factor of each side: the start letter as one plain sentence, such as "You get far more
than you give." It names no source. Its lean maps from the start letter: A and B to for, C to
even, D and F to against. Use "start letter" in code and "deal row" on the page.
_Avoid_: chart lean, The Data

**Silent row**:
A factor with no step and no new fact, such as "No player it gets is a handcuff." The adjuster marks it
silent, and the result document drops it. A row with a step always shows. A check that did not run is a
new fact, so its row shows. Use `silent` in code.
_Avoid_: empty row, hidden factor

**Roster row**:
The roster fit factor on the page. It counts the side's players in the top N at each position the trade
touches, before and after, where N is the line of the position as a plain rank: "You keep 3 WRs in the
top 36, and you get the better player." It never names a slot or the best lineup.
_Avoid_: hole sentence (on the page)

**Standing row**:
The standing factor on the page: the race of the side, its need, and whether the trade meets it, in one
sentence. "Out of the playoff race, so you want the better player for the rest of the season, and you
get him."

**Inner word**:
A word of the grade's code that a manager does not use: "trade value", "highest-value", "best lineup",
"the line", "hole", "win-now move", "return bet", "star", "opportunity", "one step", "no step", "takes RB",
"takes WR", "takes TE", "takes QB", and "sits on the bench". No bullet, row, or verdict reason holds one.
"The better player" replaces "the highest-value player". Decision 03 of grade-clarity.
_Avoid_: banned word (alone)

**Bullets**:
The 2 or 3 sentences that Claude writes for one side, one claim each. The fallback has none.
_Avoid_: analysis paragraph

**Factor lean**:
For, against, or even, for one factor. It maps from the sign of the adjuster's step, or from the
schedule lean for the schedule adjuster. Use "step" in code and "factor lean" on the page.

**Side shape**:
The exact two sides, in roster order, each once, that an analysis response must hold.

**Before the trade**:
Weeks 1 to N-1, for a proposed trade in week N. The standings, the chart week, the due-back rule, and the
injury report end there. Player stats end at the known games.

**Known games**:
Weeks 1 to N-1, plus every week N game that has a stat line on Sleeper, final or in progress. Every player
stat a grade reads ends there: points, snap share, target share, red zone touches, and the WOPR window.
_Avoid_: partial week, live stats, current week

**In progress**:
A week N game past its kickoff by less than 4 hours 30 minutes. The as-of stamp counts them, and every
factor reason that reads one says so.
_Avoid_: live game, ongoing

**Pending**:
A known game whose stat line lacks a count the grade wants, such as snaps on a Sunday night. The grade
skips that count for that game and never reads it as zero. The as-of stamp names what is pending.
_Avoid_: missing, late

**Trade value**:
A player's worth on the half-PPR redraft trade value chart for the week of the trade. It feeds the
start letter and never appears on a page.
_Avoid_: value (alone), chart value, price

**Chart week**:
The chart whose date falls in a week's trade window. A trade in week N uses the week N chart.

**Unlisted**:
A traded player with no row on the chart week's chart. He gets no trade value, so his side gets
no start letter and the rubric grades from the adjusters alone.

**Consolidation**:
A trade where one side gets more players than the other. A margin divides the sum of the side with more players
before the sides count as even. Two margins exist:

- The one-for-many margin, `CONSOLIDATION_MARGIN`, is 1.25. It is for one player for two or more.
- The uneven margin, `UNEVEN_MARGIN`, is 1.10. It is for any other uneven count, such as three for two.

**Handcuff**:
The backup to a roster's own starting running back. Insurance, never a player with no stats. A backup who
takes 25% or more of his team's carries over his last 3 played games is not a handcuff. He scores points of
his own, so every adjuster and the finder grade him as any running back. A handcuff blocks a lineup loss
in roster fit, never a hole. This gate reads his carries over
those 3 games from the Sleeper stat lines, not the one-game carry share from the play by play. With fewer
than 2 played games, or with no carry data, the depth chart alone decides.

**Position order**:
The tie rule the rubric uses at equal rank and points: RB over WR, WR over TE, TE over QB, QB over
K, K over DEF.

**Position rank**:
A player's place at his position among every player with a stat line in the known games, rostered or
not, by lineup value. RB24 is the 24th running back in the league, not on the 12 rosters. A player with
no game in the window ranks last. Inside the grade, the window is the season, so the rank sorts by season points
per game. The weekly report keeps the window of the last 4 weeks.
_Avoid_: positional rank, tier (alone), ranking

**Season rank**:
A player's place at his position by his total points this season, as Sleeper sorts it. It is the rank that the
text of a grade shows, such as WR60.
_Avoid_: overall rank, position rank (that is the measure inside the grade)

**Recent rank**:
A player's place at his position by points per game over the games he played in the last 4 weeks, with no due-back
step. A grade shows it only beside the Season rank, with its label, when the two differ by `RECENT_RANK_GAP` spots or
more.
_Avoid_: form rank, hot rank, rank (alone)

**Week line**:
The line of a grade that says, for one side and one week, how the trade changes the players who play that week at
each position the trade touches. It names byes, players listed Out or IR, players who step up, and the opponent of
each player the side gets with its rank at his position. The code writes it for the trade week and the next week. It
never moves the letter.
_Avoid_: weekly impact, matchup line, lineup fit

**Steps up**:
A player steps up for a week when the player directly ahead of him on his NFL team's depth chart, at his
position, is out for that week by the out rules of the Week line. The player ahead can be on no roster. A player who
is out himself, or whose team has a bye, does not step up. The Week line names no step-up when the newest depth chart
is more than `STEP_UP_CHART_HOURS` older than the grade, or when the grade has no time.
_Avoid_: promoted, next man up, starts (alone)

**The line**:
The last position rank a starter can hold: 36 at RB and WR, 24 at QB and TE. A flex slot reads the
line of the player's own position. K and DEF have no line.
_Avoid_: replacement level, floor, cutoff

**Hole**:
A starting slot that, after a trade, holds a player below the line or holds no player. A starter due back
inside the return window with no bench player above the line to cover him is a hole. A starter due back
after the return window is a hole. A starter out with no return week on file is a hole. For a middle team,
a player it gets who starts after the trade and has his bye in the trade week is a hole. A bye in any
other week, or on any other team, is never a hole. A hole that exists before the trade too is not new.
_Avoid_: gap, weakness, need, bye hole

**Return window**:
The trade week and the next two weeks. A starter due back inside it needs a bench player to cover him.
_Avoid_: bye window

**Depth**:
The count of a side's players at one position, starters and bench, above the line. It reads QB, RB,
WR, and TE, before and after a trade.
The depth word of a manager page counts a spare only inside the league's starter count at the position:
"stacked" with two spares, "deep" with one, "fine" with none, and "thin" with a hole.
_Avoid_: bench strength, room

**Strength**:
How many of a side's RB1, RB2, WR1, and WR2 starters hold a position rank of 24 or better. A starter
outside the top 24 but above the line is weak, not a hole.
_Avoid_: quality, power, tier (alone)

### Start or sit

**Pair**:
Two players on one roster that fit one lineup slot, which the manager asks the analyzer to compare for the
game week. QB with QB, K with K, DEF with DEF, and any mix of RB, WR, and TE.
_Avoid_: matchup (that is a player against a defense), duo

**Game week**:
The first week of the season with no scores. A start or sit decision is always for the game week.
_Avoid_: next week, upcoming week, current week

**Before the game**:
Weeks 1 to N-1, for a decision in game week N. Every fact on the start or sit fact sheet ends there.

**Either**:
The start or sit answer when the two players are too close to split: play either one. The other two answers
name the player to start.
_Avoid_: toss-up, close call, coin flip

**Source**:
The plain name of the dataset a fact came from, its week span, and a URL. Code writes every source. The page
shows one under each factor.
_Avoid_: citation, reference

### Player data from nflverse

**Target**:
A pass play with a receiver, two-point tries left out. The nflverse rule, which our count follows.
_Avoid_: look, pass attempt to

**Target share**:
A player's share of his team's targets in one game, from the nflverse weekly player file. Our own count is the fallback for a week the file lacks. The trade rubric reads the Sleeper share, which holds the same counts.
_Avoid_: target rate, target percent

**Air yards share**:
A player's share of his team's air yards in one game, from the nflverse weekly player file. It can be negative on a pass behind the line.
_Avoid_: aDOT share, depth share

**Carry share**:
A player's share of his team's carries in one game, in percent, from our own count of the play by play.
_Avoid_: rush share, touch share

**WOPR**:
Weighted opportunity rating: 1.5 times target share plus 0.7 times air yards share, per game, from the nflverse weekly player file. It is not a share, so it can pass 100 or go negative.
_Avoid_: opportunity share, volume score

**Expected points**:
What a player's volume should have scored in one game, from ffopportunity, rescaled to the league's half-PPR scoring.
_Avoid_: xFP, projected points (that is the Sleeper projection, before the game)

**Expected gap**:
A player's points in this league minus his expected points, per game. Positive is over expected, negative is under.
_Avoid_: luck, regression, variance

**Expected window**:
The last 3 games a player played, the span the expected gap averages over for the rubric. A player with fewer than 2 games in it has no gap.
_Avoid_: recent games, sample

**Pass rate over expected**:
How much more or less a team passes than the nflverse model expects, given down, distance, and score, per game.
_Avoid_: PROE, pass lean, neutral pass rate (that is the waiver board's older measure)

**Shootout**:
A next-week NFL game where both teams have a positive pass rate over expected over the last 3 games each played. A team with fewer games uses all of them.
_Avoid_: high-scoring game, fun matchup

**Unlucky award**:
The weekly award to the started player with the largest expected gap under zero, at least 5 points under. No award when no starter clears the floor.
_Avoid_: regression candidate

**Lucky award**:
The weekly award to the started player with the largest expected gap over zero, at least 5 points over. No award when no starter clears the floor.
_Avoid_: fluke, outlier

### The waiver page

**Waiver pool**:
Every player with a team, active, at QB, RB, WR, TE, K, or DEF, who is on no roster in this league.
Sleeper gives a defense no status, so an active defense counts on its active flag.
Sleeper gives an IR player the status Inactive. An active player with that status and an out injury status
joins the pool for stashes only. Every other bucket skips a player who is out.
Use "pool" in code and "free agents" on the page.
_Avoid_: free agent list, waiver wire (alone; that is the page)

**Bucket**:
One ranked list of the waiver board, such as the top pickups. It holds at most `BUCKET_SIZE` players and
at most `PER_POSITION` of one position. A player can sit in more than one bucket.
_Avoid_: tier, group, tab (a tab is the page control that shows one bucket)

**Top pickups**:
The bucket of the pool players with the best board score, at QB, RB, WR, or TE only. K and DEF stay
in the pool but never land in it. The code names it `best_adds`, and the waiver page tab says "Best".
_Avoid_: best adds (that is the look-back of a manager page), top adds

**Trending**:
The bucket of the pool players at QB, RB, WR, or TE with the most Sleeper adds in the last day.
_Avoid_: hot, buzz, most added

**Drop candidate**:
A rostered player at QB, RB, WR, or TE whose snap share fell `DROP_WEEKS` weeks in a row, and whose
rest of season projection is below the best pool player at his position. The drops bucket holds the
top `BUCKET_SIZE` drop candidates by the margin, with no cap per position. Each drop candidate names
the roster that holds him and the pool player who beats him. A drop candidate carries no price.
_Avoid_: cut, drop (alone; that is a transaction), sell

**Margin**:
The per-week rest of season projection difference between a drop candidate and the pool player who
beats him: the difference over weeks N+1 to 17, divided by the count of those weeks, to one decimal.
_Avoid_: gap (that is the swing's difference between a win and a loss), edge

**Sneaky add**:
A healthy pool player at QB, RB, WR, or TE whose usage trend score is in the top quarter and whose
projection score is in the bottom half, or who sits one depth chart slot below a player who is out. The
bucket ranks by usage trend, with the shared cap. A player in the top pickups is not a sneaky add. The reason code
is `usage_rise` or `behind_injury`.
_Avoid_: sleeper, deep add. Sleeper is the league app.

**Stash**:
A pool player at QB, RB, WR, or TE who is out with a return week inside the season and a rest of season
projection in the top half of his position. The returns file gives the return week first, the injury report
second. A handcuff counts too: an RB one slot below a healthy starter whose rest of season projection is in
the top half of every RB, rostered or not. A stash needs a rest of season projection above 0. The bucket
ranks by rest of season projection, with the shared cap. The reason code is `return` or `handcuff`.
_Avoid_: IR stash (alone), hold

**Story fact**:
The injury fact of a bucket entry behind an injured player: "{starter} is {status}, and {name} is next on the
depth chart." It comes from the injury status and the depth chart, names the starter in its players, and may be
empty.
_Avoid_: injury note, news fact

**Budget table**:
One row per roster with its FAAB budget left and its waiver order. The budget left is the league
budget minus the budget the roster used.
_Avoid_: FAAB table, bank

**Board score**:
The weighted sum of a pool player's three scores, each from 0 to 1: usage trend, environment, and
projection, with the weights of `BOARD_WEIGHTS`. The projection score is the rest of season
projection, weeks N+1 to 17, ranked inside the position. A score with no input counts 0.
_Avoid_: rank (that is the place in a bucket), value, power score

**Usage trend**:
The rise in a player's snap share plus his targets or carries share over the last `USAGE_WEEKS` weeks, ranked inside the position.
_Avoid_: momentum, buzz

**Environment**:
The team's rank in plays per game, plus neutral pass rate for a QB, WR, or TE, or rush success for an RB.
_Avoid_: situation, offense grade

**Snap share**:
The percent of the team's offensive snaps a player played in one week, from the nflverse snap counts.
_Avoid_: playing time, usage (alone)

**Neutral pass rate**:
The percent of passes on a team's neutral plays: first or second down, score within 7, first three quarters, not the half's last two minutes.
_Avoid_: pass rate over expected, PROE

**Rush success**:
The percent of a team's designed runs that nflverse marks as a success.
_Avoid_: rush efficiency, YPC

**Bid to win**:
The price of a pool player: the smallest whole dollar above the highest bid the model expects from any
rival. A rival's expected bid is his budget left times `NEED_SHARE` times the player's board score.
The need share is 0.35 when the rival has fewer healthy starters at the position than the lineup's
dedicated slots need. It is 0.12 otherwise. The most recent winning claim at the position in the last
`FLOOR_WEEKS` weeks raises the floor to that bid plus one. The price never exceeds the highest budget
left in the league. Every bucket but drops carries it, as a fact with its inputs in the numbers.
_Avoid_: value, cost, FAAB value

**Last like him**:
The most recent winning waiver claim at a pool player's position this season, with the player, the
team, the week, and the bid. Empty when no claim at the position won. The match is on position alone,
because a past claim has no bucket tier.
_Avoid_: comp, last comparable

**Research claim**:
One sentence from a web source about a ranked pool player, with its URL, the source name, the date, and
a stance: it backs the engine's facts, disputes them, or is plain news. The search reads only the last
7 days, Yahoo Fantasy first. A claim with no URL is dropped. Each player keeps at most
`CLAIMS_PER_PLAYER`, and at most `RESEARCH_PLAYERS` players get a search. The claims save as the fact
family `WV.research.{player_id}.{n}`. The fact ID is the citation. The URL is text the page shows. When the search fails for every
player, the board sets `experts_missing`. Use "experts" on the page.
_Avoid_: expert take (alone), quote, rumor

**Upside**:
The adjuster that credits a side for a player it gets who is a star return bet or who has an opportunity. It steps up or not at all, never down.
_Avoid_: potential, ceiling, buy low

**Star**:
A player with a chart value in the top of his position on the league's chart, such as the top 6 QB. `star_rank_by_position`
in the client sets the count per position. A position not in it has no stars.
_Avoid_: stud, elite, top guy

**Superstar**:
A player in the top 8 trade values of the week, over all positions. `SUPERSTAR_RANK` sets the count. Not every
star is a superstar. A superstar is not always a star: the Star rank of a position can be below 8, such as the top 6
QB. A week with no chart reads the newest saved chart of the two weeks before, and the reason then says "last week".
_Avoid_: stud, elite

**Star return bet**:
A star who is out now and is not out for the season. His return week may be missing. The injury adjuster does not count him against the side that gets him.
_Avoid_: injured star, stash

**Out for the season**:
A player the returns file marks with `season` in place of a return week. He counts zero chart value for the side that gets him.
_Avoid_: season-ending, done for the year, IR (alone)

**Opportunity**:
A player whose same-position teammate is out for the season or out with no near return, and whose snap share, target share, air yards share, or WOPR points up.
_Avoid_: breakout, vacated targets, opened role

**Best lineup**:
The starters a roster could have started for the most points, by the league's slots.
The best lineup of a week reads the real points.
The best lineups of the grade read the projections ahead and the points per game.
_Avoid_: Optimal lineup, perfect lineup, max lineup

**Move**:
One change to a roster in a week: an add from the waiver pool with its bid, or a trade.
_Avoid_: Transaction, pickup, acquisition

**Add**:
A move that brings a player onto a roster from the waiver pool, by a Sleeper waiver or free agent transaction. A trade is a move but not an add.
_Avoid_: Claim, pickup, signing

**Drop**:
A player taken off a roster and put in the waiver pool, in a week.
_Avoid_: Cut, release, waive

**Roster grade**:
The letter, A to D, that says how good a roster is now, from a 0 to 100 score of four parts.
The parts are the projection ahead, the season production, the trade value, and the depth and holes.
The slot ranks read the current roster by the projections ahead, never by recent points or injury status.
The file carries the rank of the roster on each part, from 1 to 12, and never the score.
The read is the grade in words from the slot ranks: strong in the top quarter, soft in the bottom quarter, deep with a spare, thin at a hole.
A stacked position reads "Deep" in the grade read.
_Avoid_: Score, rating, power score

### The platform

**Provider**:
The service the league's data comes from. Sleeper is the one provider today. The provider's field names stop at its adapter; the rest of the pipeline sees only the models.
_Avoid_: Source, platform, backend, API

**Bundle**:
The raw data, the history, and the facts of one week, loaded together before the writer runs. The code that builds a prose block reads the bundle and the client, and nothing else.
_Avoid_: Context, week data, state

**Published file**:
One JSON file the render step writes under the build folder `clients/<slug>/build/` and publish copies into `clients/<slug>/published/`: a week page, a waiver board, the rankings, the managers file. The pipeline owns its shape, and the site reads it with one loader.
_Avoid_: Snapshot, data file, output, artifact, feed, export

### The midseason report

**Midseason report**:
The one page per season that recaps the season to date for one client: arcs, steals and busts, waiver pickups, trades, schedule luck, and the sim of the weeks left. Brian runs its build by hand for one week, and it does not rebuild each week.
_Avoid_: Season recap, halftime report, mid-year review

**Arc**:
The shape of one team's season to date, found from the data, from a fixed set such as a turnaround or a collapse. An arc is about a team's season. A Storyline is about one next-week game.
_Avoid_: Storyline (that is the reason a next-week game matters), narrative, story

**Draft value**:
A player's points to date against his draft cost in his league's own draft: dollars in an auction, pick number in a snake. It names a steal or a bust.
_Avoid_: Value (alone), ADP, Trade value (that is the chart worth of a player)

**All-play wins**:
The sum of a team's weekly all-play win rates, a tie counted as half. It is the number of head-to-head wins that the team's scores earned with an average schedule. The report page labels it "Wins if you played everyone", because readers do not know the term.
_Avoid_: Expected wins (Expected points is a player term), projected wins

**Schedule luck**:
A team's head-to-head wins minus its All-play wins, for weeks 1 to the report week. The median game stays out. Positive is lucky. It is a team measure, not the Lucky award or the Unlucky award of a player.
_Avoid_: Luck (alone), overachiever (a prose word only), expected gap (that is a player term)

**Schedule swap**:
A team's record with another team's schedule and its own scores. In the week that the other team played it, the team plays the other team. A median game keeps its own result, so the real schedule gives the real record.
_Avoid_: Schedule strength, what-if record

**Roast setting**:
The voice of a client's report prose: `off`, `warm`, `hot`, or `savage`. It sets the voice of the whole paragraph, not one sentence. Every level keeps to football and cites real facts.
_Avoid_: Heat, roast level, tone

**Quick hits**:
The block at the end of Act II of the midseason report that holds lineup choices and the injury toll.
_Avoid_: Odds and ends, misc, extras

**Injury toll**:
The starter games that a team lost to injury, by NFL week. It is a cost, not a chance.
_Avoid_: Injury luck

**Position top 10**:
The 10 players with the most points at one position, weeks 1 to the report week, in the league's own scoring. Every NFL player counts, rostered or not. It is the league-wide list of the midseason report.
_Avoid_: Top performers (that is a team's own starters on the manager page), Position leader (that is the top 3 of one week)

**Opener**:
The top of the midseason report: the title race, with the title odds of the leaders and of the record leader.
_Avoid_: Hero (that is the top of a manager page), cover, banner

**Act**:
One of the three parts of the midseason report, each opened by a dark title page: How we got here, The moves, and What comes next.
_Avoid_: Section, part

**Spread rule**:
Each team gets at least one and at most three headlines in the midseason report: a callout, an award, or an arc.
_Avoid_: Fairness rule, balance

**Headline**:
One mention of a team as the subject of the midseason report: a callout, an award, or an arc. The opener and a table row are not headlines.
_Avoid_: Mention, feature

**Callout**:
A headline that names the #1 team of a ranking in a chapter, such as the biggest steal of the draft. When the #1 team holds three headlines, the callout names the next team, and the table still shows every team.
_Avoid_: Highlight, spotlight

**Takeover**:
The weeks when the home page shows the midseason report in place of its usual top, through the report week plus 1.
_Avoid_: Banner, promo

**Report tile**:
The home tile with one big fact and a link to the midseason report. It stays after the takeover ends.
_Avoid_: Card, teaser

**Sim run**:
One stored season of the sim, with every team's score for each week left. The replay plays one sim run per press.
_Avoid_: Simulation, sample, scenario

**Points over the line**:
A player's points in one start minus that week's score at the line of his position: RB36, WR36, or TE24. It ranks the waiver pickups of the midseason report. K and DEF have no line, so they have none.
_Avoid_: Points over replacement, VORP, value over replacement

**Swung win**:
A win of a team that the points of one of its starters decided: the team won, and that starter scored more than the margin.
_Avoid_: Clutch win, game winner, difference maker

**Trade result**:
The midseason report's label for one past trade, from the net Points over the line of each side since the trade: Robbery, Clear win, Slight edge, Push, or Too soon.
_Avoid_: Grade (that is the analyzer's letter for a proposed trade), hindsight grade, trade score

## Client language

The terms of the structure that both apps share: the clients, the packages, and the apps.

**Client**:
One league and its site, over every season. A client has one provider per season, its own packages, its own brand, and its own URL. Its slug is the league slug.
_Avoid_: League config, tenant, customer, instance, site

**Brand**:
The identity of one client: the color roles, the logo, and the copy. A brand gives a light set and a dark set of colors. It paints the look. It lives in `brand.toml`.
_Avoid_: Theme, skin, style, palette, look

**Look**:
The fonts, the radii, the layout, the components, and the motion that every client shares. Each brand paints the look with its colors.
_Avoid_: Design system, shell, report look, style, skin

**Readability floor**:
The four rules that each page of the site meets in each client, each theme, and each width: the text size, the contrast, the tap targets, and no sideways scroll.
_Avoid_: Floor (alone), a11y checks, quality bar

**Prose**:
Text that is a sentence, such as a blurb, a recap, or an error line. The readability floor holds prose to a larger size than other text.
_Avoid_: Body text, copy, paragraph

**Build folder**:
The folder `clients/<slug>/build/` of one client: each page file and season file that its build writes. Publish copies one week of it into the published data of the client.
_Avoid_: Site folder, output folder, dist

**Base role**:
One of the six colors that a brand must set in each set: the accent, the band, the page, the card, the text, and the muted text.
_Avoid_: Primary color, brand color, palette

**Derived role**:
A color that the design package computes from the base roles with a formula, such as the accent text or the lifted card. A brand can override it.
_Avoid_: Computed color, secondary color, shade

**Package**:
One domain of the league, in both languages: the rules, the ports, the fakes, the parts, and the screens. A client takes a package or omits it as a whole.
_Avoid_: Module, feature, plugin, library, lib

**League package**:
The one package that each client takes: the shape of any league, with its rosters, weeks, players, history, and provider. It names no client.
_Avoid_: Core, common, shared, base, utils

**Chapter port**:
The port of the week package through which another package gives one chapter of the weekly report: its facts and its chapter. The week owns the page and the order of the chapters. A client that omits the package gets a week with no such chapter.
_Avoid_: Plugin, hook, slot, extension point

**Design package**:
The one site package that each client takes: the primitives, the parts, the shell, and the code that applies a brand. It holds no rule of the league, so its name is not a league word.
_Avoid_: Design system, UI kit, components, parts (alone; a part is one component of it)

**League settings**:
The sizes of one season of a league that the provider gives: the team count, the playoff spots, the roster slots, and the weeks of the regular season. The lines and the star ranks derive from them.
_Avoid_: League config, sizes (alone), league rules

**Median game**:
The second game of each week, against the median score of the league. A league has it or not, and the League settings say which. With no median game, a week is one game.
_Avoid_: All-play, league average game

**Returns file**:
The one shared NFL file that names the week each injured player returns. A return week is the same in each league, so no client owns the file.
_Avoid_: Injury file, return list, returns.json (alone; that names the old file of one season)

**Package value**:
One value that a package names in its README, with its default. A client sets it in `client.toml` only when it differs from the default.
_Avoid_: Flag, feature flag, setting, option

**App**:
One thing that we deploy, such as the site or the API. An app holds only the build config, the routes, and the code that wires the packages. It holds no rule of a domain.
_Avoid_: Shell (that is the frame of a page), service, project

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

**Test verdict**:
The word PASS, FAIL, or BLOCKED that Brian gives to one acceptance test. Only a test verdict counts toward a merge.
_Avoid_: Verdict (alone; that is the answer of the analyzer), result, approval, sign-off, status

**Evidence**:
The files and the observation that show what the finished work does for one acceptance test. It holds no Test verdict.
_Avoid_: Proof, result, QA output
