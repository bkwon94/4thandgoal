"""
The median text: the vocabulary of the median game, which the week adds to the writer and the verifier prompts.
A league with no median game gets no median text, so no blurb names a game the league does not play.
"""
from pathlib import Path

from league.client import Client

MEDIAN_TEXT = Path(__file__).parent / "prompts" / "median.md"


def median_terms(client: Client) -> tuple[str, ...]:
    """The extra vocabulary of `client` for the writer and the verifier: the median text, or none."""
    if not client.settings.median_game:
        return ()
    return (MEDIAN_TEXT.read_text(encoding="utf-8").strip(),)
