"""
The tunable table of the rankings: every algorithm number of the power rankings, the odds facts, and the why facts.
Each has a name and a reason. The numbers that change with the size of the league derive from league_settings.py.
"""


# The form component counts two games a week, each with a weight in the record and the streak.
# A head-to-head loss costs a game in the standings and a median loss does not, so the head-to-head game weighs more.
# Both games still show how a team plays, so the median game stays in.
FORM_HEAD_TO_HEAD_WEIGHT = 2
FORM_MEDIAN_WEIGHT = 1

# The power score is the weighted mean of the four components, keyed by component.
# Recent form is what the league wants the rank to show, so form weighs most. Scoring is second.
POWER_WEIGHTS = {"standing": 0.10, "form": 0.60, "schedule_played": 0.10, "scoring": 0.20}

# The numbers of the odds draw live in sim/tunables.py, because the season sim is the one odds engine (ADR 0037).
# The least gap, in points, between a side's win and loss odds that counts as a swing.
# A smaller gap is noise, not a stake.
SWING_FLAT = 5

# The why facts. Rule 25 of the writer prompt holds these two numbers as digits, so change rule 25 too.
# The least move, in places either way, that makes the writer cite the rank why.
# A 1-place move needs no reason on the page.
WHY_MOVE_AT = 2
# The odds, in percent, that make a record and its odds disagree: under .500 at or above it, or over .500 under it.
WHY_ODDS_AT = 25
