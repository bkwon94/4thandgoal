# 03: The readability floor check

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests AT-35.

**App:** site

**What to build:** A check proves that each page is easy to read. It runs in Playwright on the static export of each client, in the build of each client after the export check, and in CI on each PR. It checks the contrast with axe, and the text size, the tap targets, and the sideways scroll with a page scan. The list of pages for the full floor starts empty, and each page ticket adds its pages.

**Blocked by:** none

**Status:** in-review

- [x] axe with the rule `color-contrast` fails on a violation and on an `incomplete` result.
- [x] The scan fails prose under 16px, other text under 11px, a link or button under 44px, and a sideways scroll at 390px. A link inside prose is exempt, and the check prints each exempt link.
- [x] The check sets the theme with `addInitScript` on `cpc.theme` and asserts the class on `<html>`.
- [x] The check prints the count of each text tier and its time.
- [x] CI installs Chromium. The check stays out of `check:fast`.
- [x] A 14px blurb on a local branch fails the check, which names the page, the element, and the size.
- [x] A new ADR, beside ADR 0016, fixes the readability floor as a rule.
- [x] The evidence of AT-35 is recorded in `EVIDENCE.md`.
