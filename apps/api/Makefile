# Common tasks for the Cornerstone API app: the check, the local run, and the deploy to Fly.
# Run "make help" to list the targets.

.DEFAULT_GOAL := help
.PHONY: need-main help install test lint typecheck rules check check-fast api image deploy logs

# Each command runs in the env of this member only. --exact removes each package it does not list,
# so an import of an unlisted package fails here as it fails in the deploy (decision 07).
RUN = uv run --exact --package cpc-api
# The root of the repo. The image builds from it, because the API is a member of the root uv workspace.
ROOT = $(abspath $(CURDIR)/../..)

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-11s %s\n", $$1, $$2}'

install: ## Install the dependencies
	uv sync --exact --package cpc-api

test: ## Run the tests
	$(RUN) pytest -q

lint: ## Check the code style
	$(RUN) ruff check src tests

# Only the modules that a ticket touches must pass. The include list is in pyproject.toml.
typecheck: ## Check the types of the listed modules in basic mode
	$(RUN) pyright

# The rule tests of the pipeline run on this app through tests/test_rule_api.py.
rules: ## Run the rule tests
	$(RUN) pytest -q tests/test_rule_api.py

# The CI job on every push runs this target. See docs/adr/0014-the-rules-are-checks.md.
check: lint typecheck test ## Run lint, typecheck, and all the tests

# The prek hook runs this target on each commit, so it must stay under 30 seconds.
check-fast: lint typecheck rules ## Run lint, typecheck, and the rule tests

# The API reads clients/ and data/ under the repo root, so the repo it reads is the root.
# Each client needs its own passphrase, so the target sets one for each folder under clients/, such as
# CORNERSTONE_PASSPHRASE_CPC=localtest.
PASSPHRASES = $(foreach slug,$(notdir $(wildcard $(ROOT)/clients/*)),CORNERSTONE_PASSPHRASE_$(shell echo $(slug) | tr a-z A-Z)=localtest)

api: ## Run the API on port 8080 with the test passphrase localtest for each client
	$(PASSPHRASES) CORNERSTONE_REPO=$(ROOT) $(RUN) uvicorn --factory cornerstone_api.app:app_from_env --port 8080

image: ## Build the image of the API with the local Docker
	docker build -f $(ROOT)/apps/api/Dockerfile -t cpcfantasy-api $(ROOT)

# The build context is the repo root, so each path goes to flyctl as a flag.
deploy: need-main ## Deploy the API to Fly (main branch, clean tree only)
	cd $(ROOT) && fly deploy . --config apps/api/fly.toml --dockerfile apps/api/Dockerfile --ignorefile apps/api/Dockerfile.dockerignore

logs: ## Show the Fly logs of the API
	fly logs --app cpcfantasy-api

# The guard reads only the tracked files of the API folder.
need-main:
	@test "$$(git branch --show-current)" = main || { echo "Stop: the branch is not main."; exit 1; }
	@test -z "$$(git status --porcelain --untracked-files=no -- .)" || { echo "Stop: the tree has uncommitted changes."; exit 1; }
