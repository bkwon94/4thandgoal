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
# The Path search of decision 03. A Path stops at PATH_ODDS percent or at PATH_TEAMS teams, and needs PATH_RUNS runs,
# because at 100 runs its odds move up to 19 points between seeds. A condition must lift the odds by PATH_LIFT points,
# and a condition true in more than PATH_SKIP_SHARE of the runs of the Finish says almost nothing, so the search skips it.
PATH_ODDS = 90
PATH_TEAMS = 3
PATH_RUNS = 400
PATH_LIFT = 2
PATH_SKIP_SHARE = 0.85
# The most Paths of one Finish. Three fit a phone, and each later Path covers fewer runs.
PATHS_PER_FINISH = 3
# A Week plan says that any order of its wins works when its most common order holds under this share of the runs of
# its Path (PRD, the Week plan). Under half, most of the runs take another order.
ANY_ORDER_SHARE = 0.5
# The most games to root for in one week of a Week plan, and the least runs of the plan that a side of a game needs.
# At 100 runs a share moves about 4 points between seeds, so a root-for row with fewer runs is noise.
PLAN_ROOT_FOR = 2
PLAN_ROOT_RUNS = 100
# The chance of "to be sure" in the Score to beat (decision 06).
SURE_BEAT = 0.8
# A Finish at this share of runs or more is sure, and one under 1 minus it has no way in (decision 06).
SURE_FINISH = 0.995
# The lowest odds, in percent, of a Goal that The Race opens on. Below it the 1 seed or the bye is no real race, so the
# page opens on the next Goal. A call made without Brian (PRD, Further Notes).
OPEN_GOAL_ODDS = 5
# The most ways of one Clinch line. A line shows its most likely way, and a sheet lists the rest, so a few keep sim.json
# small.
CLINCH_WAYS = 8
# The lowest playoff odds, in percent, of a team that the league fact counts in the race for the last spots.
RACE_FLOOR = 10
# The tiebreak gap of the week card shows when another team across the edge of the Goal sits within TIE_WINS wins and
# TIE_POINTS Points For of Your team (PRD, the week card). Closer than that, the points of one week can decide a tie.
TIE_WINS = 1
TIE_POINTS = 50
# The most median rows of the week card. The first always shows, and the second needs a lift of ROOT_FOR_LIFT.
MEDIAN_ROWS = 2
# The most root-for rows of one week, and the least lift in whole points that keeps a row (PRD, the page block).
ROOT_FOR_ROWS = 3
ROOT_FOR_LIFT = 1
# The runs between two checks for a stop. A What-if checks for a client that went away about every 25 ms on the Mac.
STOP_CHECK_RUNS = 250
