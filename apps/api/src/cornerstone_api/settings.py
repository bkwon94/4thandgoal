"""
The settings of the API app: the passphrase, the repo, the result cache directory, and the allowed origins.
Settings.from_env reads them from the environment, so the deploy sets them as secrets and variables.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

from league.paths import results_cache_dir

# The production league site and the two local dev servers of the site repo.
DEFAULT_ORIGINS = ("https://cpcfantasy.com", "http://localhost:5173", "http://localhost:3000")


@dataclass(frozen=True)
class Settings:
    """What the app reads from its environment."""

    # The one shared league passphrase. Every route except health needs it.
    # Kept out of the repr, so a log or a traceback never shows it.
    passphrase: str = field(repr=False)
    # The repo root that holds clients/ and data/, where the live snapshot reads and writes its caches.
    repo: Path
    # The directory of the result cache. It sits on the data volume, so a cached result survives a restart.
    result_cache_dir: Path
    allowed_origins: tuple[str, ...] = DEFAULT_ORIGINS

    @classmethod
    def from_env(cls) -> "Settings":
        """The settings from the environment. A missing passphrase stops the start, so the app never runs open."""
        passphrase = os.environ.get("CORNERSTONE_PASSPHRASE")
        if not passphrase:
            raise RuntimeError("Set CORNERSTONE_PASSPHRASE before the API starts.")
        repo = Path(os.environ.get("CORNERSTONE_REPO", ".")).resolve()
        cache = os.environ.get("CORNERSTONE_RESULT_CACHE_DIR")
        origins = os.environ.get("CORNERSTONE_ALLOWED_ORIGINS")
        return cls(
            passphrase=passphrase,
            repo=repo,
            result_cache_dir=Path(cache) if cache else results_cache_dir(repo),
            allowed_origins=tuple(o.strip() for o in origins.split(",")) if origins else DEFAULT_ORIGINS,
        )
