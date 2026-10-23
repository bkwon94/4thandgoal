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

**All-play record**:
Wins and losses as if a team played every other team that week.

**Form streak**:
Wins or losses in a row over the last 3 weeks, newest game back, with the median game counted. The
median game is the newer game of its week. A tie ends it. It feeds the form component only.
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
trend and usage, injury history, handcuff, or schedule.

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
Weeks 1 to N-1, for a proposed trade in week N. Every grade input ends there.

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
The backup to a roster's own starting running back. Insurance, never a player with no stats.

**Position order**:
The tie rule the rubric uses at equal rank and points: RB over WR, WR over TE, TE over QB, QB over
K, K over DEF.
