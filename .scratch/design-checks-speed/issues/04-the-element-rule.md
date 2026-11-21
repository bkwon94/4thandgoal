# 04: The element rule fails a raw button or dialog

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-1, AT-2, AT-12, and AT-14.

**App:** site

**What to build:** A plugin rule fails a JSX `<button>` or `<dialog>` in site code outside the `ui` folder. Test files are exempt. The message names the rule, the line, and the wrapper of `ui` to use. Each of the 8 files that has a raw `<button>` now uses a wrapper of `ui`, with the same look and behavior.

**Blocked by:** 01

**Status:** in-review

- [x] A fixture with a raw `<button>` fails, and the message names the rule, the line, and the wrapper.
- [x] A fixture with a raw `<dialog>` fails with the rule and the line.
- [x] No raw `<button>` remains in site code outside `ui` and outside test files.
- [x] A commit that adds a raw `<button>` to a site file fails the hook and does not land.
  - Evidence: a local probe added `<button type="button">probe</button>` to `apps/site/src/app/_routes/analyzer/home.tsx` and staged it.
  - Command: `~/plans/design-checks-speed/helpers/locked.sh git commit -m "probe"`. Exit code: 1.
  - The hook line: `make check-fast STAGED=1.....Failed`.
  - The rule line: `apps/site/src/app/_routes/analyzer/home.tsx:14:7: error design(no-raw-element): A raw <button> skips the wrapper of the ui folder. Use PendingButton from packages/design/site/ui/pending-button.tsx.`
  - `git log -1 --oneline` before and after: `c81d7c95 P3: add ticket 15 to the AT-20 count list (1,822 tests in 194 files)`. No commit landed.
  - Then `git restore --staged` and `git restore` put the file back, and `git status` was clean.
- [x] The lint of all site code exits 0.
