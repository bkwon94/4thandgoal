"""
The app factory of the Cornerstone API: CORS, the passphrase check, the rate limits, and the routes of each client.
The service needs CORNERSTONE_PASSPHRASE_<SLUG> for each client, such as CORNERSTONE_PASSPHRASE_CPC, and
ANTHROPIC_API_KEY for the Claude call. It reads CORNERSTONE_REPO,
CORNERSTONE_RESULT_CACHE_DIR, and CORNERSTONE_ALLOWED_ORIGINS when set.
Run it with `uv run uvicorn --factory cornerstone_api.app:app_from_env --host 0.0.0.0 --port 8080`.
At start it reads each client folder under clients/, and a bad client.toml stops the start.
Each client answers at /clients/<slug>/. The old paths with no client answer as cpc, so an old page still works.
On start, the real app refreshes the slow sources in a background thread, so the first request finds them on disk.
"""
import hmac
import logging
import threading
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from analyzer import routes as analyzer_routes
from analyzer.analysis import analyze
from analyzer.cache import ResultCache, TeamsCache
from analyzer.finder_reasons import write_reasons
from analyzer.ratelimit import GradeLimiter, RateLimiter, request_address
from analyzer.tunables import GRADES_PER_DAY, GRADES_PER_MINUTE
from cornerstone_api import refresh as refresh_routes
from cornerstone_api.settings import Settings, passphrase_env, repo_from_env
from cornerstone_api.sources import Sources
from league.client import Client, SettingsFetch, load_client, read_client_values
from league.paths import provider_cache_dir
from league.provider.sleeper import SleeperProvider, fetch_settings
from league.tunables import TEAMS_CACHE_SECONDS

logger = logging.getLogger(__name__)

# The client of the old paths with no client, such as /teams. A page from before the clients paths still calls them.
DEFAULT_SLUG = "cpc"
# The prefix of the routes of each client. The slug is the name of the client folder under clients/.
CLIENT_PREFIX = "/clients/{slug}"

# The API service: the count of requests one address may make in a fixed one-minute window, over every client.
# Past it the route answers 429, so one browser cannot loop the API and run up the Claude bill.
RATE_LIMIT_PER_MINUTE = 10

PASSPHRASE_HEADER = "X-League-Passphrase"
# The file of the daily grade counts of a client, in the result cache dir of the client.
GRADE_COUNTS_FILE = "grade-counts.json"


class _Unauthorized(Exception):
    """A request with a wrong or missing passphrase. Its handler answers 401 with no body."""


class _RateLimited(Exception):
    """A request past the rate limit of its address. Its handler answers 429 with a retry-after."""

    def __init__(self, retry_after: int) -> None:
        super().__init__()
        self.retry_after = retry_after


def _guard(request: Request) -> None:
    """Stop a request past the rate limit or without the passphrase of its client. Every route except health runs it.

    The client is the slug of the path. An old path with no client checks the passphrase of DEFAULT_SLUG.
    """
    # The count comes before the passphrase check, so wrong guesses count against the limit too.
    retry_after = request.app.state.limiter.hit(request_address(request))
    if retry_after is not None:
        raise _RateLimited(retry_after)
    slug = request.path_params.get("slug", request.app.state.default_slug)
    expected = request.app.state.settings.passphrases.get(slug)
    if expected is None:
        # Each client the app serves has a passphrase, so only a slug the app does not serve has none.
        # The route lookup answers 404 for it.
        return
    given = request.headers.get(PASSPHRASE_HEADER, "")
    # A constant-time compare, so the response time does not leak how much of a guess was right.
    if not hmac.compare_digest(given.encode(), expected.encode()):
        raise _Unauthorized()


def refresh_sources_on_start(settings: Settings, sources: Mapping[str, Sources]) -> None:
    """Refresh the slow sources of each client, for the season that Sleeper is in, with the normal max age.

    The normal max age keeps a fresh file, so the refresh fetches only the old files again.
    It runs in a background thread at start. Any error logs a warning and never raises, so the app keeps running,
    and the next client still refreshes. The log names only the client and the error type, so it never holds a key.
    """
    for slug, each in sources.items():
        try:
            each.refresh_current_season()
        except Exception as error:  # noqa: BLE001 - the app keeps running after a failed refresh
            logger.warning("The start-up refresh of the slow sources of %s failed (%s)", slug, type(error).__name__)


def _real_sources(client: Client) -> Sources:
    """The real fetches of `client`. The Sleeper adapter takes the shared NFL cache dir, which holds the players file."""
    return Sources(client, clock=lambda: datetime.now(client.tz),
                   fetch_sleeper=SleeperProvider(provider_cache_dir(client.nfl_dir)).fetch_live)


def _served(settings: Settings, client: Client, sources: Sources) -> analyzer_routes.Served:
    """The state of one client. Its result cache and its grade counts sit in its own folder of the result cache dir."""
    folder = settings.result_cache_dir / client.slug
    # The grade count file sits next to the result cache, so on Fly it is on the volume and a deploy keeps it.
    # The day of the limit is the calendar day in the timezone of the client.
    limiter = GradeLimiter(GRADES_PER_MINUTE, GRADES_PER_DAY, folder / GRADE_COUNTS_FILE, client.tz)
    return analyzer_routes.Served(client=client, sources=sources, cache=ResultCache(folder),
                                  teams_cache=TeamsCache(TEAMS_CACHE_SECONDS), grade_limiter=limiter)


def create_app(
        settings: Settings, clients: Sequence[Client], sources: Mapping[str, Sources] | None = None,
        analyzer: analyzer_routes.Analyzer | None = None, finder_reasons: analyzer_routes.ReasonWriter | None = None,
        *, refresh_on_start: bool = False) -> FastAPI:
    """The app that serves each of `clients`. Tests give fixture-backed sources by slug, an analyzer, and a finder
    reason writer. The defaults are the real ones.

    With `refresh_on_start`, a daemon thread refreshes the slow sources. It is off by default, so a test makes no fetch.
    """
    # A client with no passphrase would run open, so the app refuses it. Settings.from_env stops the real start first.
    for client in clients:
        if client.slug not in settings.passphrases:
            raise ValueError(f"The client {client.slug} has no passphrase. Set {passphrase_env(client.slug)}.")
    app = FastAPI(title="Cornerstone API")
    app.state.settings = settings
    given = sources or {}
    app.state.sources = {client.slug: given.get(client.slug) or _real_sources(client) for client in clients}
    app.state.served = {client.slug: _served(settings, client, app.state.sources[client.slug]) for client in clients}
    app.state.default_slug = DEFAULT_SLUG
    app.state.limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)
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

    # Each route answers at /clients/<slug>/ and at the old path with no client, which answers as DEFAULT_SLUG.
    for prefix in (CLIENT_PREFIX, ""):
        app.include_router(analyzer_routes.router, prefix=prefix, dependencies=[Depends(_guard)])
        app.include_router(refresh_routes.router, prefix=prefix, dependencies=[Depends(_guard)])

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


def load_clients(repo: Path, fetch: SettingsFetch = fetch_settings) -> list[Client]:
    """Each client folder under `repo`/clients, with the League settings of its latest season, in slug order.

    A folder with a missing or bad client.toml raises ClientError with the file and the key, so the start stops.
    """
    folders = sorted(path for path in (repo / "clients").iterdir() if path.is_dir())
    clients = []
    for folder in folders:
        season = read_client_values(folder).latest_season
        clients.append(load_client(repo, folder.name, season, fetch))
    return clients


def app_from_env() -> FastAPI:
    """The app with the settings from the environment and each client. The uvicorn factory flag calls it.

    A missing or bad client.toml stops the start, so a bad value never reaches a reader.
    """
    clients = load_clients(repo_from_env())
    # The passphrases stay in the settings, because each one is a secret, so client.toml never holds one.
    settings = Settings.from_env(client.slug for client in clients)
    return create_app(settings, clients, refresh_on_start=True)
