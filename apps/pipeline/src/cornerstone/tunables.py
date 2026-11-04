"""
The tunable table: every algorithm number of the power rankings, the playoff odds,
and the next-week storylines. The numbers that change with the size of the league derive from league_settings.py.
Each has a name and a reason. The analyzer and the waiver board keep their own numbers in their packages.
"""

# Both best projected lineups for next week rank this high or higher for a shootout. The week reads it.
# GLOSSARY.md, "Projected shootout": the top four of the league.
SHOOTOUT_TOP = 4

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

# The next-week storylines: the weight of each kind. GLOSSARY.md, "Storyline". A game's storyline score is the sum,
# and the two games with the highest score are Must Watch. Stakes and a streak count most, because a reader feels
# them every week. A shootout and the top of the table count next. A rematch and revenge only add color.
# The order is the order of the reason when two weights tie: a streak comes before near the cut.
STORYLINE_WEIGHTS = {"streak": 3, "cut": 3, "shootout": 2, "table": 2, "rematch": 1, "revenge": 1}

# The key starter: GLOSSARY.md, "Key starter", and ADR 0009. The rule reads real starts, so it shows the habit of
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
# The lowest score of each letter, best first. A score under the last band is a D. A report card reads A to D.
# Each part puts the league's worst roster at 0 and its best at 1, so a median roster scores near 50. The bands
# put that roster at C, so the letters spread A to D across a league and the middle of the league is not a D.
GRADE_BANDS = (("A", 70), ("B", 55), ("C", 40))
GRADE_BELOW_BANDS = "D"

# The most awards one player wins in a week. A reader expects the top scorer to be the top scorer, so the cap is
# not one. Three tiles for one player reads as a bug, so the cap is two.
AWARDS_PER_PLAYER = 2
