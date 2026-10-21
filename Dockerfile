# The image of the Cornerstone API for Fly.io: Python 3.12, the locked dependencies through uv, and the uvicorn server.
# The tracked data goes in as a seed, and deploy/entrypoint.sh copies it onto the /data volume at start.
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
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN uv sync --frozen --no-dev

# The tracked data is the seed. /app/data is a link to the volume, so every path helper joins data/ to the
# repo root /app and lands on the volume, with no change to the code.
COPY data/ ./seed/data/
RUN ln -s /data /app/data

COPY deploy/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# --no-sync stops uv run from a sync at start: the default sync adds the dev group, and the image has no network need.
CMD ["uv", "run", "--no-sync", "uvicorn", "--factory", "cornerstone_api.app:app_from_env", "--host", "0.0.0.0", "--port", "8080"]
