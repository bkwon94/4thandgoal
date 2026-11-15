# 02: The ui-sdk sheet wrapper and its rule

Spec: `.scratch/ui-sdk-sheet/PRD.md`. Acceptance tests AT-32, AT-33, AT-34, AT-36, and AT-37.

**App:** site

**What to build:** The design package declares `@ui-sdk/react` and `@ui-sdk/core` at one exact version, the newest `0.1.0` beta. The site app declares neither. The global CSS of the site declares `@layer ui-sdk;` as its first rule, above the import of Tailwind. The folder of the shadcn primitives gets one sheet wrapper of the ui-sdk `Drawer`, with the root, the trigger, the backdrop, the content, the handle, the title, and the close. Tailwind styles each part on `data-slot`, the state attributes, and the CSS variables, and no `web.css` loads. A rule test beside the component rule fails an import of `@ui-sdk` outside that folder, through the shared rule report. The README of the folder names the sheet wrapper and the rule. No page uses the wrapper yet.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] The rule test fails a throwaway import of `@ui-sdk` in a shell file, with the file and the line, and passes on the real tree (AT-33).
- [ ] A search for `@ui-sdk` in the source, outside `node_modules`, lists only files in the wrapper folder (AT-32).
- [ ] Both packages sit at one exact version in the design package, and the site app lists neither (AT-34).
- [ ] No source file imports `web.css` (AT-37).
- [ ] The README of the wrapper folder names the sheet wrapper and the rule (AT-36).
- [ ] The static build of `cpc` passes with no new warning.
- [ ] `make check-fast` passes at the root.
