"""
The one-time claim tokens of the egg check, in memory. A token is good for one claim and for TOKEN_SECONDS.
A restart drops each token, so a manager finds the egg again, which costs one more check and nothing else.
"""
import secrets
from datetime import datetime, timedelta

from eggs.tunables import TOKEN_SECONDS


class ClaimTokens:
    """The live claim tokens, each with its egg and the end of its life."""

    def __init__(self) -> None:
        self.live: dict[str, tuple[int, datetime]] = {}

    def issue(self, egg_id: int, now: datetime) -> str:
        """A new token for the egg. The old tokens go first, so the map holds only live tokens."""
        self.live = {token: held for token, held in self.live.items() if held[1] > now}
        token = secrets.token_urlsafe(24)
        self.live[token] = (egg_id, now + timedelta(seconds=TOKEN_SECONDS))
        return token

    def take(self, token: str, now: datetime) -> int | None:
        """The egg of the token, one time only. An unknown or an old token gives None."""
        held = self.live.pop(token, None)
        if held is None or held[1] <= now:
            return None
        return held[0]
