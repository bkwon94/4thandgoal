# The menu label of the season sim is not title case

Kind: bug
Status: done
Branch: `bug-season-sim-label`.
Source: the session of 2026-11-19.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The menu label of the season sim is not title case

Done condition: The menu link of the sim package reads "Season Sim", in title case like the other menu labels such as "Power Rankings" and "Trade Analyzer".
Method: diagnosing-bugs
Cause: `menuLink` in `apps/site/src/app/_routes/sim/menu.ts` sets the label `"Season sim"` in sentence case, so the menu shows it unlike the other title-case labels.
Red: at `2e799df4` with `apps/site/src/app/_routes/sim/menu.test.ts` of `efa25ec6`, `cd apps/site && pnpm exec vitest run src/app/_routes/sim/menu.test.ts`

```text
 FAIL  src/app/_routes/sim/menu.test.ts > the menu link of the sim package > links the sim page of the season of the latest week
AssertionError: expected { label: 'Season sim', …(1) } to deeply equal { label: 'Season Sim', …(1) }
-   "label": "Season Sim",
+   "label": "Season sim",
 Test Files  1 failed (1)
      Tests  1 failed | 3 passed (4)
```

Green: at `efa25ec6`, `cd apps/site && pnpm exec vitest run src/app/_routes/sim/menu.test.ts`

```text
 Test Files  1 passed (1)
      Tests  4 passed (4)
```
Test verdict: PASS

## Smoke

Smoke: none. `pnpm --dir apps/site pick --base main` printed "No flow: no file of the diff matches a glob of the flow list."

## Comments

Closes with the squash merge of the PR of `bug-season-sim-label`. Commits: `efa25ec6`, `b3e45062`. Date: 2026-11-19.
The loop `menu.test.ts` went red at `2e799df4` and green at `efa25ec6`, and `make check-fast BASE=main` passed with 430 site tests and 63 root tests.
The page title, the chapter label of the week tile, and the Announcement eyebrow still read "Season sim", and no smoke flow covers `_routes/sim/`.
Read 6 files: AGENTS.md, apps/site/AGENTS.md, .scratch/bugs/season-sim-label.md, .claude/plugin/skills/quick/format.md, apps/site/src/app/_routes/sim/menu.ts, apps/site/src/app/_routes/sim/menu.test.ts.
