# The menu sheet replaces the dock on every page

Kind: quick-win
Status: in-progress
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
