"""
The shared tunables of the league kernel: the numbers that the kernel modules read, or that three or more
packages read. Each package keeps the rest of its numbers in its own tunables module.
"""

# Roster fit and standing compare a side's best lineup before and after the trade.
# The count of completed weeks whose points per game pick the best lineup. Fewer weeks use what exists.
LINEUP_WEEKS = 4

# Trend and usage compares snap and target share over the last weeks against the same count of weeks before them.
# The count of scored weeks in each window. The share helpers in history.py read it, so both windows change here.
SHARE_WEEKS = 2

# A player who is out now is a near return when his return week is no later than the trade week plus this count.
# The hole read uses the same window, GLOSSARY.md "Return window", so a starter due back inside it needs a bench
# player to cover him. Three weeks is the trade week and the next two. A pickup or another trade can rarely fix a
# slot sooner.
RETURN_WINDOW_WEEKS = 2

# The carry share reads his last 3 played games, so one big game cannot free him alone.
HANDCUFF_CARRY_GAMES = 3
# With fewer played games than this, the share is too thin to read, so the depth chart answer stands.
HANDCUFF_MIN_GAMES = 2

# The teams route: the seconds it answers one season from memory before it builds the teams again.
# Each build fetches Sleeper, so the trade form fills at once. A trade or a waiver claim shows within this window.
TEAMS_CACHE_SECONDS = 300

# The team trend is the mean of this many latest weeks. The form component of the power score reads the same window.
TREND_WEEKS = 3

# The positions of the waiver pool. Here and not in the engine, so the Sleeper client imports it with no cycle.
POOL_POSITIONS = ("QB", "RB", "WR", "TE", "K", "DEF")

# The count of falls in a row of a rostered player's snap share that make him a drop candidate. One or two
# falls can be a game script or a blowout, and three is a role that shrinks.
DROP_WEEKS = 3
# The count of latest weeks of usage the nflverse extract saves. DROP_WEEKS falls in a row take one more week
# than the falls, so the extract follows DROP_WEEKS. The usage trend reads only the last USAGE_WEEKS of them.
USAGE_SAVED_WEEKS = DROP_WEEKS + 1

# The refresh: the seconds after which the refresh fetches the injuries file and the player weeks file again.
# Injury status and snap counts change on game days, so a day-old file would miss Sunday on a Monday morning grade.
# Every other nflverse source keeps the day of CACHE_MAX_AGE_SECONDS.
FAST_SOURCES_MAX_AGE_SECONDS = 6 * 60 * 60

# The known games: a week N game is in progress when the clock is past its kickoff by less than this.
# An NFL game takes about 3 hours 15 minutes. Overtime and weather delays add more, so the extra time keeps
# a long game in progress until it ends. GLOSSARY.md, "In progress".
IN_PROGRESS_MINUTES = 4 * 60 + 30
