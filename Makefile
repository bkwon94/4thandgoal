# Root Makefile of the repo. One command checks the three apps and each package: "make check".
# Run "make help" to list the targets.

.DEFAULT_GOAL := help
.PHONY: help check check-fast check-scripts check-site check-site-unit check-site-browser check-pipeline check-pipeline-parallel check-pipeline-serial check-api check-packages

# The command of each app, per target. Each app owns its rules, so the root only calls them.
site-check = pnpm --dir apps/site check
# A selected run of the site tests only the vitest files that the changed files reach through imports. VITEST_CHANGED is
# empty without a selection, so the site still runs every vitest file. "make check-site" never sets it, so CI runs all.
# A git hook sets GIT_DIR and GIT_INDEX_FILE and no GIT_WORK_TREE, so git takes the folder of the command as the top of the
# work tree. Vitest runs git from apps/site, would see every file as changed, and would select all of them. The env -u
# calls make git find the work tree from the folder, as it does outside a hook.
site-check-fast = VITEST_CHANGED="$(VITEST_CHANGED)" LINT_FILES="$(LINT_FILES)" FMT_FILES="$(FMT_FILES)" env -u GIT_DIR -u GIT_INDEX_FILE -u GIT_PREFIX -u GIT_WORK_TREE pnpm --dir apps/site check:fast
pipeline-check = make -C apps/pipeline check
pipeline-check-fast = make -C apps/pipeline check-fast
pipeline-check-parallel = make -C apps/pipeline check-parallel
pipeline-check-serial = make -C apps/pipeline check-serial
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
# and each member that needs it. A change outside apps/ and packages/, such as a root file, selects every one,
# except a change under .scratch/ or docs/, which selects only the members whose tests read it.
# The hook sets STAGED=1 to use the commit index. Without either option, run every member. The site runs first.
# See scripts/changed_apps.py for the shared rules.
ALL_APPS = site pipeline api
SELECTION = $(if $(filter 1,$(STAGED)),--staged,$(BASE))
ifeq ($(STAGED),1)
CHANGED := $(shell python3 -B scripts/changed_apps.py --staged || echo selection-failed)
ifeq ($(CHANGED),selection-failed)
$(error Cannot select staged checks)
endif
else
CHANGED = $(if $(BASE),$(shell python3 -B scripts/changed_apps.py $(BASE)))
endif
APPS = $(if $(SELECTION),$(filter $(ALL_APPS),$(CHANGED)),$(ALL_APPS))
# The hook lints only the staged site files, as paths from the repo root. LINT_FILES is empty without STAGED=1, and the
# lint script of the site then lints all site code. The paths leave out packages/design/lint/fixtures/, which break the
# rules on purpose for the rule test.
LINT_FILES = $(if $(filter 1,$(STAGED)),$(shell git diff --cached --name-only --diff-filter=d -- 'apps/site/*.ts' 'apps/site/*.tsx' 'apps/site/*.mjs' 'packages/*/site/*.ts' 'packages/*/site/*.tsx' packages/design/lint/plugin.mjs))
# The hook checks the format of the same staged files, plus the CSS files. FMT_FILES is empty without STAGED=1, and the
# fmt scripts of the site then take all site code and package code.
FMT_FILES = $(if $(filter 1,$(STAGED)),$(shell git diff --cached --name-only --diff-filter=d -- 'apps/site/*.ts' 'apps/site/*.tsx' 'apps/site/*.mjs' 'apps/site/*.mts' 'apps/site/*.css' 'packages/*/site/*.ts' 'packages/*/site/*.tsx' 'packages/*/site/*.css' packages/design/lint/plugin.mjs))
VITEST_CHANGED = $(if $(filter 1,$(STAGED)),--changed,$(if $(BASE),--changed $(BASE)))
PACKAGES = $(if $(SELECTION),$(filter-out $(ALL_APPS),$(CHANGED)),$(notdir $(wildcard packages/*)))

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

# The local full run and the prek hook run these targets. set -e stops the run at the first failure.
# Usage: make check [BASE=origin/main]
check: ## Run the full check of every app and package (BASE=<ref> runs only the changed ones)
	@set -e; \
	echo "==> scripts: check"; $(scripts-check); \
	$(if $(strip $(APPS) $(PACKAGES)),$(foreach app,$(APPS),echo "==> $(app): check"; $($(app)-check); )$(foreach pkg,$(PACKAGES),echo "==> packages/$(pkg): check"; $(call package-check,$(pkg),check)),echo "No app or package changed since $(BASE). Nothing to run.")

# The hook calls this target with STAGED=1. Install the hook one time per clone with "prek install".
check-fast: ## Run fast checks (BASE=<ref> selects changes since the merge base, STAGED=1 selects the commit index)
	@set -e; \
	echo "==> scripts: check-fast"; $(scripts-check); \
	$(if $(strip $(APPS) $(PACKAGES)),$(foreach app,$(APPS),echo "==> $(app): check-fast"; $($(app)-check-fast); )$(foreach pkg,$(PACKAGES),echo "==> packages/$(pkg): check-fast"; $(call package-check,$(pkg),check-fast)),echo "$(if $(filter 1,$(STAGED)),No app or package has staged changes.,No app or package changed since $(BASE).) Nothing to run.")

# One target per member, for the CI job of that member. Each one runs the full check of its member and ignores BASE,
# because CI always runs every member. "make check" runs the same commands in sequence.
# The -v flag lists each case, so the CI log names each test of the root scripts.
check-scripts: ## Run the full check of the root scripts
	@echo "==> scripts: check"; $(scripts-check) -v

check-site: ## Run the full check of the site
	@echo "==> site: check"; $(site-check)

# CI splits the full check of the site into two jobs that run at the same time. "make check-site" runs both halves in
# sequence: the unit half first, then the browser half.
check-site-unit: ## Run the unit half of the site check: the lint, the client build, typecheck, and all vitest files
	@echo "==> site: check:fast"; pnpm --dir apps/site check:fast

check-site-browser: ## Run the browser half of the site check: Playwright and the export of each client
	@echo "==> site: check:browser"; pnpm --dir apps/site check:browser

check-pipeline: ## Run the full check of the pipeline
	@echo "==> pipeline: check"; $(pipeline-check)

# CI splits the full check of the pipeline into two jobs that run at the same time. "make check-pipeline" runs both halves.
check-pipeline-parallel: ## Run the parallel half of the pipeline check: lint, typecheck, and the parallel tests
	@echo "==> pipeline: check-parallel"; $(pipeline-check-parallel)

check-pipeline-serial: ## Run the serial half of the pipeline check: the tests that measure wall time
	@echo "==> pipeline: check-serial"; $(pipeline-check-serial)

check-api: ## Run the full check of the API
	@echo "==> api: check"; $(api-check)

# The packages run one after another, because two "uv run --exact --package" runs in one checkout break each other.
check-packages: ## Run the full check of each package
	@set -e; \
	$(foreach pkg,$(notdir $(wildcard packages/*)),echo "==> packages/$(pkg): check"; $(call package-check,$(pkg),check))
