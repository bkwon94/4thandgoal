# Makefile for the Cornerstone League Weekly site.
# Each target wraps a pnpm script or a deploy step. Run "make" to list them.

.PHONY: help install dev dev-local build test typecheck check serve deploy
.DEFAULT_GOAL := help

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Install the dependencies from the lockfile
	pnpm install --frozen-lockfile

dev: ## Start the dev server
	pnpm dev

# Local test of the analyzer against the API on this machine. First run "make api" in the pipeline repo,
# which serves port 8080 with the passphrase "localtest". Then run this, open the analyzer, and enter that passphrase.
dev-local: ## Start the dev server against the local API on port 8080
	NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm dev

build: ## Build the static site into out/
	pnpm build

test: ## Run the tests
	pnpm test

typecheck: ## Check the types
	pnpm typecheck

# The list of steps lives in the "check" script of package.json, so the hook, CI, and make run the same rules.
check: ## Run typecheck, test, build, and the export check
	pnpm check

# The API must run on port 8080 from the pipeline repo.
serve: ## Build against the local API and serve out/ on port 3000
	NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build
	cd out && python3 -m http.server 3000

# A push to main deploys through GitHub Actions.
deploy: ## Push main to origin, which deploys the site
	@test "$$(git branch --show-current)" = main || { echo "Stop: the current branch is not main."; exit 1; }
	git push origin main
