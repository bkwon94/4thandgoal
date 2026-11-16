# The analyzer opens with the team of the front door

Kind: quick-win
Status: done
Branch: `win-analyzer-your-team`.
Source: the session of 2026-11-16.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam, because the analyzer reads the existing local storage key `cpc.your-team`; each done condition is one sentence.

## Items

### 1. The analyzer fills the first team from the team of the front door

Done condition: When `/analyze/` opens with no team in its query and the front door stored a team in `cpc.your-team`, the first side of the trade form shows that team, and a team in the query still wins.
Method: tdd
Red: at `74164e68` with `packages/analyzer/site/form/analyzer.test.tsx` of `6cda97a8`, `cd apps/site && npx vitest run ../../packages/analyzer/site/form/analyzer.test.tsx -t "team of the front door"`

```text
AssertionError: expected 'Pick Your Team' to match /^Your Team: Blitz Bakers/
 Test Files  1 failed (1)
      Tests  1 failed | 18 skipped (19)
```

Green: at `6cda97a8`, `cd apps/site && npx vitest run ../../packages/analyzer/site/form/analyzer.test.tsx -t "team of the front door"`

```text
 Test Files  1 passed (1)
      Tests  1 passed | 18 skipped (19)
```

The hook of `6cda97a8` and `make check-fast BASE=main` passed: 147 files, 1523 tests.

Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `win-analyzer-your-team`. Commits: `74164e68`, `6cda97a8`, `1c30ca0b`, `0d8de7e7`. Date: 2026-11-16.
The loop of item 1 went red at `74164e68` and green at `6cda97a8`, and `make check-fast BASE=main` passed 1523 tests in 147 files.
A stored team that is not in the roster list of the season shows as no pick, because the form finds no team for the id.
Read 9 files: AGENTS.md, apps/site/AGENTS.md, apps/site/src/app/front-door/your-team-store.ts, packages/analyzer/site/form/analyzer.tsx, packages/analyzer/site/form/trade-form.tsx, packages/analyzer/site/lib/prefill.ts, packages/analyzer/site/lib/teams-store.ts, packages/analyzer/site/form/analyzer.test.tsx, .claude/plugin/skills/quick/format.md.
