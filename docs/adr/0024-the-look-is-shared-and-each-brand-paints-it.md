# The look is shared, each brand paints it, and dark is the default

The site kept the look of the printed report: Helvetica, a black masthead, white pages, and grey cards (ADR 0006). The site now has one shared look for every client. The look owns the fonts, the radii, the layout, the components, and the motion. Each brand keeps only its color roles, its logo, and its copy, and paints the look with its colors. Dark is the default for every client, and every client keeps a light option with the theme button. We chose a new look over the report look because the goal is a first reaction of "wow" and "so easy to read", and the report look reads as print. We chose one shared look over a look per client because a client on Helvetica loses the feel, and one look is one thing to build and to check.

## Consequences

- The look uses Space Grotesk for text and JetBrains Mono for numbers and labels, self-hosted (decision 02 of `site-redesign`).
- `brand.toml` holds the `light` and the `dark` sets only, and both are required. The fonts and the radii of the look live in `apps/site/src/app/globals.css` (decision 01 of `site-redesign`).
- A brand that wants its own font or radius gets no override. A new client gets the look as it is.
- The hero surface carries the grid texture, the corner brackets, the brand glow, and a scan line on entry. Other surfaces stay plain, so the hero stays the one loud part of a page.
- The hero stays dark in both themes. It sits on the `band` color of the brand, so the light theme has a light page and a dark hero, and the site has one hero (decision 09 of `site-redesign`).
- Motion keeps the rule of the site: transform and opacity only, a strong ease-out, and none under reduced motion.
- ADR 0006 is superseded. The rule "light is the default" of ADR 0007 is superseded. The `.dark` override of ADR 0007 stays. The build puts the `dark` class on `<html>` for every client, and the boot script removes it for a stored light choice. So a reader with scripts off gets dark, and every `dark:` variant stays (decision 12 of `site-redesign`). We chose this over a `.light` override because the inversion changes every `dark:` variant of the components, for no gain to the reader.
