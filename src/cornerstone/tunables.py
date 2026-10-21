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

# In a one-for-two-or-more trade, the depth side's sum is divided by this in both ratios.
CONSOLIDATION_MARGIN = Decimal("1.25")
