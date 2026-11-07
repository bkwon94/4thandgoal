"""
The app factory of the Cornerstone API: CORS, the passphrase check, the rate limits, and the routes of each client.
The service needs CORNERSTONE_PASSPHRASE_<SLUG> for each client, such as CORNERSTONE_PASSPHRASE_CPC,
CORNERSTONE_COMMISSIONER_KEY_<SLUG> for each client of the eggs package, and ANTHROPIC_API_KEY for the Claude call.
It reads CORNERSTONE_REPO, CORNERSTONE_RESULT_CACHE_DIR, CORNERSTONE_EGGS_DIR, and CORNERSTONE_ALLOWED_ORIGINS when set.
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
from cornerstone_api.settings import Settings, commissioner_key_env, eggs_dir, passphrase_env, repo_from_env
from cornerstone_api.sources import Sources
from cornerstone_api.value_models import VALUE_MODELS
from eggs import routes as eggs_routes
from eggs.store import EggStore
from eggs.tunables import BOARD_READS_PER_MINUTE, BOARD_WINDOW_SECONDS, CHECK_WINDOW_SECONDS, CHECKS_PER_HOUR
from eggs.values import EggsValues
from league.client import Client, SettingsFetch, load_client
from league.paths import provider_cache_dir
from league.provider.sleeper import SleeperProvider, fetch_settings
from league.tunables import TEAMS_CACHE_SECONDS

logger = logging.getLogger(__name__)

# The client of the old paths with no client, such as /teams. A page from before the clients paths still calls them.
DEFAULT_SLUG = "cpc"
# The prefix of the routes of each client. The slug is the name of the client folder under clients/.
CLIENT_PREFIX = "/clients/{slug}"

PASSPHRASE_HEADER = "X-League-Passphrase"
COMMISSIONER_HEADER = "X-Commissioner-Key"
# The prefix of the eggs routes of each client. Only the clients paths serve them, because no old page calls them.
EGGS_PREFIX = f"{CLIENT_PREFIX}/eggs"
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
    """Stop a request past the rate limit or without the passphrase of its client. Every route runs it, except health,
    the open eggs routes, and the commissioner routes of the eggs, which run their own guard.

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


def _limit(request: Request) -> None:
    """Stop a request past the rate limit of its address. The commissioner guard runs it before the key check."""
    retry_after = request.app.state.limiter.hit(request_address(request))
    if retry_after is not None:
        raise _RateLimited(retry_after)


def _check_limit(request: Request) -> None:
    """Stop an egg check past the limit of the egg check of its address. The check counts apart from the other routes,
    so a hunt spends none of the limit of the analyzer, and a sweep of the site stops at the limit of one hour."""
    retry_after = request.app.state.check_limiter.hit(request_address(request))
    if retry_after is not None:
        raise _RateLimited(retry_after)


def _board_limit(request: Request) -> None:
    """Stop a board read past the limit of the board of its address. The egg button and the egg banner read the board
    on each page, so the board counts apart from the other routes and a page read spends none of the analyzer limit."""
    retry_after = request.app.state.board_limiter.hit(request_address(request))
    if retry_after is not None:
        raise _RateLimited(retry_after)


def _commissioner_guard(request: Request) -> None:
    """Stop a request past the rate limit or without the commissioner key of its client. The drop and the undo run it.

    Every manager knows the passphrase, so the passphrase alone never drops an egg or undoes a claim.
    """
    _limit(request)
    expected = request.app.state.settings.commissioner_keys.get(request.path_params.get("slug"))
    if expected is None:
        # Each client of the eggs package has a key, so only a client with no hunt has none. With no key, nothing can
        # prove the commissioner, so the guard refuses the request and never lets it pass open.
        raise _Unauthorized()
    given = request.headers.get(COMMISSIONER_HEADER, "")
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


def _hunt(settings: Settings, client: Client, served: analyzer_routes.Served) -> eggs_routes.Hunt:
    """The egg hunt of one client. Its SQLite file is <slug>.sqlite in the eggs folder, on the volume on Fly.

    The rosters come from the teams route of the analyzer, so the board shares its cache of the live Sleeper rosters.
    """
    season = client.values.latest_season

    def rosters() -> dict[int, str]:
        return {team["roster_id"]: team["team"] for team in analyzer_routes.teams(season, served)["teams"]}

    return eggs_routes.Hunt(store=EggStore(eggs_dir(settings) / f"{client.slug}.sqlite"),
                            values=client.values.package(EggsValues), rosters=rosters,
                            clock=lambda: datetime.now(client.tz), tz=client.tz)


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
    # A client of the eggs package with no commissioner key would let anyone drop an egg, so the app refuses it too.
    for client in clients:
        if "eggs" in client.values.packages and client.slug not in settings.commissioner_keys:
            raise ValueError(f"The client {client.slug} has no commissioner key. Set {commissioner_key_env(client.slug)}.")
    app = FastAPI(title="Cornerstone API")
    app.state.settings = settings
    given = sources or {}
    app.state.sources = {client.slug: given.get(client.slug) or _real_sources(client) for client in clients}
    app.state.served = {client.slug: _served(settings, client, app.state.sources[client.slug]) for client in clients}
    app.state.default_slug = DEFAULT_SLUG
    # Only a client of the eggs package has a hunt, so the eggs routes of any other client answer 404.
    app.state.hunts = {client.slug: _hunt(settings, client, app.state.served[client.slug])
                       for client in clients if "eggs" in client.values.packages}
    app.state.limiter = RateLimiter(settings.rate_limit_per_minute)
    app.state.check_limiter = RateLimiter(CHECKS_PER_HOUR, window=CHECK_WINDOW_SECONDS)
    app.state.board_limiter = RateLimiter(BOARD_READS_PER_MINUTE, window=BOARD_WINDOW_SECONDS)
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

    # The egg check and the egg board are open, the claim needs the passphrase, and the drop and the undo need the
    # commissioner key. The check and the board each have their own limit of each address, and each other group keeps
    # the rate limit.
    app.include_router(eggs_routes.check_router, prefix=EGGS_PREFIX, dependencies=[Depends(_check_limit)])
    app.include_router(eggs_routes.open_router, prefix=EGGS_PREFIX, dependencies=[Depends(_board_limit)])
    app.include_router(eggs_routes.claim_router, prefix=EGGS_PREFIX, dependencies=[Depends(_guard)])
    app.include_router(eggs_routes.commissioner_router, prefix=EGGS_PREFIX, dependencies=[Depends(_commissioner_guard)])

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
    # A season of None takes the latest season, so the start reads each client.toml one time.
    return [load_client(repo, folder.name, None, fetch, VALUE_MODELS) for folder in folders]


def app_from_env() -> FastAPI:
    """The app with the settings from the environment and each client. The uvicorn factory flag calls it.

    A missing or bad client.toml stops the start, so a bad value never reaches a reader.
    """
    clients = load_clients(repo_from_env())
    # The passphrases and the commissioner keys stay in the settings, because each one is a secret, so client.toml
    # never holds one.
    settings = Settings.from_env((client.slug for client in clients),
                                 (client.slug for client in clients if "eggs" in client.values.packages))
    return create_app(settings, clients, refresh_on_start=True)
