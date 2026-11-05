# packages/design/site/brand: the brand and the copy of a client

## Knows

- The JSON Schema of `brand.toml` and of `copy.toml`. A missing base role, an unknown role, or an unknown key fails.
- The six base roles, the derived roles, and the formula of each derived role. A brand can override a derived role.
- The brand CSS: the first set, the fonts, and the radii in one `@theme` block, then the dark set under `.dark` for a two-set brand.
- The `@font-face` of each font file. The site serves each file at `/brand/fonts/`, so no font comes from an outside host.
- The text pairs of the site and the WCAG contrast ratio of each pair in each set.

## Ports

- None. The client build reads the files and passes the values in.

## Does not do

- It reads no file, no env, and no config. `apps/site/scripts/client-build.mjs` reads `clients/$CLIENT/` and writes the CSS.
- It holds no spacing, type, breakpoint, or tracking token. `apps/site/src/app/globals.css` holds them, with `move-up` and `move-down`.
- It holds no component. The masthead takes the logo and the theme button as props.
