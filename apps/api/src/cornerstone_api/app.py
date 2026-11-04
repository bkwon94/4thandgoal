"""
The app factory of the Cornerstone API: CORS, the passphrase check, the rate limits, and the route groups.
The service needs CORNERSTONE_PASSPHRASE, and ANTHROPIC_API_KEY for the Claude call. It reads CORNERSTONE_REPO,
CORNERSTONE_RESULT_CACHE_DIR, and CORNERSTONE_ALLOWED_ORIGINS when set.
Run it with `uv run uvicorn --factory cornerstone_api.app:app_from_env --host 0.0.0.0 --port 8080`.
On start, the real app refreshes the slow sources in a background thread, so the first request finds them on disk.
"""
import hmac
import logging
import threading
from datetime import datetime

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from cornerstone.analysis import analyze
from cornerstone.finder_reasons import write_reasons
from cornerstone.tunables import GRADES_PER_DAY, GRADES_PER_MINUTE, RATE_LIMIT_PER_MINUTE
from cornerstone_api import analyzer as analyzer_routes
from cornerstone_api import refresh as refresh_routes
from cornerstone_api.cache import ResultCache, TeamsCache
from cornerstone_api.ratelimit import GradeLimiter, RateLimiter, client_address
from cornerstone_api.settings import Settings
from cornerstone_api.sources import Sources
from league.client import Client, load_client, read_client_values
from league.paths import client_dir, provider_cache_dir
from league.provider.sleeper import SleeperProvider, fetch_settings
from league.tunables import TEAMS_CACHE_SECONDS

logger = logging.getLogger(__name__)

# The one client the API serves, until it serves each client by its path.
CLIENT_SLUG = "cpc"

PASSPHRASE_HEADER = "X-League-Passphrase"
# The file of the daily grade counts, in the result cache dir.
GRADE_COUNTS_FILE = "grade-counts.json"


class _Unauthorized(Exception):
    """A request with a wrong or missing passphrase. Its handler answers 401 with no body."""


class _RateLimited(Exception):
    """A request past the rate limit of its address. Its handler answers 429 with a retry-after."""

    def __init__(self, retry_after: int) -> None:
        super().__init__()
        self.retry_after = retry_after


def _guard(request: Request) -> None:
    """Stop a request past the rate limit or without the league passphrase. Every route group except health runs it."""
    # The count comes before the passphrase check, so wrong guesses count against the limit too.
    retry_after = request.app.state.limiter.hit(client_address(request))
    if retry_after is not None:
        raise _RateLimited(retry_after)
    given = request.headers.get(PASSPHRASE_HEADER, "")
    # A constant-time compare, so the response time does not leak how much of a guess was right.
    if not hmac.compare_digest(given.encode(), request.app.state.settings.passphrase.encode()):
        raise _Unauthorized()


def refresh_sources_on_start(settings: Settings, sources: Sources) -> None:
    """Refresh the slow sources of the season that Sleeper is in, with the normal max age.

    The normal max age keeps a fresh file, so the refresh fetches only the old files again.
    It runs in a background thread at start. Any error logs a warning and never raises, so the app keeps running.
    The log names only the error type, as the chart read does, so it never holds a key.
    """
    try:
        sources.refresh_current_season()
    except Exception as error:  # noqa: BLE001 - the app keeps running after a failed refresh
        logger.warning("The start-up refresh of the slow sources failed (%s)", type(error).__name__)


def create_app(
        settings: Settings, client: Client, sources: Sources | None = None,
        analyzer: analyzer_routes.Analyzer | None = None, finder_reasons: analyzer_routes.ReasonWriter | None = None,
        *, refresh_on_start: bool = False) -> FastAPI:
    """The app for these settings. Tests give fixture-backed sources, an analyzer, and a finder reason writer.
    The defaults are the real ones.

    With `refresh_on_start`, a daemon thread refreshes the slow sources. It is off by default, so a test makes no fetch.
    """
    app = FastAPI(title="Cornerstone API")
    app.state.settings = settings
    # The Sleeper adapter takes the shared NFL cache dir of the client, which holds the players file.
    app.state.sources = sources or Sources(client, clock=lambda: datetime.now(client.tz),
                                           fetch_sleeper=SleeperProvider(provider_cache_dir(client.nfl_dir)).fetch_live)
    app.state.cache = ResultCache(settings.result_cache_dir)
    app.state.teams_cache = TeamsCache(TEAMS_CACHE_SECONDS)
    app.state.limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)
    # The grade count file sits next to the result cache, so on Fly it is on the volume and a deploy keeps it.
    app.state.grade_limiter = GradeLimiter(
        GRADES_PER_MINUTE, GRADES_PER_DAY, settings.result_cache_dir / GRADE_COUNTS_FILE, client.tz)
    # The default is the real analyzer with the real Claude call. A test injects a stub, so no test needs the network.
    app.state.analyzer = analyzer or analyze
    # The finder reasons make the real Claude call by default too, so a test injects a writer with a fake call.
    app.state.finder_reasons = finder_reasons or write_reasons

    # The site calls the API from the browser, so only its origins and the local dev servers may read the answers.
    app.add_middleware(
        CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_methods=["GET", "POST"],
        allow_headers=[PASSPHRASE_HEADER, "Content-Type"], expose_headers=["Retry-After"],
    )

    @app.exception_handler(_Unauthorized)
    def unauthorized(request: Request, exc: _Unauthorized) -> Response:
        # No body, so a stranger learns nothing about the routes.
        return Response(status_code=401)

    @app.exception_handler(_RateLimited)
    def rate_limited(request: Request, exc: _RateLimited) -> Response:
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Try again later."},
                            headers={"Retry-After": str(exc.retry_after)})

    app.include_router(analyzer_routes.router, dependencies=[Depends(_guard)])
    app.include_router(refresh_routes.router, dependencies=[Depends(_guard)])

    @app.get("/health")
    def health() -> dict[str, str]:
        """The liveness check. It needs no passphrase and reads no data."""
        return {"status": "ok"}

    # A deploy or a fresh volume pays the downloads here and not in the first request.
    # The thread is a daemon, so it never holds up a stop of the app.
    app.state.refresh_thread = None
    if refresh_on_start:
        app.state.refresh_thread = threading.Thread(
            target=refresh_sources_on_start, args=(settings, app.state.sources), name="start-up-refresh", daemon=True)
        app.state.refresh_thread.start()

    return app


def app_from_env() -> FastAPI:
    """The app with the settings from the environment and the client. The uvicorn factory flag calls it.

    A missing or bad client.toml stops the start, so a bad value never reaches a reader.
    """
    settings = Settings.from_env()
    # The one client of the process, with the League settings of its latest season. The passphrase stays in the
    # settings, because it is a secret and not the league.
    season = read_client_values(client_dir(settings.repo, CLIENT_SLUG)).latest_season
    client = load_client(settings.repo, CLIENT_SLUG, season, fetch_settings)
    return create_app(settings, client, refresh_on_start=True)
