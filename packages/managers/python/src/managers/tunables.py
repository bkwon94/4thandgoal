"""
The tunables of the managers: the weights of the roster grade, the hole cost, the depth spares, and the letter bands.
Each number has a name and a reason, beside the rule that reads it. The numbers of the other packages stay in theirs.
"""

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
