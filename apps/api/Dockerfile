# The image of the Cornerstone API for Fly.io: Python 3.12, the locked dependencies through uv, and the uvicorn server.
# The tracked data goes in as a seed, and deploy/entrypoint.sh copies it onto the /data volume at start.
# The build context is the repo root, because the API is a member of the root uv workspace. Build it from the root:
# docker build -f apps/api/Dockerfile . The file Dockerfile.dockerignore beside this file names what goes in.
FROM python:3.12-slim

# The uv version matches the build backend pin in pyproject.toml, uv_build>=0.8.18,<0.9.0.
COPY --from=ghcr.io/astral-sh/uv:0.8.18 /uv /usr/local/bin/uv

# The base image has its own Python, so uv uses it and never downloads one.
# The project venv sits outside /app, so no copy of the source can overwrite it.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# The dependencies install first, so a change to the source alone reuses this layer.
# The image holds the five members the API needs: the API, the pipeline, and the league, facts, and week packages they import.
COPY pyproject.toml uv.lock ./
COPY apps/pipeline/pyproject.toml apps/pipeline/README.md ./apps/pipeline/
COPY packages/league/python/pyproject.toml ./packages/league/python/
COPY packages/facts/python/pyproject.toml ./packages/facts/python/
COPY packages/week/python/pyproject.toml ./packages/week/python/
COPY apps/api/pyproject.toml ./apps/api/
RUN uv sync --frozen --no-dev --package cpc-api --no-install-workspace

COPY apps/pipeline/src/ ./apps/pipeline/src/
COPY packages/league/python/src/ ./packages/league/python/src/
COPY packages/facts/python/src/ ./packages/facts/python/src/
COPY packages/week/python/src/ ./packages/week/python/src/
COPY apps/api/src/ ./apps/api/src/
RUN uv sync --frozen --no-dev --package cpc-api

# The values of the CPC client come from the image: client.toml, copy.toml, and the voice in prompts/.
COPY clients/cpc/client.toml clients/cpc/copy.toml ./clients/cpc/
COPY clients/cpc/prompts/ ./clients/cpc/prompts/

# The tracked data is the seed: the CPC data under clients/cpc/data and the shared NFL data under nfl/.
# /app/data is a link to the volume, so the NFL data and the result cache land on it. /app/clients/cpc/data is a link
# to the CPC data on the volume. The path helpers join each path to the repo root /app, so the code needs no change.
COPY clients/cpc/data/ ./seed/data/clients/cpc/data/
COPY data/nfl/ ./seed/data/nfl/
RUN ln -s /data /app/data && ln -s /data/clients/cpc/data /app/clients/cpc/data

COPY apps/api/deploy/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# --no-sync stops uv run from a sync at start: the default sync adds the dev group, and the image has no network need.
CMD ["uv", "run", "--no-sync", "uvicorn", "--factory", "cornerstone_api.app:app_from_env", "--host", "0.0.0.0", "--port", "8080"]
