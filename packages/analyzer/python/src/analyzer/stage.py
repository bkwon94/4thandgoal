"""
The stage callback of the Advisor: one plain line for each stage of a read or a Finder press, such as "Weighed 6 offers".
The front door sends each line as a step before the whole Answer. With no callback, a press tells no one.
"""
from collections.abc import Callable

# One stage line in plain words. Site copy shows it as it is, so a line never names an inner tool.
Stage = Callable[[str], None]


def quiet(line: str) -> None:
    """The default callback: it drops the line, because a route with no stream has no one to send it to."""
