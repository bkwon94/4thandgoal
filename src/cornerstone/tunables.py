"""
The tunable table: every number the trade analyzer rubric names, each with its name and its reason.
The rubric file in the prompts directory points here, so a band or a margin changes in one place.
"""
from decimal import Decimal

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

# In a one-for-two-or-more trade, both ratios use the depth side's sum divided by this.
CONSOLIDATION_MARGIN = Decimal("1.25")

# Roster fit and standing compare a side's best lineup before and after the trade.
# The count of completed weeks whose points per game pick the best lineup. Fewer weeks use what exists.
LINEUP_WEEKS = 4
# The change in the best lineup's total points per game that counts as a gain or a loss.
# The value is a first guess, and the commissioner tunes it.
FIT_THRESHOLD = Decimal("3.0")

# Standing: a contender holds a playoff spot by record, and a seller is far out of the last spot.
# The count of playoff spots. The league ranks by wins, then by points for. The weekly facts read it too.
PLAYOFF_SPOTS = 6
# A seller has more than this many wins fewer than the team in the last playoff spot.
# The league scores a median game each week, so each week gives two results, and two games are one week of results.
SELLER_GAP = 2
# The last week of the regular season. When the side gets a player who is due back by this week, the trade is a return bet.
RETURN_BY_WEEK = 14
