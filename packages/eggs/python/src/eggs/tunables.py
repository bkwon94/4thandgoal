"""
The numbers of the eggs package: the life of a claim token, the limit of the egg check, and the limit of the board.
A token is good for one claim, so a manager claims at once after the find.
"""

# A claim token is good for 15 minutes after the check that gave it.
TOKEN_SECONDS = 15 * 60

# The egg checks of one address in one hour. A real hunter makes about 80 checks in a long session, and a sweep of
# the site needs thousands, so the limit stops a sweep and seldom stops a hunter (decision ticket 10).
CHECKS_PER_HOUR = 60
CHECK_WINDOW_SECONDS = 60 * 60

# The board reads of one address in one minute. The egg button and the egg banner read the board on each page, so
# the board counts apart from the analyzer and the claim, and a manager who reads many pages never spends their limit.
BOARD_READS_PER_MINUTE = 60
BOARD_WINDOW_SECONDS = 60
