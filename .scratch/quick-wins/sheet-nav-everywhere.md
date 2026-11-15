# The menu sheet replaces the dock on every page

Kind: quick-win
Status: done
Branch: `win-sheet-nav-everywhere`.
Source: the session of 2026-11-15.
Boundary: holds. 1 item of one kind; no new term or ADR, and the `Dock` term leaves `GLOSSARY.md`; no moved seam; each done condition is one sentence.

## Items

### 1. Every page uses the menu sheet on a phone and a tablet, and no page has a dock

Done condition: Below the desktop tier, every page shows the menu button and its sheet in the top band and no dock, while the desktop tier and the front door, with its ask box, its chips, and the place of its ask box above the keyboard on focus, stay as they are.
Method: tdd
Red: at `3d569486` with `packages/design/site/shell/top-band.test.tsx` of `3e81e5d3`, `cd apps/site && pnpm exec vitest run ../../packages/design/site/shell/top-band.test.tsx -t "shows the menu button, and no dock"`

```text
TestingLibraryElementError: Unable to find an accessible element with the role "button" and name "Open the menu"
 ❯ packages/design/site/shell/top-band.test.tsx:238:47
 Test Files  1 failed (1)
      Tests  1 failed | 35 skipped (36)
```
Green: at `3e81e5d3`, `cd apps/site && pnpm exec vitest run ../../packages/design/site/shell/top-band.test.tsx -t "shows the menu button, and no dock"`

```text
 Test Files  1 passed (1)
      Tests  1 passed | 33 skipped (34)
```
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `win-sheet-nav-everywhere`. Commits: `3d569486`, `3e81e5d3`, `b8612607`, `c7d2e05f`. Date: 2026-11-15.
The loop went red on the old band and green on the fix, and `make check-fast` passes with 1521 site tests.
The flaky AT-31 test of `apps/site/src/app/page.test.tsx` fails about 1 run in 6 on `main` too, so it needs its own fix.
The "Grade the Trade" bar now sits at the bottom edge on a phone and a tablet, its place on a desktop.
The Playwright specs, with the changed `apps/site/e2e/floor.spec.ts`, run only in CI.
Read 9 files: AGENTS.md, GLOSSARY.md, docs/agents/issue-tracker.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, packages/design/site/shell/top-band.tsx, packages/design/site/shell/dock.tsx, packages/design/site/shell/menu-sheet.tsx, packages/design/site/shell/README.md, apps/site/src/app/shell-props.ts.
