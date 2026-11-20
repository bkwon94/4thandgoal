# 04: The element rule fails a raw button or dialog

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-1, AT-2, AT-12, and AT-14.

**App:** site

**What to build:** A plugin rule fails a JSX `<button>` or `<dialog>` in site code outside the `ui` folder. Test files are exempt. The message names the rule, the line, and the wrapper of `ui` to use. Each of the 8 files that has a raw `<button>` now uses a wrapper of `ui`, with the same look and behavior.

**Blocked by:** 01

**Status:** in-review

- [x] A fixture with a raw `<button>` fails, and the message names the rule, the line, and the wrapper.
- [x] A fixture with a raw `<dialog>` fails with the rule and the line.
- [x] No raw `<button>` remains in site code outside `ui` and outside test files.
- [ ] A commit that adds a raw `<button>` to a site file fails the hook and does not land.
- [x] The lint of all site code exits 0.
