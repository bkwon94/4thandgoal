# 03: The menu sheet runs on the ui-sdk sheet

Spec: `.scratch/ui-sdk-sheet/PRD.md`. Acceptance tests AT-1 to AT-31, AT-35, AT-38, and AT-39.

**App:** site

**What to build:** The menu sheet of the front door runs on the sheet wrapper of ticket 02. It drops from the top band with `side="top"`, one snap point at the height of its rows, a grab handle at its bottom edge, and the default `sheetPhysics.ios`. The dim follows `--drawer-dim`, and the page does not scale. Under reduced motion the sheet fades and does not slide (ADR 0034). A CSS rule keeps the band and its X above the sheet and the dim, and `persistentElements` keeps the band usable. The sheet is modal, so the focus stays in the sheet and the band. The rows, the notes, the check, the week row, and "Past weeks" stay as they are. The hand-built drag code goes. The prototype on the branch `ui-sdk-sheet-08-prototype` shows the band rule. Rewrite it, and do not merge that branch.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] On a 390 x 844 touch phone, the sheet follows the finger, settles on a spring, closes on a flick and on a slow drag past half its height, and goes back after a short drag (AT-1 to AT-6).
- [ ] A 5 px move on a row opens the row, and a 30 px move does not (AT-7, AT-8).
- [ ] The sheet shows the handle and every row at one height, and "Past weeks" pushes the rows down (AT-9 to AT-11).
- [ ] The dim follows the drag, a tap on it closes the sheet, the X sits in the place of the menu icon, and the band stays on top (AT-12 to AT-15).
- [ ] The rows, the check, the week row, and the chips match AT-16 to AT-19.
- [ ] The sheet fades under reduced motion (AT-20).
- [ ] The focus, Escape, the accessibility tree, and the names match AT-21 to AT-26.
- [ ] The desktop shows the pill bar, and no menu button shows with scripts off (AT-27, AT-28).
- [ ] A dock page loads no more code than on `main`, and the first tap on the front door loads no new script (AT-29, AT-30).
- [ ] The sheet keeps the look of `cpc` and of `norcal` (AT-31).
- [ ] The menu sheet holds no hand-built drag code (AT-35).
- [ ] The other four sheets, the dock, the pill bar, and the CI workflows do not change (AT-38, AT-39).
- [ ] The top band tests check the open, the rows, the X, the focus, and each close, and a Tab keeps the focus in the sheet.
- [ ] `make check-fast` passes at the root.
