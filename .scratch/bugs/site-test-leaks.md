# Site tests leak temp folders and reach the live API

Kind: bug
Status: in-progress
Branch: `bug-site-test-leaks`.
Source: the queue task `Site tests leave temp folders behind`, and the handoff file `.handoff/2026-11-21-quick-test-fixes.md`, items 1 and 3.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Site tests leave temp folders behind

Done condition: One run of the site `bun test` suite leaves no more entries in the macOS temp folder than it found, for each `mkdtemp` prefix of a site test.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 2. Some site tests call the live API

Done condition: One run of the site `bun test` suite sends no request to `https://api.4thandgoal.app` or to a Fly address, and its output holds no `Cross-Origin Request Blocked` and no `ECONNREFUSED`.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments
