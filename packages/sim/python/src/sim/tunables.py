"""
The tunable table of the season sim: the count of runs, the sample of runs for the replay, and the numbers of the draw.
The draw numbers equal those of the weekly playoff odds in rankings/tunables.py. The parity test holds the two together.
"""

# The count of runs. At 10,000 runs one percent is 100 runs, so the sample error of a title odds number is under 1 point.
SIM_RUNS = 10_000
# The count of runs that sim.json stores for the replay. 200 runs keep the file under 50 KB gzip (PRD, sim.json).
SAMPLE_RUNS = 200
# The weight of the league average in a roster's level is k over n plus k, with k this count of weeks.
# The same number as LEVEL_SHRINK_WEEKS of the weekly odds, so the two draws agree.
LEVEL_SHRINK_WEEKS = 5
# The share of the gap from a team's season average to its projected best-lineup total that moves each drawn score.
# The same number as PROJECTION_WEIGHT of the weekly odds, so the two draws agree.
PROJECTION_WEIGHT = 0.5
# The decimals of each drawn score. The run counts the rounded score, so the stored scores of a run replay exactly.
SCORE_DECIMALS = 1
