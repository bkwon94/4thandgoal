# Common tasks for the Cornerstone weekly report. The API app has its own Makefile in apps/api.
# Run "make help" to list the targets.

SEASON ?= 2026
# The client slug: the name of its folder under clients/. Each league command needs it, so it has no default.
CLIENT ?=

# Each command runs in the env of this member only. --exact removes each package it does not list, such as the API,
# so an import of an unlisted package fails here as it fails in the deploy (decision 07).
RUN = uv run --exact --package cornerstone

.DEFAULT_GOAL := help

.PHONY: need-week need-client need-main settings help install test golden lint typecheck rules check check-fast build publish page-json rankings analyze push

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-11s %s\n", $$1, $$2}'

install: ## Install the dependencies
	uv sync --exact --package cornerstone

# The tests share no files or data, so they run in parallel. A test that measures wall time is marked serial and runs alone. See .scratch/fast-cycle/decisions/09-research-parallel-pytest.md.
# The serial pass runs each serial test with its full assertion, alone, so no check gets weaker.
# Each -m replaces the -m of addopts in pyproject.toml, so each pass also leaves out live.
test: ## Run the tests
	$(RUN) pytest -q -n auto -m 'not live and not serial'
	$(RUN) pytest -q -p no:xdist -m 'serial and not live'

# A golden change must show in review, so commit the rewritten files with the code that changed them.
golden: ## Rewrite the four golden files from the week 6 fixtures
	$(RUN) python tests/golden.py

lint: ## Check the code style
	$(RUN) ruff check src tests

# Only the modules that a ticket touches must pass. The include list is in pyproject.toml.
typecheck: ## Check the types of the listed modules in basic mode
	$(RUN) pyright

# The CI job on every push runs this target. See docs/adr/0014-the-rules-are-checks.md.
check: lint typecheck test ## Run lint, typecheck, and all the tests

# Name a rule test tests/test_rule_<topic>.py. This target finds each one with no edit.
rules: ## Run the rule tests
	$(RUN) pytest -q tests/test_layers.py $(wildcard tests/test_rule_*.py)

# The prek hook runs this target on each commit, so it must stay under 30 seconds.
# Install the hook one time per clone with "prek install".
check-fast: lint typecheck rules ## Run lint, typecheck, and the rule tests

# Usage: make build CLIENT=cpc WEEK=7 [SEASON=2026]
build: need-client need-week ## Build the report of a week (CLIENT and WEEK required)
	$(RUN) cornerstone build --client $(CLIENT) --season $(SEASON) --week $(WEEK)

# This target commits the build, data, and published folders of the season under clients/$(CLIENT)/ and pushes the repo.
publish: need-client need-week ## Publish a week to clients/$(CLIENT)/published and push it (CLIENT and WEEK required)
	$(RUN) cornerstone publish --client $(CLIENT) --season $(SEASON) --week $(WEEK)

page-json: need-client need-week ## Write page.json for a saved week (CLIENT and WEEK required)
	$(RUN) cornerstone page-json --client $(CLIENT) --season $(SEASON) --week $(WEEK)

rankings: need-client need-week ## Write rankings.json for a saved week (CLIENT and WEEK required)
	$(RUN) cornerstone rankings --client $(CLIENT) --season $(SEASON) --week $(WEEK)

# Example: make analyze CLIENT=cpc SIDES="4:7569@12 12:10236@7 7:11628@4" ASKER=4
# SIDES holds two to four sides, each ROSTER:PLAYER@TO,PLAYER@TO. A two-side trade may still use A=4:7569 B=12:10236.
analyze: need-client ## Grade a trade without the Claude call (SIDES="ROSTER:PLAYER@TO,PLAYER@TO ..." and ASKER required)
	@test -n "$(SIDES)$(A)$(B)" -a -n "$(ASKER)" || { echo "Set SIDES and ASKER. Example: make analyze SIDES=\"4:7569@12 12:10236@4\" ASKER=4"; exit 1; }
	$(RUN) cornerstone analyze --client $(CLIENT) --season $(SEASON) $(foreach side,$(or $(SIDES),$(A) $(B)),--side $(side)) --asker $(ASKER) --no-claude

settings: need-client ## Print the League settings and the derived sizes of a season (CLIENT required)
	$(RUN) cornerstone settings --client $(CLIENT) --season $(SEASON)

# The refresh cron runs from main.
push: need-main ## Push main to origin (main branch, clean tree only)
	git push origin main

need-client:
	@test -n "$(CLIENT)" || { echo "Set CLIENT, the client slug. Example: make $(MAKECMDGOALS) CLIENT=cpc WEEK=8"; exit 1; }

need-week:
	@test -n "$(WEEK)" || { echo "Set WEEK. Example: make $(MAKECMDGOALS) WEEK=7"; exit 1; }

# The guard reads only the tracked files of the pipeline folder. The tracker is the root .scratch, outside it.
need-main:
	@test "$$(git branch --show-current)" = main || { echo "Stop: the branch is not main."; exit 1; }
	@test -z "$$(git status --porcelain --untracked-files=no -- .)" || { echo "Stop: the tree has uncommitted changes."; exit 1; }
