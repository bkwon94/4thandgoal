"""
The tunable table: every algorithm number of the power rankings, the playoff odds, and the waiver board.
The week package holds the numbers of the week in week/tunables.py, and the analyzer keeps its own numbers in
packages/analyzer. The numbers that change with the size of the league derive from league_settings.py.
Each has a name and a reason.
"""


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
# The weight of the league average in a roster's level is k over n plus k, with k this count of weeks.
# At 5 with 7 weeks played, the roster's own average carries 58 percent. On week 7, k from 3 to 8 lands within 3 points.
LEVEL_SHRINK_WEEKS = 5
# The share of the gap from a team's season average to its projected best-lineup total that moves each drawn score.
# Past scores know the team's level, and the projection knows that week's roster. Half each, Brian's call.
# The gap reads from the raw average, so at 1 a draw is the shrunk level plus the full gap, not the projection itself.
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
# The count of latest weeks the usage trend reads. The trend is the change from the first of these weeks
# to the last, so 2 compares last week with the week before.
USAGE_WEEKS = 2
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
