# Common tasks for the Python side of the league package: the check and the export of the client schema.
# Run "make help" to list the targets. The root Makefile runs check and check-fast for each selected package.

.DEFAULT_GOAL := help
.PHONY: help install test lint typecheck rules check check-fast schema

# Each command runs in the env of this member only. --exact removes each package it does not list,
# so an import of an app fails here (decision 07).
RUN = uv run --exact --package cpc-league

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-11s %s\n", $$1, $$2}'

install: ## Install the dependencies
	uv sync --exact --package cpc-league

test: ## Run the tests
	$(RUN) pytest -q

lint: ## Check the code style
	$(RUN) ruff check src tests

# Only the modules that a ticket touches must pass. The include list is in pyproject.toml.
typecheck: ## Check the types of the listed modules in basic mode
	$(RUN) pyright

# The rule tests of the pipeline run on this package through tests/test_rule_league.py.
rules: ## Run the rule tests
	$(RUN) pytest -q tests/test_rule_league.py

# The CI job on every push runs this target.
check: lint typecheck test ## Run lint, typecheck, and all the tests

# The prek hook runs this target on each commit, so it must stay fast. The package tests take a few seconds.
check-fast: lint typecheck test ## Run lint, typecheck, and the tests

# The site build checks the kernel keys of client.toml and [values.league] with these two files, so commit them with
# the model change that rewrote them.
schema: ## Rewrite the exported JSON Schemas of the kernel keys and of the package values
	$(RUN) python -c "from league.client import ClientValues, write_schema_file; from league.values import LeagueValues; print(write_schema_file(ClientValues)); print(write_schema_file(LeagueValues))"
