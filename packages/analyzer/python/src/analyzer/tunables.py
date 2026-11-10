"""
The tunable table of the analyzer: every algorithm number of the Measures and the grade limits.
A number changes in one place. Each has a name and a reason.
"""
from decimal import Decimal

# Standing: a team out of the race is more than this many weeks of results under the team in the last playoff spot.
# The standing Measure reads it. The gap counts weeks, not games: a week gives two results with the median game, else one, so the analyzer turns
# it into wins with the League settings.
OUT_OF_RACE_WEEKS = 1

# Superstar: a player in the top this many trade values of the week, over all positions, is a superstar.
# GLOSSARY.md, "Superstar". A tie at the edge shares the better rank, so every tied player is a superstar.
# 8 is the top of a 12-team league's first round, so a superstar is a player who can win a week alone.
SUPERSTAR_RANK = 8

# Roster fit and standing compare a side's best lineup before and after the trade. The season points per game
# of each player pick the best lineup of the Measures. GLOSSARY.md, "Lineup value".
# The change in the best lineup's total points per game that counts as a gain or a loss.
# The value is a first guess, and the commissioner tunes it.
FIT_THRESHOLD = Decimal("3.0")

# The ranks in the text of a grade: the Season rank always, and the Recent rank beside it only when the two differ by
# this many spots or more. GLOSSARY.md, "Recent rank". Decision 05 of grade-clarity: one number for every position.
# 12 spots is half the line at QB and TE, and a third of it at RB and WR, so a smaller swing shows no Recent rank.
RECENT_RANK_GAP = 12

# The Week line names no step-up when the newest depth chart is more than this many hours older than the grade.
# Decision 02 of grade-clarity: the chart is 3 to 27 hours old by design, and about 35 with a late daily run. 48 hours
# lets one late run pass and stops a chart after a missed day.
STEP_UP_CHART_HOURS = 48

# Trend and usage compares snap and target share over the SHARE_WEEKS windows of league/tunables.py.
# The change in mean WOPR between the two windows that counts as up or down. WOPR is 1.5 times target share plus
# 0.7 times air yards share. The 8 counts only the target share part: 1.5 times a 5-point share swing is about 8.
WOPR_SWING = 8

# Injury: a player the side gets who is out now, or who was on the injury report in many weeks, reads against it.
# The count of weeks on the injury report, through the last completed week, that makes a player injury-prone.
INJURY_WEEKS = 3
# The near return reads RETURN_WINDOW_WEEKS of league/tunables.py, because the lineup reads it too.

# Handcuff: a backup to the roster's own starting running back is insurance only when he carries the ball little.
# A backup who takes 25% of his team's carries scores points of his own, so he counts as a running back.
# A pure backup sits near 15%. A backup with a real role, such as Blake Corum at 28%, sits above 25%.
# The gate compares the exact share, so 24.6% stays a handcuff.
HANDCUFF_CARRY_SHARE = 25

# Expected gap: the league points of the players it gets and gives against their expected points over the window.
# The mean gap, in points per game, at or past which a group counts, either way, for the gets and for the gives.
# Gets under or gives over read for a side. Gets over or gives under read against it.
# The value is a first guess, and the commissioner tunes it.
EXPECTED_GAP = Decimal("3.0")
# The expected gap Measure is off until a real trade checks out, so no live sheet holds an untried Measure.
EXPECTED_MEASURE_ON = False

# The analyze route: the count of grades one address per client may get in a fixed one-minute window.
# Each grade that misses the result cache is a Claude call, so this caps the Claude bill from one browser.
GRADES_PER_MINUTE = 5
# The analyze route: the count of grades one address per client may get in one calendar day in the league timezone.
# It caps the Claude bill from one browser over a day, and the count lives on the volume so a deploy keeps it.
GRADES_PER_DAY = 20
