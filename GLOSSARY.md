# Cornerstone Weekly

The weekly report page for the Cornerstone fantasy football league. It turns Sleeper and nflverse
data into facts, the facts into chapters of prose, and the chapters into page data for the site.

## Language

### The sheet

**Fact**:
One sentence of true data with an ID, the numbers it holds, and the teams and players it names.
_Avoid_: stat, data point

**Fact sheet**:
Every fact of one week plus the chapters that cite them.

**Chapter**:
One unit of prose on the page, with the fact IDs it may cite and the sentence range it must fit.
_Avoid_: section, blurb (a blurb is the written output, a chapter is the brief)

**Blurb**:
The sentences the writer wrote for one chapter, each with the fact IDs it cites.

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
The Claude call that turns one chapter and its facts into a blurb.

**Verifier**:
The code check and the Claude check that reject a blurb with an uncited number or claim.
The code check does not match the last name of an out-of-scope player when that name is a word of
a scope team name. So a bare "London" passes when London Cooking is in scope.
The full name "Drake London" still fails.

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
_Avoid_: chance, probability, projection (that is a player's projected points)

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

**Clinched**:
A team that is sure of a playoff spot by a plain check on wins. No team outside the playoff spots can
reach its wins, even with 2 wins in every week left. Use "in" in code and "In" on the page.
_Avoid_: locked, safe

**Out**:
A team that cannot reach the wins of the last playoff spot with 2 wins every week left. Use "out" in
code and "Out" on the page.
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
One of standing, form, schedule played, scoring. Each has a rank of 1 to 12.
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
A fact id a chapter must cite, listed on the chapter and named in the writer prompt. The rankings
chapter requires the rank why of every mover and the odds why of a team whose odds and record disagree.
The code check fails a blurb that leaves one uncited by that team's sentences.
_Avoid_: mandatory fact, forced citation

**Projected pace**:
The mean of a team's projected best-lineup totals over the weeks left, rounded to a whole point.
_Avoid_: projection (alone).

**Season pace**:
The mean of a team's scores over the weeks played, rounded to a whole point. The rank of the
remaining schedule reads the season pace of the opponents left.

**Roster tag**:
The roster ID on a sentence of the rankings chapter. It names the team the sentence is about, so
the season file puts the sentence in that team's row. Other chapters leave it empty.

**Opener**:
The first sentence of a team in the rankings chapter. The code check compares its first 3 words,
with case and edge punctuation ignored.

**The cut**:
The last playoff spot. A standing fact for a team with the wins of that spot ends in one fixed
phrase: "in the last playoff spot" for the team in it, "level with the last playoff spot" for a
tied team above it, and "1 spot outside the playoff spots" or "2 spots outside the playoff
spots", and so on, for a tied team below it.

### Trades

**Trade**:
A Sleeper transaction that moves players or picks between two or more rosters.

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
A trade the analyzer grades before it happens: two sides, the players each gives, and which side
asked.

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

**Lineup value**:
The points per game a player counts for in a side's best lineup: his recent points per game, or his projection ahead when he is due back.
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
The page word for the win-win state of the fairness. Use "win_win" in code and "good for both" on
the page.
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

**Chart lean**:
More, even, or less: how the trade values lean for one side. It maps from the start letter: A and
B to more, C to even, D and F to less. Use "start letter" in code and "chart lean" on the page.

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
A trade of two or more players for one. The depth side's values must sum to a margin above the one
player before the sides count as even.

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
no game in the window ranks last.
_Avoid_: positional rank, tier (alone), ranking

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
One ranked list of the waiver board, such as best adds. It holds at most `BUCKET_SIZE` players and
at most `PER_POSITION` of one position. A player can sit in more than one bucket.
_Avoid_: tier, group, tab (a tab is the page control that shows one bucket)

**Best adds**:
The bucket of the pool players with the best board score, at QB, RB, WR, or TE only. K and DEF stay
in the pool but never land in it.
_Avoid_: top adds, pickups

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
bucket ranks by usage trend, with the shared cap. A player in best adds is not a sneaky add. The reason code
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
A player with a chart value in the top of his position on the league's chart, such as the top 6 QB. `STAR_RANK_BY_POSITION`
sets the count per position. A position not in it has no stars.
_Avoid_: stud, elite, top guy

**Star return bet**:
A star who is out now and is not out for the season. His return week may be missing. The injury adjuster does not count him against the side that gets him.
_Avoid_: injured star, stash

**Out for the season**:
A player the returns file marks with `season` in place of a return week. He counts zero chart value for the side that gets him.
_Avoid_: season-ending, done for the year, IR (alone)

**Opportunity**:
A player whose same-position teammate is out for the season or out with no near return, and whose snap share, target share, air yards share, or WOPR points up.
_Avoid_: breakout, vacated targets, opened role
