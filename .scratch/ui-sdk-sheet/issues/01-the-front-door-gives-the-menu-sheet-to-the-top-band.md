# 01: The front door gives the menu sheet to the top band

Spec: `.scratch/ui-sdk-sheet/PRD.md`. Acceptance test AT-29.

**App:** site

**What to build:** The top band no longer imports the menu sheet. The front door gives its menu sheet to the top band, in place of `nav="sheet"`, and the top band shows it in the banner in place of the dock and the week chip. The menu sheet looks and works the same as before. The 11 dock pages load no code of the menu sheet. This ticket readies the move of ticket 03, so the cost of the `Drawer` reaches only the front door.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] The top band tests of the menu sheet pass with no change to what they check.
- [ ] A dock page renders no menu button and no menu sheet, and the front door renders both, as before.
- [ ] The gzip sum of the scripts of `/rankings/` on the static build of `cpc` is less than or equal to the sum on `main` (AT-29).
- [ ] `make check-fast` passes at the root.
