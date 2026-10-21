"""
The app factory of the Cornerstone API: CORS, the passphrase check, the rate limit, and the route groups.
The service needs CORNERSTONE_PASSPHRASE, and ANTHROPIC_API_KEY for the Claude call. It reads CORNERSTONE_REPO,
CORNERSTONE_RESULT_CACHE_DIR, and CORNERSTONE_ALLOWED_ORIGINS when set.
Run it with `uv run uvicorn --factory cornerstone_api.app:app_from_env --host 0.0.0.0 --port 8080`.
"""
import hmac

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from cornerstone.analysis import analyze
from cornerstone.tunables import RATE_LIMIT_PER_MINUTE
from cornerstone_api import analyzer as analyzer_routes
from cornerstone_api.cache import ResultCache
from cornerstone_api.ratelimit import RateLimiter
from cornerstone_api.settings import Settings
from cornerstone_api.sources import Sources

PASSPHRASE_HEADER = "X-League-Passphrase"


class _Unauthorized(Exception):
    """A request with a wrong or missing passphrase. Its handler answers 401 with no body."""


class _RateLimited(Exception):
    """A request past the rate limit of its address. Its handler answers 429 with a retry-after."""

    def __init__(self, retry_after: int) -> None:
        super().__init__()
        self.retry_after = retry_after


def _client_address(request: Request) -> str:
    """The address of the client. On Fly every request comes from the proxy, so the proxy sets Fly-Client-IP."""
    forwarded = request.headers.get("Fly-Client-IP")
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def _guard(request: Request) -> None:
    """Stop a request past the rate limit or without the league passphrase. Every route group except health runs it."""
    # The count comes before the passphrase check, so wrong guesses count against the limit too.
    retry_after = request.app.state.limiter.hit(_client_address(request))
    if retry_after is not None:
        raise _RateLimited(retry_after)
    given = request.headers.get(PASSPHRASE_HEADER, "")
    # A constant-time compare, so the response time does not leak how much of a guess was right.
    if not hmac.compare_digest(given.encode(), request.app.state.settings.passphrase.encode()):
        raise _Unauthorized()


def create_app(
        settings: Settings, sources: Sources | None = None,
        analyzer: analyzer_routes.Analyzer | None = None) -> FastAPI:
    """The app for these settings. Tests give fixture-backed sources and an analyzer. The defaults are the real ones."""
    app = FastAPI(title="Cornerstone API")
    app.state.settings = settings
    app.state.sources = sources or Sources()
    app.state.cache = ResultCache(settings.result_cache_dir)
    app.state.limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)
    # The default is the real analyzer with the real Claude call. A test injects a stub, so no test needs the network.
    app.state.analyzer = analyzer or analyze

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

    @app.get("/health")
    def health() -> dict[str, str]:
        """The liveness check. It needs no passphrase and reads no data."""
        return {"status": "ok"}

    return app


def app_from_env() -> FastAPI:
    """The app with the settings from the environment. The uvicorn factory flag calls it."""
    return create_app(Settings.from_env())
