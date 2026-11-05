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
# The image holds the members the API needs: the API and the league, facts, and analyzer packages it imports.
# uv reads the pyproject of the pipeline to check the lock, but --no-dev installs none of the pipeline code.
COPY pyproject.toml uv.lock ./
COPY apps/pipeline/pyproject.toml apps/pipeline/README.md ./apps/pipeline/
COPY packages/league/python/pyproject.toml ./packages/league/python/
COPY packages/facts/python/pyproject.toml ./packages/facts/python/
COPY packages/analyzer/python/pyproject.toml ./packages/analyzer/python/
COPY apps/api/pyproject.toml ./apps/api/
RUN uv sync --frozen --no-dev --package cpc-api --no-install-workspace

COPY packages/league/python/src/ ./packages/league/python/src/
COPY packages/facts/python/src/ ./packages/facts/python/src/
COPY packages/analyzer/python/src/ ./packages/analyzer/python/src/
COPY apps/api/src/ ./apps/api/src/
RUN uv sync --frozen --no-dev --package cpc-api

# Each client folder comes from the image: client.toml, copy.toml, the voice in prompts/, and the tracked data.
# The API reads each folder under clients/ at start, so a new client folder needs no change here.
COPY clients/ ./clients/

# The tracked data is the seed: the data of each client under clients/<slug>/data and the shared NFL data under nfl/.
# /app/data is a link to the volume, so the NFL data and the result cache land on it. /app/clients/<slug>/data is a
# link to the data of that client on the volume. A client with no tracked data gets an empty seed folder, so its link
# never dangles. The path helpers join each path to the repo root /app, so the code needs no change.
COPY data/nfl/ ./seed/data/nfl/
RUN ln -s /data /app/data && for folder in /app/clients/*/; do \
        slug="$(basename "$folder")"; \
        mkdir -p "/app/seed/data/clients/$slug"; \
        if [ -d "$folder/data" ]; then mv "$folder/data" "/app/seed/data/clients/$slug/data"; \
        else mkdir -p "/app/seed/data/clients/$slug/data"; fi; \
        ln -s "/data/clients/$slug/data" "$folder/data"; \
    done

COPY apps/api/deploy/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# --no-sync stops uv run from a sync at start: the default sync adds the dev group, and the image has no network need.
CMD ["uv", "run", "--no-sync", "uvicorn", "--factory", "cornerstone_api.app:app_from_env", "--host", "0.0.0.0", "--port", "8080"]
