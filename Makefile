# Common tasks for the Cornerstone weekly report and its API.
# Run "make help" to list the targets.

SEASON ?= 2026

.DEFAULT_GOAL := help
.PHONY: need-week need-main help install test lint check build publish page-json rankings analyze api deploy logs push

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Install the dependencies
	uv sync

test: ## Run the tests
	uv run pytest -q

lint: ## Check the code style
	uv run ruff check src tests

check: lint test ## Run lint, then the tests

# Usage: make build WEEK=7 [SEASON=2026]
build: need-week ## Build the report of a week (WEEK required)
	uv run cornerstone build --season $(SEASON) --week $(WEEK)

# This target pushes the site repo.
publish: need-week ## Publish a week to the site repo and push it (WEEK required)
	uv run cornerstone publish --season $(SEASON) --week $(WEEK)

page-json: need-week ## Write page.json for a saved week (WEEK required)
	uv run cornerstone page-json --season $(SEASON) --week $(WEEK)

rankings: need-week ## Write rankings.json for a saved week (WEEK required)
	uv run cornerstone rankings --season $(SEASON) --week $(WEEK)

# Example: make analyze A=4:7569 B=12:10236,8146 ASKER=4
analyze: ## Grade a trade without the Claude call (A, B, ASKER required)
	@test -n "$(A)" -a -n "$(B)" -a -n "$(ASKER)" || { echo "Set A, B, and ASKER. Example: make analyze A=4:7569 B=12:10236,8146 ASKER=4"; exit 1; }
	uv run cornerstone analyze --season $(SEASON) --side $(A) --side $(B) --asker $(ASKER) --no-claude

api: ## Run the API on port 8080 with a test passphrase
	CORNERSTONE_PASSPHRASE=localtest CORNERSTONE_REPO=$(CURDIR) uv run uvicorn --factory cornerstone_api.app:app_from_env --port 8080

deploy: need-main ## Deploy the API to Fly (main branch, clean tree only)
	fly deploy

logs: ## Show the Fly logs of the API
	fly logs --app cpcfantasy-api

# The refresh cron runs from main.
push: need-main ## Push main to origin (main branch, clean tree only)
	git push origin main

need-week:
	@test -n "$(WEEK)" || { echo "Set WEEK. Example: make $(MAKECMDGOALS) WEEK=7"; exit 1; }

# The tickets under .scratch are untracked by design, so the guard reads only tracked files outside it.
need-main:
	@test "$$(git branch --show-current)" = main || { echo "Stop: the branch is not main."; exit 1; }
	@test -z "$$(git status --porcelain --untracked-files=no -- . ":!.scratch")" || { echo "Stop: the tree has uncommitted changes."; exit 1; }
