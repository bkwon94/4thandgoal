"""
The numbers of the eggs package: the life of a claim token.
A token is good for one claim, so a manager claims at once after the find.
"""

# A claim token is good for 15 minutes after the check that gave it.
TOKEN_SECONDS = 15 * 60
