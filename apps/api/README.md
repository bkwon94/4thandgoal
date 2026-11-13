# Cornerstone API

The FastAPI app serves each client through domain packages and deploys to Fly.
Its product code imports no pipeline code.
API tests reuse pipeline fixtures and README-rule helpers; these test dependencies do not define product ownership.

## Module map

- HTTP composition: the [API owner](src/cornerstone_api/README.md) creates the app and mounts client routes in [app.py](src/cornerstone_api/app.py).
- App state and limits: the [API owner](src/cornerstone_api/README.md) owns client state, access checks, and daily answer allowances.
- Analyzer routes: the [analyzer owner](../../packages/analyzer/README.md) owns trade grades, caches, and persistent grade limits. The API mounts those routes.

## Commands

Run `make help` in `apps/api/` for the app commands.
Run `make check-fast` for lint, types, and rules.
Run `make check` for lint, types, and all tests.
