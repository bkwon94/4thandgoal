"""
The tunables of the week: the shootout cut, the storyline weights, the key starter rule, and the award cap.
Each number has a name and a reason, beside the rule that reads it. The numbers of the other packages stay in theirs.
"""

# Both best projected lineups for next week rank this high or higher for a shootout. The week reads it.
# GLOSSARY.md, "Projected shootout": the top four of the league.
SHOOTOUT_TOP = 4

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

# The most awards one player wins in a week. A reader expects the top scorer to be the top scorer, so the cap is
# not one. Three tiles for one player reads as a bug, so the cap is two.
AWARDS_PER_PLAYER = 2
