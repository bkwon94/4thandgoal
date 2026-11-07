"""
The egg drop step of the publish: it sends the confirmed eggs of the week in the egg file to the drop route of the API.
A failed drop warns and never fails the publish, so "make egg-drop" retries it.
"""
import os
from pathlib import Path

import httpx

from eggs.eggfile import confirmed_spots
from league.client import Client


def run_egg_drop(client: Client, week: int, egg_file: Path, http: httpx.Client, key: str | None) -> str:
    """Drop the confirmed eggs of the week of `client` through `http`, and return the one line that says the result.

    `http` has the base URL of the API, and `key` is the commissioner key of the client.
    """
    if "eggs" not in client.values.packages:
        return f"The client {client.slug} has no eggs package, so no eggs dropped."
    spots = confirmed_spots(egg_file, week)
    if not spots:
        return f"No eggs dropped: week {week} has no confirmed egg in {egg_file}."
    retry = f"Run make egg-drop CLIENT={client.slug} WEEK={week} to retry."
    if not key:
        return f"WARNING: the egg drop of week {week} failed: no commissioner key. {retry}"
    try:
        response = http.post(f"/clients/{client.slug}/eggs/drop", headers={"X-Commissioner-Key": key},
                             json={"week": week, "eggs": [spot.egg() for spot in spots]})
    except httpx.HTTPError as err:
        return f"WARNING: the egg drop of week {week} failed: {err}. {retry}"
    # The status check is by hand, because the test client of the API raises its own error type, not the one of httpx.
    if response.status_code != 200:
        return f"WARNING: the egg drop of week {week} failed: HTTP {response.status_code} {response.text}. {retry}"
    dropped = response.json()["dropped"]
    if dropped == 0:
        # A second drop of one week adds nothing, so the eggs of the first drop stay.
        return f"Week {week} already holds its eggs, so no eggs dropped."
    return f"Dropped {dropped} eggs of week {week}."


# The API of the site, the same default as the site config.
API_URL = "https://api.4thandgoal.app"


def commissioner_key_env(slug: str) -> str:
    """The env value of the commissioner key of the client `slug`, as the API app reads it."""
    return f"CORNERSTONE_COMMISSIONER_KEY_{slug.upper()}"


def drop_from_env(client: Client, week: int, egg_file: Path) -> str:
    """Run the egg drop against the API of CORNERSTONE_API_URL, with the commissioner key of the env."""
    with httpx.Client(base_url=os.environ.get("CORNERSTONE_API_URL", API_URL), timeout=30) as http:
        return run_egg_drop(client, week, egg_file, http, os.environ.get(commissioner_key_env(client.slug)))
