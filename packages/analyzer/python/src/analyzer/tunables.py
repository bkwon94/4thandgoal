"""
The tunable table of the analyzer: every algorithm number of the trade analyzer rubric, the finder, and the grade limits.
The rubric file in the prompts directory points here, so a number changes in one place. Each has a name and a reason.
"""
from decimal import Decimal

# Standing: a seller is more than this many weeks of results under the team in the last playoff spot. The analyzer reads
# it. The gap counts weeks, not games: a week gives two results with the median game, else one, so the analyzer turns
# it into wins with the League settings.
SELLER_GAP_WEEKS = 1

# The numbers are Decimal, so a ratio at a lower bound, such as 22 over 20, lands in its band exactly.

# Start letter bands on the ratio of trade value got over trade value gave. Each lower bound is inclusive.
# The lowest ratio that starts a side at A.
BAND_A = Decimal("1.25")
# The lowest ratio that starts a side at B.
BAND_B = Decimal("1.10")
# The lowest ratio that starts a side at C.
BAND_C = Decimal("0.90")
# The lowest ratio that starts a side at D. A ratio below it starts the side at F.
BAND_D = Decimal("0.75")

# The bands from the top down. A ratio below the last bound starts at F.
START_LETTER_BANDS: tuple[tuple[Decimal, str], ...] = ((BAND_A, "A"), (BAND_B, "B"), (BAND_C, "C"), (BAND_D, "D"))

# A side that gives one player for two or more, or two or more for one, divides the sum of the two or more by this.
CONSOLIDATION_MARGIN = Decimal("1.25")

# Roster fit and standing compare a side's best lineup before and after the trade. LINEUP_WEEKS of
# league/tunables.py picks the best lineup.
# The change in the best lineup's total points per game that counts as a gain or a loss.
# The value is a first guess, and the commissioner tunes it.
FIT_THRESHOLD = Decimal("3.0")

# Trend and usage compares snap and target share over the SHARE_WEEKS windows of league/tunables.py.
# The change in mean WOPR between the two windows that counts as up or down. WOPR is 1.5 times target share plus
# 0.7 times air yards share. The 8 counts only the target share part: 1.5 times a 5-point share swing is about 8.
WOPR_SWING = 8

# Injury: a player the side gets who is out now, or who was on the injury report in many weeks, is a step down.
# The count of weeks on the injury report, through the last completed week, that makes a player injury-prone.
INJURY_WEEKS = 3
# The near return reads RETURN_WINDOW_WEEKS of league/tunables.py, because the lineup reads it too.

# Handcuff: a backup to the roster's own starting running back is insurance only when he carries the ball little.
# A backup who takes 25% of his team's carries scores points of his own, so he counts as a running back.
# A pure backup sits near 15%. A backup with a real role, such as Blake Corum at 28%, sits above 25%.
# The gate compares the exact share, so 24.6% stays a handcuff.
HANDCUFF_CARRY_SHARE = 25

# Schedule: byes left and the playoff opponents of the players it gets against the players it gives.
# It never moves a letter.
# The gap in the mean rank of the week 15 to 17 opponents, in points allowed to the position, that makes a lean.
# Set this number by hand. The commissioner tunes it.
SCHEDULE_RANK_GAP = 4

# Expected gap: the league points of the players it gets and gives against their expected points over the window.
# The mean gap, in points per game, at or past which a group counts, either way, for the gets and for the gives.
# Gets under or gives over step a side up. Gets over or gives under step it down.
# The value is a first guess, and the commissioner tunes it.
EXPECTED_GAP = Decimal("3.0")
# The expected gap adjuster is off until a real trade checks out, so no live breakdown shows an untried adjuster.
EXPECTED_ADJUSTER_ON = False

# The chart ratio picks the start letter. The sum of the adjuster steps clamps to this many steps either way,
# so a side that starts at C never ends at A or F, and the chart weighs more than the adjusters.
CLAMP_STEPS = 1

# The verdict for the side that asked reads its final letter.
# The lowest final letter that accepts outright.
ACCEPT_AT_OR_ABOVE = "B"
# The highest final letter that declines outright. A letter between the two bands accepts when the other side's
# final letter is no better, and counters when it is better. The schedule lean can turn that middle result.
DECLINE_AT_OR_BELOW = "D"

# The fairness of a trade reads the final letter of both sides, so it says whether the other side will take it.
# The lowest final letter of both sides that makes a win-win. At B a side gets more than it gives, so both win.
WIN_WIN_AT_OR_ABOVE = "B"
# The highest final letter of either side that makes a trade lopsided. At D a side gives more than it gets.
LOPSIDED_AT_OR_BELOW = "D"

# The analyze route: the count of grades one address per client may get in a fixed one-minute window.
# Each grade that misses the result cache is a Claude call, so this caps the Claude bill from one browser.
GRADES_PER_MINUTE = 5
# The analyze route: the count of grades one address per client may get in one calendar day in the league timezone.
# It caps the Claude bill from one browser over a day, and the count lives on the volume so a deploy keeps it.
GRADES_PER_DAY = 20

# The finder: the count of win-win trades it returns at most for one pair of rosters.
# A short list is one a manager reads, and three trades with no shared player each stand as a real choice.
FINDER_TOP = 3
