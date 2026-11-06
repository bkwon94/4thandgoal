"""
The settings of the API app: the passphrase of each client, the repo, the result cache directory, and the origins.
Settings.from_env reads them from the environment, so the deploy sets them as secrets and variables.
"""
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from league.paths import results_cache_dir

# The site of each client at its Worker, the old CPC host for a page that a reader still has open, and the two local dev servers.
DEFAULT_ORIGINS = (
    "https://cpc.4thandgoal.app", "https://norcal.4thandgoal.app", "https://cpcfantasy.com",
    "http://localhost:5173", "http://localhost:3000",
)

# The API service: the count of requests one address may make in a fixed one-minute window, over every client.
# Past it the route answers 429, so one browser cannot loop the API and run up the Claude bill.
# This is the default. CORNERSTONE_RATE_LIMIT_PER_MINUTE changes it, and Fly never sets it.
RATE_LIMIT_PER_MINUTE = 10


@dataclass(frozen=True)
class Settings:
    """What the app reads from its environment."""

    # The passphrase of each client, by slug. Every route of a client except health needs its own passphrase.
    # No passphrase is shared, so the managers of one league cannot spend the grades of another.
    # Kept out of the repr, so a log or a traceback never shows one.
    passphrases: Mapping[str, str] = field(repr=False)
    # The repo root that holds clients/ and data/, where the live snapshot reads and writes its caches.
    repo: Path
    # The directory of the result cache. It sits on the data volume, so a cached result survives a restart.
    result_cache_dir: Path
    allowed_origins: tuple[str, ...] = DEFAULT_ORIGINS
    # The count of requests per minute and address. Only an evidence run sets a different one.
    rate_limit_per_minute: int = RATE_LIMIT_PER_MINUTE

    @classmethod
    def from_env(cls, slugs: Iterable[str]) -> "Settings":
        """The settings from the environment for the clients `slugs`. Each client reads passphrase_env(slug).

        A client with no passphrase stops the start, so no client runs open and none falls back to another one.
        """
        passphrases = {}
        for slug in slugs:
            name = passphrase_env(slug)
            passphrase = os.environ.get(name)
            if not passphrase:
                raise RuntimeError(f"Set {name} before the API starts.")
            passphrases[slug] = passphrase
        repo = repo_from_env()
        cache = os.environ.get("CORNERSTONE_RESULT_CACHE_DIR")
        origins = os.environ.get("CORNERSTONE_ALLOWED_ORIGINS")
        return cls(
            passphrases=passphrases,
            repo=repo,
            result_cache_dir=Path(cache) if cache else results_cache_dir(repo),
            allowed_origins=tuple(o.strip() for o in origins.split(",")) if origins else DEFAULT_ORIGINS,
            rate_limit_per_minute=rate_limit_from_env(),
        )


def passphrase_env(slug: str) -> str:
    """The env value of the passphrase of the client `slug`, such as CORNERSTONE_PASSPHRASE_CPC for cpc."""
    return f"CORNERSTONE_PASSPHRASE_{slug.upper()}"


def repo_from_env() -> Path:
    """The repo root that holds clients/ and data/, from CORNERSTONE_REPO. The default is the folder of the process."""
    return Path(os.environ.get("CORNERSTONE_REPO", ".")).resolve()


def rate_limit_from_env() -> int:
    """The count of requests per minute from CORNERSTONE_RATE_LIMIT_PER_MINUTE. The default is RATE_LIMIT_PER_MINUTE.

    A value that is not a whole number of 1 or more stops the start, so a typo never falls back to the default.
    """
    name = "CORNERSTONE_RATE_LIMIT_PER_MINUTE"
    value = os.environ.get(name)
    if value is None:
        return RATE_LIMIT_PER_MINUTE
    try:
        limit = int(value)
    except ValueError:
        limit = 0
    if limit < 1:
        raise RuntimeError(f"Set {name} to a whole number of 1 or more, not {value!r}.")
    return limit
