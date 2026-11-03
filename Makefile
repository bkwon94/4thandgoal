# Root Makefile of the repo. One command checks both apps: "make check".
# Run "make help" to list the targets.

.DEFAULT_GOAL := help
.PHONY: help check check-fast

# The command of each app, per target. Each app owns its rules, so the root only calls them.
site-check = pnpm --dir apps/site check
site-check-fast = pnpm --dir apps/site check:fast
pipeline-check = make -C apps/pipeline check
pipeline-check-fast = make -C apps/pipeline check-fast

# The root scripts have their own tests, such as the Test verdict rule of scripts/verdict.py. They use only the
# Python standard library and take under a second, so both targets run them first, with or without BASE.
# The -B flag writes no __pycache__, so a run leaves the tree clean.
scripts-check = python3 -B -m unittest discover -s scripts -p 'test_*.py'

# With BASE set, only the apps with changed files since the merge base run. See scripts/changed-apps.sh.
# Without BASE, both apps run. The site runs first.
APPS = $(if $(BASE),$(shell scripts/changed-apps.sh $(BASE)),site pipeline)

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-11s %s\n", $$1, $$2}'

# The CI job and the prek hook run these targets. set -e stops the run at the first failure.
# Usage: make check [BASE=origin/main]
check: ## Run the full check of both apps (BASE=<ref> runs only the changed apps)
	@set -e; \
	echo "==> scripts: check"; $(scripts-check); \
	$(if $(strip $(APPS)),$(foreach app,$(APPS),echo "==> $(app): check"; $($(app)-check); ),echo "No app changed since $(BASE). Nothing to run.")

# The hook runs this target on each commit. Install the hook one time per clone with "prek install".
check-fast: ## Run the fast check of both apps (BASE=<ref> runs only the changed apps)
	@set -e; \
	echo "==> scripts: check-fast"; $(scripts-check); \
	$(if $(strip $(APPS)),$(foreach app,$(APPS),echo "==> $(app): check-fast"; $($(app)-check-fast); ),echo "No app changed since $(BASE). Nothing to run.")
