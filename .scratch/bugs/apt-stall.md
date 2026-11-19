# The apt step of site-browser stalls on a slow mirror

Kind: bug
Status: in-progress
Branch: `bug-apt-stall`.
Source: the session of 2026-11-19. PR #80 failed `site-browser` because the apt step took 18.7 min.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The system packages of Chromium and WebKit come from the Ubuntu mirror on each run

Done condition: Each workflow step that runs `playwright install-deps` or `install --with-deps` first restores its apt packages from the GitHub Actions cache, and a rule script fails the check when a step does not.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: none, no site or API change.

## Comments

- Run 44626873845 of PR #80: "Fetched 140 MB in 17min 59s (130 kB/s)" in the step "Install the system packages of Chromium and WebKit", so the 25 min job limit stopped the browser tests. Run 44599815183 took 15.1 min in the same step. Other runs took under 1 min.
