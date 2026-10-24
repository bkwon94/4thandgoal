"""
The tunable table: every number of the trade analyzer rubric, the power rankings, the playoff odds, and the waiver board.
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

# In a one-for-two-or-more trade, both ratios use the depth side's sum divided by this.
CONSOLIDATION_MARGIN = Decimal("1.25")

# Roster fit and standing compare a side's best lineup before and after the trade.
# The count of completed weeks whose points per game pick the best lineup. Fewer weeks use what exists.
LINEUP_WEEKS = 4
# The change in the best lineup's total points per game that counts as a gain or a loss.
# The value is a first guess, and the commissioner tunes it.
FIT_THRESHOLD = Decimal("3.0")

# Standing: a contender holds a playoff spot by record, and a seller is far out of the last spot.
# The count of playoff spots. The league ranks by wins, then by points for. The weekly facts read it too.
PLAYOFF_SPOTS = 6
# A seller has more than this many wins fewer than the team in the last playoff spot.
# The league scores a median game each week, so each week gives two results, and two games are one week of results.
SELLER_GAP = 2
# The last week of the regular season. When the side gets a player who is due back by this week, the trade is a return bet.
RETURN_BY_WEEK = 14

# Trend and usage compares snap and target share over the last weeks against the same count of weeks before them.
# The count of scored weeks in each window. The share helpers in history.py read it, so both windows change here.
SHARE_WEEKS = 2

# Injury: a player the side gets who is out now, or who was on the injury report in many weeks, is a step down.
# The count of weeks on the injury report, through the last completed week, that makes a player injury-prone.
INJURY_WEEKS = 3
# A player who is out now is a near return when his return week is no later than the trade week plus this count.
RETURN_WINDOW_WEEKS = 2

# Schedule: byes left and the playoff opponents of the players it gets against the players it gives. It never moves a letter.
# The gap in the mean rank of the week 15 to 17 opponents, in points allowed to the position, that makes a lean.
# Set this number by hand. The commissioner tunes it.
SCHEDULE_RANK_GAP = 4

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

# The power score is the weighted mean of the four components, keyed by component.
# The weights are equal so the rank is one line to explain.
POWER_WEIGHTS = {"standing": 0.25, "form": 0.25, "schedule_played": 0.25, "scoring": 0.25}

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
# The lowest playoff odds, in percent, that show the most likely seed. Below it the seed rests on fewer than half the runs.
SEED_SHOW_AT = 50
# The count of top seeds that get a bye. The bracket gives seeds 1 and 2 a bye in week 15.
BYE_COUNT = 2
# The least gap, in points, between a side's win and loss odds that counts as a swing. A smaller gap is noise, not a stake.
SWING_FLAT = 5

# The why facts. Rule 25 of the writer prompt holds these two numbers as digits, so change rule 25 too.
# The least move, in places either way, that makes the writer cite the rank why. A 1-place move needs no reason on the page.
WHY_MOVE_AT = 2
# The odds, in percent, that make a record and its odds disagree: under .500 at or above it, or over .500 under it.
WHY_ODDS_AT = 25

# The season edges. The regular season ends at week 14. The playoff bracket, not the round robin, decides later weeks.
LAST_REGULAR_WEEK = 14
# The last week of the NFL fantasy season. A waiver add plays the fantasy playoffs too, so his rest of
# season projection runs to this week.
LAST_SEASON_WEEK = 17

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
