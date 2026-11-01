# Common tasks for the Cornerstone weekly report and its API.
# Run "make help" to list the targets.

SEASON ?= 2026

.DEFAULT_GOAL := help
.PHONY: need-week need-main help install test golden lint typecheck check build publish page-json rankings analyze api deploy logs push

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Install the dependencies
	uv sync

test: ## Run the tests
	uv run pytest -q

# A golden change must show in review, so commit the rewritten files with the code that changed them.
golden: ## Rewrite the four golden files from the week 6 fixtures
	uv run python tests/golden.py

lint: ## Check the code style
	uv run ruff check src tests

# Only the modules that a ticket touches must pass. The include list is in pyproject.toml.
typecheck: ## Check the types of the listed modules in basic mode
	uv run pyright

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

# Example: make analyze SIDES="4:7569@12 12:10236@7 7:11628@4" ASKER=4
# SIDES holds two to four sides, each ROSTER:PLAYER@TO,PLAYER@TO. A two-side trade may still use A=4:7569 B=12:10236.
analyze: ## Grade a trade without the Claude call (SIDES="ROSTER:PLAYER@TO,PLAYER@TO ..." and ASKER required)
	@test -n "$(SIDES)$(A)$(B)" -a -n "$(ASKER)" || { echo "Set SIDES and ASKER. Example: make analyze SIDES=\"4:7569@12 12:10236@4\" ASKER=4"; exit 1; }
	uv run cornerstone analyze --season $(SEASON) $(foreach side,$(or $(SIDES),$(A) $(B)),--side $(side)) --asker $(ASKER) --no-claude

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
