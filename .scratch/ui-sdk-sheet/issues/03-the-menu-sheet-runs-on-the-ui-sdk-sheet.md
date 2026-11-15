# 03: The menu sheet runs on the ui-sdk sheet

Spec: `.scratch/ui-sdk-sheet/PRD.md`. Acceptance tests AT-1 to AT-31, AT-35, AT-38, and AT-39.

**App:** site

**What to build:** The menu sheet of the front door runs on the sheet wrapper of ticket 02. It drops from the top band with `side="top"`, one snap point at the height of its rows, a grab handle at its bottom edge, and the default `sheetPhysics.ios`. The dim follows `--drawer-dim`, and the page does not scale. Under reduced motion the sheet fades and does not slide (ADR 0034). A CSS rule keeps the band and its X above the sheet and the dim, and `persistentElements` keeps the band usable. The sheet is modal, so the focus stays in the sheet and the band. The rows, the notes, the check, the week row, and "Past weeks" stay as they are. The hand-built drag code goes. The prototype on the branch `ui-sdk-sheet-08-prototype` shows the band rule. Rewrite it, and do not merge that branch.

**Blocked by:** 01, 02

**Status:** done

- [x] On a 390 x 844 touch phone, the sheet follows the finger, settles on a spring, closes on a flick and on a slow drag past half its height, and goes back after a short drag (AT-1 to AT-6).
- [x] A 5 px move on a row opens the row, and a 30 px move does not (AT-7, AT-8).
- [x] The sheet shows the handle and every row at one height, and "Past weeks" pushes the rows down (AT-9 to AT-11).
- [x] The dim follows the drag, a tap on it closes the sheet, the X sits in the place of the menu icon, and the band stays on top (AT-12 to AT-15).
- [x] The rows, the check, the week row, and the chips match AT-16 to AT-19.
- [x] The sheet fades under reduced motion (AT-20).
- [x] The focus, Escape, the accessibility tree, and the names match AT-21 to AT-26.
- [x] The desktop shows the pill bar, and no menu button shows with scripts off (AT-27, AT-28).
- [x] A dock page loads no more code than on `main`, and the first tap on the front door loads no new script (AT-29, AT-30).
- [x] The sheet keeps the look of `cpc` and of `norcal` (AT-31).
- [x] The menu sheet holds no hand-built drag code (AT-35).
- [x] The other four sheets, the dock, the pill bar, and the CI workflows do not change (AT-38, AT-39).
- [x] The top band tests check the open, the rows, the X, the focus, and each close, and a Tab keeps the focus in the sheet.
- [x] `make check-fast` passes at the root.

## Comments

The merge: `70ca4fc1` on `ui-sdk-sheet-03`, merged into `ui-sdk-sheet` on 2026-11-14, with review fixes P4 `eee6e29d`, P6 `04614dc3`, and S7 `f2503ac0`.
The proof: The full check passed with 1523 of 1523 site tests, and the Judge gave PASS to AT-1 to AT-39.
The note: A phone check on iOS Safari of the touch drag is still open, because the evidence ran in Chromium emulation.
Read at least 9 files: AGENTS.md, apps/site/AGENTS.md, .scratch/ui-sdk-sheet/PRD.md, .scratch/ui-sdk-sheet/ACCEPTANCE.md, .scratch/ui-sdk-sheet/issues/03-the-menu-sheet-runs-on-the-ui-sdk-sheet.md, packages/design/site/shell/menu-sheet.tsx, packages/design/site/shell/top-band.test.tsx, packages/design/site/ui/sheet.tsx, apps/site/src/app/globals.css.
Closes with the squash merge of the spec PR.
