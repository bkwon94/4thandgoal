"""
The shared error mapping of the route groups that read the live snapshot.
A season that Sleeper is not in is a bad input, so each route answers 422 for it.
"""
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import HTTPException


@contextmanager
def season_in_progress(season: int) -> Iterator[None]:
    """Turn the ValueError of a season that is not in progress into a 422."""
    try:
        yield
    except ValueError:
        raise HTTPException(status_code=422, detail=f"The season {season} is not in progress.")
