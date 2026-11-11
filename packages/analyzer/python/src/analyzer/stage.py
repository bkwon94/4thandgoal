"""
The stage callback of the Advisor: one plain line for each stage of a read or a Finder press, such as "Weighed 6 offers".
The front door sends each line as a step before the whole Answer. With no callback, a press tells no one.
"""
from typing import Protocol


class Stage(Protocol):
    """One stage line in plain words. Site copy shows it as it is, so a line never names an inner tool.

    A live line names the stage at work in the present, such as "Building offers", and the site shows it with a
    spinner. The done line of the stage takes its place when the stage ends, in the past, such as "Built 56 offers".
    """

    def __call__(self, line: str, *, live: bool = False) -> None: ...


def quiet(line: str, *, live: bool = False) -> None:
    """The default callback: it drops the line, because a route with no stream has no one to send it to."""
