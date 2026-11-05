# Site redesign: map

App: site.
Spec branch: `site-redesign`.

## DESTINATION

Every route of the site, in both clients, shows the look: dark by default, with a light option, each client in its own brand colors. It ships as one spec and one PR.

## DECISIONS SO FAR

- The scope is every route of `apps/site`: home, week, analyzer, managers, rankings, waiver, and 404, in both clients. Brian, 2026-11-05.
- The goal: the first reaction of a manager is "wow, this looks incredible" and "this is so easy to use and to read". Brian, 2026-11-05.
- The direction is board A, Night Broadcast, with the futuristic structure of board C, Telemetry: the grid texture, the big hero number, and the tiles. No lime. The canvas is https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8. Brian, 2026-11-05.
- Each brand keeps its colors, its logo, and its copy. The look owns the fonts, the radii, the layout, the components, and the motion. Brian, 2026-11-05.
- Dark is the default for every client. Every client has a light option and the theme button. Claude picks the NorCal light set. Brian, 2026-11-05.
- The redesign is one spec and one PR, with one cutover. Brian, 2026-11-05.
- The proof is a readability floor that runs as checks, and Brian's verdict on screenshots of each route. The screenshots cover phone and desktop width, both clients, and both themes. Brian, 2026-11-05.
- During the build, Claude starts the local dev server after each route, so Brian can look at it. Brian, 2026-11-05.
- The redesign may change anything on the page: animations, navigation, order, components, type, shapes, and visual diagrams. Brian, 2026-11-05.
- The redesign uses only the data that the pipeline publishes now. Brian, 2026-11-05.
- The new term **Look** names the shared part. **Brand** keeps the colors, the logo, and the copy. Both are in `GLOSSARY.md`. Brian, 2026-11-05.
- The brand schema keeps only the required `light` and `dark` sets. The fonts and the radii of the look go into the `@theme static` block of `globals.css`. `decisions/01-research-brand-schema-drops-fonts.md`.
- The floor runs in Playwright on the static export of each client: axe for contrast, failing on `incomplete` too, and a scan for tap targets, scroll width, and text size. It runs in `build-each-client.mjs`, not in `check:fast`. `decisions/10-research-readability-floor-checks.md`.
- The site self-hosts Space Grotesk and JetBrains Mono with `next/font/local`, as two Latin variable woff2 files of 53,660 bytes in total, both under the OFL. `decisions/02-research-web-fonts-without-speed-loss.md`.
- The look is the blend of Instrument and Glass HUD: Space Grotesk and JetBrains Mono, brand surfaces, a loud hero with the grid, brackets, glow, and scan line, round photo frames, and a staggered rise. ADR 0024. `decisions/03-prototype-the-look.md`.

## NOT YET SPECIFIED

- How does a reader move across the routes? `decisions/04-prototype-the-navigation.md`.
- What does the week page show, and in what order? `decisions/05-prototype-the-week-page.md`.
- What does the analyzer look like in the look? `decisions/06-prototype-the-analyzer.md`.
- What do the managers, rankings, and waiver pages look like? `decisions/07-prototype-managers-rankings-waiver.md`.
- What do the home page and the 404 page show? `decisions/08-prototype-home-and-404.md`.
- What are the light sets of both brands in the look? `decisions/09-prototype-the-light-sets.md`.
- Where are the edges of the readability floor? `decisions/13-grill-readability-floor-edges.md`.
- How does dark become the default? `decisions/12-spec-dark-default-mechanism.md`.
- The hand-off to the spec `decisions/11-spec-hand-off.md`.

## OUT OF SCOPE

- New data from the pipeline. It touches a second app, the published schema, and a republish of every week. Each idea that needs new data goes on the list below, for a later pipeline spec.
- A test of the reaction with other managers. Brian's verdict is the proof, so the merge does not wait on other people.
- Timed tasks, such as "find your score in 5 seconds". Somebody must run each task by hand.

### Ideas that need new data

None yet.
