"""
The tunable table: every algorithm number of the waiver board and the roster grade.
The week, the rankings, and the analyzer packages each keep their own numbers in their own tunables module.
The numbers that change with the size of the league derive from league_settings.py. Each has a name and a reason.
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
# The lowest score of each letter, best first. A score under the last band is a D. A report card reads A to D.
# Each part puts the league's worst roster at 0 and its best at 1, so a median roster scores near 50. The bands
# put that roster at C, so the letters spread A to D across a league and the middle of the league is not a D.
GRADE_BANDS = (("A", 70), ("B", 55), ("C", 40))
GRADE_BELOW_BANDS = "D"
