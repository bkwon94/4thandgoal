"""
The tunables of the waiver package: every algorithm number of the waiver board, its price, and its research step.
Each has a name and a reason. The shared numbers of the league kernel sit in league/tunables.py.
"""

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
