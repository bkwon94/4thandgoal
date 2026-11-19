# Common tasks for the Cornerstone weekly report. The API app has its own Makefile in apps/api.
# Run "make help" to list the targets.

SEASON ?= 2026
# The client slug: the name of its folder under clients/. Each league command needs it, so it has no default.
CLIENT ?=
# The egg file of the commissioner. Empty means ~/cpc-eggs/<season>.toml, outside the repo. A test names a temp file.
EGGS_FILE ?=
EGGS_ARG = $(if $(EGGS_FILE),--eggs-file $(EGGS_FILE))

# Each command runs in the env of this member only. --exact removes each package it does not list, such as the API,
# so an import of an unlisted package fails here as it fails in the deploy (decision 07).
RUN = uv run --exact --package cornerstone

.DEFAULT_GOAL := help

.PHONY: need-week need-client need-main settings spares-list backtest help install test golden lint typecheck rules check check-fast build publish egg-draft egg-drop page-json facts rankings sim sim-fixtures midseason midseason-publish egg-undo push

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
# Its last step sends the confirmed eggs of the week to the API. A failed drop warns, and make egg-drop retries.
publish: need-client need-week ## Publish a week to clients/$(CLIENT)/published and push it (CLIENT and WEEK required)
	$(RUN) cornerstone publish --client $(CLIENT) --season $(SEASON) --week $(WEEK) $(EGGS_ARG)

# The agent reads the catalog, the survey notes, the built week page, and the eggs that dropped before.
egg-draft: need-client need-week ## Propose the six egg spots of a week, marked not confirmed (CLIENT and WEEK required)
	$(RUN) cornerstone egg-draft --client $(CLIENT) --season $(SEASON) --week $(WEEK) $(EGGS_ARG)

# It reads CORNERSTONE_API_URL and CORNERSTONE_COMMISSIONER_KEY_<SLUG>. A failed drop warns and exits 0.
egg-drop: need-client need-week ## Send the confirmed eggs of a week to the API (CLIENT and WEEK required)
	$(RUN) cornerstone egg-drop --client $(CLIENT) --season $(SEASON) --week $(WEEK) $(EGGS_ARG)

page-json: need-client need-week ## Write page.json for a saved week (CLIENT and WEEK required)
	$(RUN) cornerstone page-json --client $(CLIENT) --season $(SEASON) --week $(WEEK)

facts: need-client need-week ## Rebuild facts.json of a saved week from its saved inputs (CLIENT and WEEK required)
	$(RUN) cornerstone facts --client $(CLIENT) --season $(SEASON) --week $(WEEK)

rankings: need-client need-week ## Write rankings.json for a saved week (CLIENT and WEEK required)
	$(RUN) cornerstone rankings --client $(CLIENT) --season $(SEASON) --week $(WEEK)

# It reads the saved data of the week and calls no writer and no network. It writes only to the build folder.
sim: need-client need-week ## Write week-NN/sim.json for a saved week, the sim step of the build (CLIENT and WEEK required)
	$(RUN) cornerstone sim --client $(CLIENT) --season $(SEASON) --week $(WEEK)

# The playoff fixture and the season-end fixture of the sim page tests (season-sim ACCEPTANCE.md): the inputs of CPC
# 2026 week 10 with the later weeks played as stored run 1. It writes only the fixture folder of the sim package.
sim-fixtures: ## Write the playoff and season-end fixtures of the sim page tests from CPC 2026 week 10
	$(RUN) cornerstone sim-fixtures --client cpc --season 2026 --week 10 --out ../../packages/sim/site/fixtures

# The report is one edited moment per season, so only this target builds it, never the weekly build.
# It writes only to the build folder of the season, never to published/.
midseason: need-client need-week ## Write the midseason report of a saved week (CLIENT and WEEK required)
	$(RUN) cornerstone midseason --client $(CLIENT) --season $(SEASON) --week $(WEEK)

# It checks each blurb of the draft again and refuses on a failure. It commits only midseason.json and sim.json of the
# published season folder, then pushes the repo, as the weekly publish does.
midseason-publish: need-client need-week ## Check the midseason draft, then commit it to published and push it (CLIENT and WEEK required)
	$(RUN) cornerstone midseason-publish --client $(CLIENT) --season $(SEASON) --week $(WEEK)

settings: need-client ## Print the League settings and the derived sizes of a season (CLIENT required)
	$(RUN) cornerstone settings --client $(CLIENT) --season $(SEASON)

# The two commands of the Finder backtest call the live Jev on the live week, so make check-fast never runs them.
# TYPESAFE_API_KEY must be set. The marks file holds Brian's Backtest marks (decision 05).
MARKS ?= ../../.scratch/deadline-week/backtest-marks.json
spares-list: need-client ## Print about 30 Spares tree stops and passes of the live week for Brian to mark (CLIENT required)
	$(RUN) cornerstone spares-list --client $(CLIENT) --season $(SEASON)

backtest: need-client ## Check each Backtest mark against the tree with the live Jev (CLIENT required, MARKS optional)
	$(RUN) cornerstone backtest --client $(CLIENT) --season $(SEASON) --marks $(MARKS)

# The commissioner key of the client comes from the env CORNERSTONE_COMMISSIONER_KEY_<SLUG>, such as ..._CPC. The API
# base URL is CORNERSTONE_API_URL. It defaults to the live API, the same default as egg-drop (eggs.keys.API_URL).
# A local run sets CORNERSTONE_API_URL, such as http://127.0.0.1:8080 for "make api" in apps/api.
# Example: make egg-undo CLIENT=cpc EGG=12
CORNERSTONE_API_URL ?= $(shell $(RUN) python -c "from eggs.keys import API_URL; print(API_URL)")
COMMISSIONER_KEY_ENV = CORNERSTONE_COMMISSIONER_KEY_$(shell echo $(CLIENT) | tr a-z A-Z)
egg-undo: need-client ## Undo the claim of an egg so the egg is live again (CLIENT and EGG required)
	@test -n "$(EGG)" || { echo "Set EGG, the egg id. Example: make egg-undo CLIENT=cpc EGG=12"; exit 1; }
	@test -n "$${$(COMMISSIONER_KEY_ENV)}" || { echo "Set $(COMMISSIONER_KEY_ENV), the commissioner key of $(CLIENT)."; exit 1; }
	@curl --fail-with-body --silent --show-error -X POST "$(CORNERSTONE_API_URL)/clients/$(CLIENT)/eggs/undo" \
		-H "X-Commissioner-Key: $${$(COMMISSIONER_KEY_ENV)}" -H "Content-Type: application/json" -d '{"egg_id": $(EGG)}'
	@echo

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
