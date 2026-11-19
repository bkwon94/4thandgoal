"""
The tunable table of the season sim, the one odds engine: the count of runs, the sample of runs for the replay, the
numbers of the draw, and the show line of the seed.
"""

# The count of runs. At 10,000 runs one percent is 100 runs, so the sample error of a title odds number is under 1 point.
SIM_RUNS = 10_000
# The count of runs that sim.json stores for the replay. 200 runs keep the file under 50 KB gzip (PRD, sim.json).
SAMPLE_RUNS = 200
# The weight of the league average in a roster's level is k over n plus k, with k this count of weeks.
# At 5 with 7 weeks played, the roster's own average carries 58 percent. On week 7, k from 3 to 8 lands within 3 points.
LEVEL_SHRINK_WEEKS = 5
# The share of the gap from a team's season average to its projected best-lineup total that moves each drawn score.
# Past scores know the team's level, and the projection knows that week's roster. Half each, Brian's call.
# The gap reads from the raw average, so at 1 a draw is the shrunk level plus the full gap, not the projection itself.
PROJECTION_WEIGHT = 0.5
# The decimals of each drawn score. The run counts the rounded score, so the stored scores of a run replay exactly.
SCORE_DECIMALS = 1
# The lowest playoff odds, in percent, that show the most likely seed.
# Below it the seed rests on fewer than half the runs.
SEED_SHOW_AT = 50
# A number of the page block shows "about" when its chance times the effective runs is under this count (decision 07).
ABOUT_RUNS = 400
# The playoff odds, in percent, at which the sentence of the ladder says "you're in".
IN_ODDS = 90
# The lowest playoff odds, in percent, of a team that the league fact counts in the race for the last spots.
RACE_FLOOR = 10
# The most root-for rows of one week, and the least lift in whole points that keeps a row (PRD, the page block).
ROOT_FOR_ROWS = 3
ROOT_FOR_LIFT = 1
# The runs between two checks for a stop. A What-if checks for a client that went away about every 25 ms on the Mac.
STOP_CHECK_RUNS = 250
