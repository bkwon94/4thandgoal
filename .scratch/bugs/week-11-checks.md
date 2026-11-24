# The week 11 data breaks four checks

Kind: bug
Status: in-progress
Branch: `bug-week-11-checks`.
Source: the session of 2026-11-24. The Check of `f44dc5b1` (run 45506075668) failed after the cpc week 11 publish.
Boundary: holds. 4 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The topics test pins the team names of the live rankings

Done condition: `apps/pipeline/tests/test_topics.py` passes on the cpc week 11 data, where some teams have new names.
Method: diagnosing-bugs.
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 2. The analyzer stage spec pins the team names of the live rosters

Done condition: `apps/site/e2e/analyzer-stage.spec.ts` passes on the cpc week 11 build, where roster 2 has a new name.
Method: diagnosing-bugs.
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 3. A team link with a short name is under the tap floor

Done condition: the readability floor of `/2026/managers/7/` at 390px passes on the cpc week 11 build, where a team link shows only "💿 🐑".
Method: diagnosing-bugs.
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 4. A player name splits a word over two lines on the week page

Done condition: the no-split-word check of `/2026/week-11/` passes at 375px and 1280px on the cpc week 11 build, with "David Montgomery" on the page.
Method: diagnosing-bugs.
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Comments
