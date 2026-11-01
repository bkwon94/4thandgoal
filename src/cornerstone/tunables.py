"""
The tunable table: every algorithm number of the trade analyzer rubric, the power rankings, the playoff odds,
the waiver board, and the next-week storylines. The numbers that change with the size of the league are in config.py.
Each has a name and a reason. The rubric file in the prompts directory points here, so a number changes in one place.
"""
from decimal import Decimal

# The numbers are Decimal, so a ratio at a lower bound, such as 22 over 20, lands in its band exactly.

# Start letter bands on the ratio of trade value got over trade value gave. Each lower bound is inclusive.
# The lowest ratio that starts a side at A.
BAND_A = Decimal("1.25")
# The lowest ratio that starts a side at B.
BAND_B = Decimal("1.10")
# The lowest ratio that starts a side at C.
BAND_C = Decimal("0.90")
# The lowest ratio that starts a side at D. A ratio below it starts the side at F.
BAND_D = Decimal("0.75")

# The bands from the top down. A ratio below the last bound starts at F.
START_LETTER_BANDS: tuple[tuple[Decimal, str], ...] = ((BAND_A, "A"), (BAND_B, "B"), (BAND_C, "C"), (BAND_D, "D"))

# A side that gives one player for two or more, or two or more for one, divides the sum of the two or more by this.
CONSOLIDATION_MARGIN = Decimal("1.25")

# Roster fit and standing compare a side's best lineup before and after the trade.
# The count of completed weeks whose points per game pick the best lineup. Fewer weeks use what exists.
LINEUP_WEEKS = 4
# The change in the best lineup's total points per game that counts as a gain or a loss.
# The value is a first guess, and the commissioner tunes it.
FIT_THRESHOLD = Decimal("3.0")

# Trend and usage compares snap and target share over the last weeks against the same count of weeks before them.
# The count of scored weeks in each window. The share helpers in history.py read it, so both windows change here.
SHARE_WEEKS = 2
# The change in mean WOPR between the two windows that counts as up or down. WOPR is 1.5 times target share plus
# 0.7 times air yards share. The 8 counts only the target share part: 1.5 times a 5-point share swing is about 8.
WOPR_SWING = 8

# Injury: a player the side gets who is out now, or who was on the injury report in many weeks, is a step down.
# The count of weeks on the injury report, through the last completed week, that makes a player injury-prone.
INJURY_WEEKS = 3
# A player who is out now is a near return when his return week is no later than the trade week plus this count.
# The hole read uses the same window, GLOSSARY.md "Return window", so a starter due back inside it needs a bench
# player to cover him. Three weeks is the trade week and the next two. A pickup or another trade can rarely fix a
# slot sooner.
RETURN_WINDOW_WEEKS = 2

# Handcuff: a backup to the roster's own starting running back is insurance only when he carries the ball little.
# A backup who takes 25% of his team's carries scores points of his own, so he counts as a running back.
# A pure backup sits near 15%. A backup with a real role, such as Blake Corum at 28%, sits above 25%.
# The gate compares the exact share, so 24.6% stays a handcuff.
HANDCUFF_CARRY_SHARE = 25
# The carry share reads his last 3 played games, so one big game cannot free him alone.
HANDCUFF_CARRY_GAMES = 3
# With fewer played games than this, the share is too thin to read, so the depth chart answer stands.
HANDCUFF_MIN_GAMES = 2

# Schedule: byes left and the playoff opponents of the players it gets against the players it gives.
# It never moves a letter.
# The gap in the mean rank of the week 15 to 17 opponents, in points allowed to the position, that makes a lean.
# Set this number by hand. The commissioner tunes it.
SCHEDULE_RANK_GAP = 4

# Expected gap: the league points of the players it gets and gives against their expected points over the window.
# The mean gap, in points per game, at or past which a group counts, either way, for the gets and for the gives.
# Gets under or gives over step a side up. Gets over or gives under step it down.
# The value is a first guess, and the commissioner tunes it.
EXPECTED_GAP = Decimal("3.0")
# The expected gap adjuster is off until a real trade checks out, so no live breakdown shows an untried adjuster.
EXPECTED_ADJUSTER_ON = False

# The chart ratio picks the start letter. The sum of the adjuster steps clamps to this many steps either way,
# so a side that starts at C never ends at A or F, and the chart weighs more than the adjusters.
CLAMP_STEPS = 1

# The verdict for the side that asked reads its final letter.
# The lowest final letter that accepts outright.
ACCEPT_AT_OR_ABOVE = "B"
# The highest final letter that declines outright. A letter between the two bands accepts when the other side's
# final letter is no better, and counters when it is better. The schedule lean can turn that middle result.
DECLINE_AT_OR_BELOW = "D"

# The fairness of a trade reads the final letter of both sides, so it says whether the other side will take it.
# The lowest final letter of both sides that makes a win-win. At B a side gets more than it gives, so both win.
WIN_WIN_AT_OR_ABOVE = "B"
# The highest final letter of either side that makes a trade lopsided. At D a side gives more than it gets.
LOPSIDED_AT_OR_BELOW = "D"

# The API service: the count of requests one client address may make in a fixed one-minute window.
# Past it the route answers 429, so one browser cannot loop the API and run up the Claude bill.
RATE_LIMIT_PER_MINUTE = 10

# The analyze route: the count of grades one client address may get in a fixed one-minute window.
# Each grade that misses the result cache is a Claude call, so this caps the Claude bill from one browser.
GRADES_PER_MINUTE = 5
# The analyze route: the count of grades one client address may get in one calendar day in Eastern time.
# It caps the Claude bill from one browser over a day, and the count lives on the volume so a deploy keeps it.
GRADES_PER_DAY = 20

# The teams route: the seconds it answers one season from memory before it builds the teams again.
# Each build fetches Sleeper, so the trade form fills at once. A trade or a waiver claim shows within this window.
TEAMS_CACHE_SECONDS = 300

# The finder: the count of win-win trades it returns at most for one pair of rosters.
# A short list is one a manager reads, and three trades with no shared player each stand as a real choice.
FINDER_TOP = 3

# The form component counts two games a week, each with a weight in the record and the streak.
# A head-to-head loss costs a game in the standings and a median loss does not, so the head-to-head game weighs more.
# Both games still show how a team plays, so the median game stays in.
FORM_HEAD_TO_HEAD_WEIGHT = 2
FORM_MEDIAN_WEIGHT = 1

# The power score is the weighted mean of the four components, keyed by component.
# Recent form is what the league wants the rank to show, so form weighs most. Scoring is second.
POWER_WEIGHTS = {"standing": 0.10, "form": 0.60, "schedule_played": 0.10, "scoring": 0.20}

# The playoff odds engine: a Monte Carlo of the remaining weeks, one table per run.
# The count of runs. At 5,000 runs one percent is 50 runs, so the sample error of an odds number is under 1 percent.
SIM_RUNS = 5000
# The count of latest played weeks that weigh more in the score draw, so the draw follows the current form.
RECENT_WEEKS = 3
# The weight of each recent week in the score draw. An older week weighs 1. At 1.25 with 6 weeks played,
# the last 3 weeks are 56 percent of the draws; at 2 they are 67 percent, too much trust in 3 scores.
RECENT_WEIGHT = 1.25
# The share of the gap from a team's season average to its projected best-lineup total that moves each drawn score.
# Past scores know the team's level, and the projection knows that week's roster. Half each, Brian's call.
PROJECTION_WEIGHT = 0.5
# The lowest playoff odds, in percent, that show the most likely seed.
# Below it the seed rests on fewer than half the runs.
SEED_SHOW_AT = 50
# The least gap, in points, between a side's win and loss odds that counts as a swing.
# A smaller gap is noise, not a stake.
SWING_FLAT = 5

# The why facts. Rule 25 of the writer prompt holds these two numbers as digits, so change rule 25 too.
# The least move, in places either way, that makes the writer cite the rank why.
# A 1-place move needs no reason on the page.
WHY_MOVE_AT = 2
# The odds, in percent, that make a record and its odds disagree: under .500 at or above it, or over .500 under it.
WHY_ODDS_AT = 25

# The waiver board ranks the waiver pool into buckets.
# The weights of the three board scores. Usage leads and projection is a tiebreak, because the projection
# lags the usage.
BOARD_WEIGHTS = {"usage": 0.5, "environment": 0.3, "projection": 0.2}
# The count of players in a bucket. Eight fit the field and the list of the page on a phone.
BUCKET_SIZE = 8
# The most players of one position in a bucket, so one position does not fill it.
PER_POSITION = 3
# The positions of every ranked bucket. K and DEF have no usage or environment score, so a projection score
# ranked inside the position would put the top of each in best adds every week. Kickers also fill the trending
# adds, as live data showed. They stay in the pool.
BUCKET_POSITIONS = ("QB", "RB", "WR", "TE")
# The positions of the waiver pool. Here and not in the engine, so the Sleeper client imports it with no cycle.
POOL_POSITIONS = ("QB", "RB", "WR", "TE", "K", "DEF")
# The count of latest weeks the usage trend reads. The trend is the change from the first of these weeks
# to the last, so 2 compares last week with the week before.
USAGE_WEEKS = 2
# The count of falls in a row of a rostered player's snap share that make him a drop candidate. One or two
# falls can be a game script or a blowout, and three is a role that shrinks.
DROP_WEEKS = 3
# The count of latest weeks of usage the nflverse extract saves. DROP_WEEKS falls in a row take one more week
# than the falls, so the extract follows DROP_WEEKS. The usage trend reads only the last USAGE_WEEKS of them.
USAGE_SAVED_WEEKS = DROP_WEEKS + 1
# The share of his budget left that the model expects a rival to bid on a player with a board score of 1.
# "need" is for a rival with fewer healthy starters at the position than the lineup needs, "covered" for any other.
NEED_SHARE = {"need": 0.35, "covered": 0.12}
# The count of weeks, N-2 to N, whose most recent winning claim at a position sets the price floor. One old
# big win, such as $41 for an RB in week 3, must not set the price of every RB all season.
FLOOR_WEEKS = 3
# The least usage score of a sneaky add: the top quarter of the risers at his position.
SNEAKY_USAGE_FLOOR = 0.75
# The least projection score in the top half of a position. A score under it is in the bottom half.
TOP_HALF = 0.5

# The research step asks the web for research claims on the ranked players.
# The most players the research step reads per build. Each one is one Claude call with web search, at about
# $0.14 per player with tokens, so 32 players cost about $4.50 a week. 32 covers four full buckets of 8 when
# none repeats. Prices from https://platform.claude.com/docs/en/about-claude/pricing, read 2026-10-23.
RESEARCH_PLAYERS = 32
# The most research claims kept per player. The sheet has room for two lines under the facts, and a third
# claim is most often a repeat of the first two.
CLAIMS_PER_PLAYER = 2
# The most web searches in one research call. The prompt has four steps: the Yahoo waiver column, the Yahoo
# author pages, the wider web, and one spare for a step that gave nothing. Each search costs $0.01.
RESEARCH_SEARCHES = 4

# The refresh: the seconds after which the refresh fetches the injuries file and the player weeks file again.
# Injury status and snap counts change on game days, so a day-old file would miss Sunday on a Monday morning grade.
# Every other nflverse source keeps the day of CACHE_MAX_AGE_SECONDS.
FAST_SOURCES_MAX_AGE_SECONDS = 6 * 60 * 60

# The known games: a week N game is in progress when the clock is past its kickoff by less than this.
# An NFL game takes about 3 hours 15 minutes. Overtime and weather delays add more, so the extra time keeps
# a long game in progress until it ends. GLOSSARY.md, "In progress".
IN_PROGRESS_MINUTES = 4 * 60 + 30

# The next-week storylines: the weight of each kind. GLOSSARY.md, "Storyline". A game's storyline score is the sum,
# and the two games with the highest score are Must Watch. Stakes and a streak count most, because a reader feels
# them every week. A shootout and the top of the table count next. A rematch and revenge only add color.
# The order is the order of the reason when two weights tie: a streak comes before near the cut.
STORYLINE_WEIGHTS = {"streak": 3, "cut": 3, "shootout": 2, "table": 2, "rematch": 1, "revenge": 1}

# The key starter: GLOSSARY.md, "Key starter", and ADR 0006. The rule reads real starts, so it shows the habit of
# the manager.
# The count of latest completed weeks the rule reads.
KEY_STARTER_WEEKS = 4
# The starts in those weeks that make a key starter. Three of four lets one benched or hurt week pass.
KEY_STARTER_STARTS = 3
# The starts a key starter needs when fewer than KEY_STARTER_WEEKS weeks are complete. It is also the fewest weeks
# the rule reads, because one start in one week says nothing about a habit.
KEY_STARTER_SHORT_STARTS = 2

# The roster grade: GLOSSARY.md, "Roster grade". The score is 0 to 100, the sum of four parts, each 0 to 1, times
# its weight. The weights sum to 100, so a roster with every part in full scores 100.
GRADE_WEIGHTS = {
    # The projection ahead weighs most: the starters against the line and the best lineup against the league, by
    # the projections to the end of the regular season. The rest of the season is what the grade says the most of.
    "projection": 45,
    # The season production weighs next: the best lineup by the points per game so far. A projection can miss a
    # player who scores, and the points already scored are a fact.
    "production": 30,
    # The trade value of the whole roster, bench included, against the league, weighs least. The chart reads a
    # player as the market prices him, so it sees a strong bench the starters do not show. But a market price is
    # not points, so it says the least of the season ahead.
    "trade_value": 10,
    # The depth and the holes, as one part. A hole is a slot no one can start in. A bench player above the line
    # only scores when a starter misses a game, so the part weighs under production but over the trade value.
    "depth": 15,
}
# The share of the holes part that one hole takes away. Four holes leave none, and a fifth costs nothing more.
GRADE_HOLE_COST = 0.25
# The players above the line past the starters at a position that give the depth part in full. One spare per
# position covers one missed game at a time.
GRADE_DEPTH_SPARES = 1
# The depth word of a position on the manager page counts a spare only inside the league's starter count at the
# position. 12 teams start 1 QB, 2 RB, 2 WR, and 1 TE, flex aside. The line is looser, so a QB16 is startable.
# He is a backup, not a second good player. Two spares read "stacked", one reads "deep", none reads "fine".
GRADE_SPARE_RANK = {"QB": 12, "RB": 24, "WR": 24, "TE": 12}
# The lowest score of each letter, best first. A score under the last band is a D. A report card reads A to D.
# Each part puts the league's worst roster at 0 and its best at 1, so a median roster scores near 50. The bands
# put that roster at C, so the letters spread A to D across a league and the middle of the league is not a D.
GRADE_BANDS = (("A", 70), ("B", 55), ("C", 40))
# The slot rank that reads "strong" in the grade sentence, and the one that reads "soft". The top quarter of a
# 12-team league is strong, and the bottom quarter is soft.
GRADE_STRONG_RANK = 3
GRADE_SOFT_RANK = 10
GRADE_BELOW_BANDS = "D"
