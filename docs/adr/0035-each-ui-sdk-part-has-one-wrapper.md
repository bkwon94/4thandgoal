# Each ui-sdk part has one wrapper

ui-sdk renders no styles and offers an optional default look, `web.css`. The look of ADR 0024 owns the components, so a package could not use that default look without a clash. We decided that each ui-sdk part gets one wrapper in `packages/design/site/ui/`, such as `ui/sheet.tsx`, and that no other file imports `@ui-sdk`. We chose one wrapper over a direct import in each package because one wrapper keeps the look and the version in one place. Brian decided it on 2026-11-14 (spec `ui-sdk-sheet`).

## Consequences

- Tailwind styles each part on `data-slot`, the state attributes, and the CSS variables. The site loads no `web.css`.
- `globals.css` declares `@layer ui-sdk;` above the Tailwind import, so the site styles win over any ui-sdk style.
- The `package.json` of the design package alone declares `@ui-sdk/react` and `@ui-sdk/core`, each at one exact version. The site app gets them through its workspace dependency and does not declare them.
- The rule `no-restricted-imports` of the Oxlint config `.oxlintrc.json` fails an import of `@ui-sdk` outside `packages/design/site/ui/`. The failure names the file and the line. ADR 0038 moved the rule there from a rule test.
