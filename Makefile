# Root Makefile of the repo. One command checks the three apps and each package: "make check".
# Run "make help" to list the targets.

.DEFAULT_GOAL := help
.PHONY: help check check-fast

# The command of each app, per target. Each app owns its rules, so the root only calls them.
site-check = pnpm --dir apps/site check
site-check-fast = pnpm --dir apps/site check:fast
pipeline-check = make -C apps/pipeline check
pipeline-check-fast = make -C apps/pipeline check-fast
api-check = make -C apps/api check
api-check-fast = make -C apps/api check-fast
# The check of a package runs its Python side. The check of the site app typechecks and tests the site side of each
# package, and a change in a package always selects the site, because the site depends on each package.
package-check = $(if $(wildcard packages/$(1)/python),make -C packages/$(1)/python $(2); ,echo "The site check covers it."; )

# The root scripts have their own tests, such as the Test verdict rule of scripts/verdict.py. They use only the
# Python standard library and take under a second, so both targets run them first, with or without BASE.
# The -B flag writes no __pycache__, so a run leaves the tree clean.
scripts-check = python3 -B -m unittest discover -s scripts -p 'test_*.py'

# With BASE set, only the apps and the packages that a change since the merge base selects run: each changed member,
# and each member that needs it. A change outside apps/ and packages/, such as a root file, selects every one.
# See scripts/changed_apps.py. Without BASE, every app and every package runs. The site runs first.
ALL_APPS = site pipeline api
CHANGED = $(if $(BASE),$(shell python3 -B scripts/changed_apps.py $(BASE)))
APPS = $(if $(BASE),$(filter $(ALL_APPS),$(CHANGED)),$(ALL_APPS))
PACKAGES = $(if $(BASE),$(filter-out $(ALL_APPS),$(CHANGED)),$(notdir $(wildcard packages/*)))

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-11s %s\n", $$1, $$2}'

# The CI job and the prek hook run these targets. set -e stops the run at the first failure.
# Usage: make check [BASE=origin/main]
check: ## Run the full check of every app and package (BASE=<ref> runs only the changed ones)
	@set -e; \
	echo "==> scripts: check"; $(scripts-check); \
	$(if $(strip $(APPS) $(PACKAGES)),$(foreach app,$(APPS),echo "==> $(app): check"; $($(app)-check); )$(foreach pkg,$(PACKAGES),echo "==> packages/$(pkg): check"; $(call package-check,$(pkg),check)),echo "No app or package changed since $(BASE). Nothing to run.")

# The hook runs this target on each commit. Install the hook one time per clone with "prek install".
check-fast: ## Run the fast check of every app and package (BASE=<ref> runs only the changed ones)
	@set -e; \
	echo "==> scripts: check-fast"; $(scripts-check); \
	$(if $(strip $(APPS) $(PACKAGES)),$(foreach app,$(APPS),echo "==> $(app): check-fast"; $($(app)-check-fast); )$(foreach pkg,$(PACKAGES),echo "==> packages/$(pkg): check-fast"; $(call package-check,$(pkg),check-fast)),echo "No app or package changed since $(BASE). Nothing to run.")
