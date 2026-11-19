# The apt step of site-browser stalls on a slow mirror

Kind: bug
Status: done
Branch: `bug-apt-stall`.
Source: the session of 2026-11-19. PR #80 failed `site-browser` because the apt step took 18.7 min.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The system packages of Chromium and WebKit come from the Ubuntu mirror on each run

Done condition: Each workflow step that runs `playwright install-deps` or `install --with-deps` first restores its apt packages from the GitHub Actions cache, and a rule script fails the check when a step does not.
Method: diagnosing-bugs
Cause: the job `site-browser` in `.github/workflows/check.yml` caches only `~/.cache/ms-playwright`, and the job `rerun` in `.github/workflows/rerun.yml` caches nothing, so each `playwright install-deps` or `install --with-deps` downloads about 140 MB of .deb files from the Ubuntu mirror, and a slow mirror stalls the job.
Red: at `ec4d4c6e` with `scripts/apt_cache_rule.py` of `60737881`, `python3 -B scripts/apt_cache_rule.py`

```text
.github/workflows/check.yml:120 job site-browser installs system packages with no earlier step that restores ~/.cache/apt-archives: run: pnpm --dir apps/site exec playwright install --with-deps chromium webkit
.github/workflows/check.yml:125 job site-browser installs system packages with no earlier step that restores ~/.cache/apt-archives: run: pnpm --dir apps/site exec playwright install-deps chromium webkit
.github/workflows/rerun.yml:99 job rerun installs system packages with no earlier step that restores ~/.cache/apt-archives: run: pnpm --dir apps/site exec playwright install --with-deps chromium webkit
FAILED: 3 steps install system packages with no apt cache.
```

Green: at `60737881`, `python3 -B scripts/apt_cache_rule.py`

```text
(no output; the exit code is 0)
```
Test verdict: PASS

## Smoke

Smoke: none, no site or API change.

## Comments

- Run 44626873845 of PR #80: "Fetched 140 MB in 17min 59s (130 kB/s)" in the step "Install the system packages of Chromium and WebKit", so the 25 min job limit stopped the browser tests. Run 44599815183 took 15.1 min in the same step. Other runs took under 1 min.
- Closes with the squash merge of the PR of `bug-apt-stall`. Commits: `60737881`. Date: 2026-11-19.
- The rule went red on 3 steps at `ec4d4c6e` and green at `60737881`; `make check-fast BASE=main` passes, with 217 script tests.
- Later: the first CI run of the PR is a cache miss that saves the .deb files, and the second run shows the hit; `apt-get update` still reads the package lists from the mirror.
- Read 3 files: AGENTS.md, .github/workflows/check.yml, .claude/plugin/skills/quick/format.md; the count of the builder subagent is not in this line.
