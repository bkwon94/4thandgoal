# packages/design/site/brand: the brand and the copy of a client

## Knows

- The JSON Schema of `brand.toml` and of `copy.toml`. Each brand gives the light and the dark set. A missing set, a missing
  base role, an unknown role, or an unknown key fails, so a stale `[fonts]` table or radius key fails the build.
- The eight base roles, the derived roles, and the formula of each derived role. A brand can override a derived role.
- The brand CSS: the light set in one `@theme` block, then the dark set under `.dark`. The dark class on `<html>` makes dark the default.
- The text pairs of the site and the WCAG contrast ratio of each pair in each set.

## Ports

- None. The client build reads the files and passes the values in.

## Does not do

- It reads no file, no env, and no config. `apps/site/scripts/client-build.mjs` reads `clients/$CLIENT/` and writes the CSS.
- It holds no font, radius, spacing, type, breakpoint, or tracking token. The look owns them, so `apps/site/src/app/globals.css`
  holds them, with `move-up` and `move-down` (ADR 0024).
- It holds no component. The top band takes the logo as a prop.
