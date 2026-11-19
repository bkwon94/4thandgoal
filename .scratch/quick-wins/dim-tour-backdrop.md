# Dim the onboarding tour backdrop

Kind: quick-win
Status: done
Branch: `win-dim-tour-backdrop`.
Source: the session of 2026-11-19.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Dim the onboarding tour backdrop

Done condition: The tour dims the page more in both themes while the spotlight and tour card stay clear.
Method: text only.
Red: none, text only.
Green: at `92228e3f`, the tour backdrop changes from 45% to 65% black.
Test verdict: none

## Comments

The phone-size preview shows the new shade in both themes. Team selection opens the tour. Next and Skip work in both themes.

Closes with the squash merge of the PR of `win-dim-tour-backdrop`. Commits: `1a95c05d`, `92228e3f`, `c9cc59b2`. Date: 2026-11-19.
Fast checks pass with 149 script tests, 282 site tests, and 63 pipeline tests.
Read 12 files: AGENTS.md, apps/site/AGENTS.md, docs/agents/issue-tracker.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, GLOSSARY.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/implement/build.md, apps/site/src/app/globals.css, apps/site/src/app/front-door/tour.tsx, apps/site/src/app/front-door/front-door.tsx, apps/site/e2e/front-door-tour-look.spec.ts, apps/site/e2e/front-door-tour-replay.spec.ts.
