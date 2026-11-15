# 01: The front door gives the menu sheet to the top band

Spec: `.scratch/ui-sdk-sheet/PRD.md`. Acceptance test AT-29.

**App:** site

**What to build:** The top band no longer imports the menu sheet. The front door gives its menu sheet to the top band, in place of `nav="sheet"`, and the top band shows it in the banner in place of the dock and the week chip. The menu sheet looks and works the same as before. The 11 dock pages load no code of the menu sheet. This ticket readies the move of ticket 03, so the cost of the `Drawer` reaches only the front door.

**Blocked by:** none

**Status:** done

- [x] The top band tests of the menu sheet pass with no change to what they check.
- [x] A dock page renders no menu button and no menu sheet, and the front door renders both, as before.
- [x] The gzip sum of the scripts of `/rankings/` on the static build of `cpc` is less than or equal to the sum on `main` (AT-29).
- [x] `make check-fast` passes at the root.

## Comments

The merge: `90562bc8` on `ui-sdk-sheet-01`, merged into `ui-sdk-sheet` on 2026-11-14.
The proof: The site suite passed 1514 of 1514, and AT-29 measured `/rankings/` at 316270 bytes gzip against 317814 on `main`.
Read at least 7 files: AGENTS.md, apps/site/AGENTS.md, .scratch/ui-sdk-sheet/PRD.md, .scratch/ui-sdk-sheet/ACCEPTANCE.md, .scratch/ui-sdk-sheet/issues/01-the-front-door-gives-the-menu-sheet-to-the-top-band.md, packages/design/site/shell/top-band.tsx, apps/site/src/app/front-door/door-page.tsx.
Closes with the squash merge of the spec PR.
