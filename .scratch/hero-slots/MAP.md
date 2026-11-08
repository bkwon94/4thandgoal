# Hero slots: map

App: site.
Spec branch: `hero-slots`.

## DESTINATION

Every hero on the site has the same structure and the same type on a phone. `Hero` takes six fixed hero slots, each with one style, and the first hero of a page draws a hero scene of its own data that a reader taps or slides to read.

## DECISIONS SO FAR

- The goal: the heroes read as one family on a phone, and the hero art is a bold, ambitious change that a phone shows. Brian, 2026-11-07.
- One spec, site only. The tickets of the slots come first and the tickets of the scene come last, so the scene can leave the spec and the slots still ship. Brian, 2026-11-07.
- The layout and the type come from the Tide template of Scrolltide. The idea of the scene comes from the Astera template of Scrolltide. We adapt the method and write our own code. The raw prompts are paid source and never enter the repo. Brian, 2026-11-07.
- `Hero` takes six hero slots in a fixed order: `eyebrow`, `title`, `meta`, `feature`, `stats`, `action`. Only `title` is required. `Hero` takes no `children`. Brian, 2026-11-07.
- `feature` holds the one part that is unique to a page, such as the team rows, the avatar with its grade, or the fairness block. `action` holds the links, the buttons, and the share bar. Brian, 2026-11-07.
- The `title` has one style on every hero: `text-headline`, Space Grotesk 300, `tracking-tight`. A prop sets the heading level. The big "404" moves to `feature`, and the title of the 404 reads "Page not found". Brian, 2026-11-07.
- One faded hairline in the `rule-dark` color sits above `stats`, from the `tablet` tier up only. Brian, 2026-11-07.
- A phone shows one column in the slot order. From the `tablet` tier up, the hero takes the two-row split of Tide. `meta` stays one or two lines at 16px, the week chips of the manager move to `feature`, the title of the Matchup is words, and an empty slot takes no space. `decisions/01-prototype-slot-layout.md`.
- The art of the first hero of a page is a hero scene: lights drift in for about 1.9 s and settle into a star chart of real data. A tap selects the nearest light, a slide scrubs, one label shows at rest, a hint shows once, and the scene replays on re-entry. The label must not cover the margin text. `decisions/06-prototype-hero-scene.md`.
- The scene replaces the scan line and the bend of Mesh Flow. `decisions/02-prototype-mesh-tune.md` closes as replaced.
- ADR 0027 lets the canvas of the hero scene redraw on entry and on re-entry. It supersedes the scan line and the rule of transform and opacity only of ADR 0024 for that canvas alone. `docs/adr/0027-the-hero-scene-settles-on-a-canvas.md`.
- The terms Hero slot and Hero scene go into `GLOSSARY.md`, and the term Hero names its slots. Brian, 2026-11-07.

## NOT YET SPECIFIED

- How does the canvas get plain RGB numbers for the brand colors of each client? `decisions/03-research-canvas-brand-color.md`.
- Does the blurb of the Matchup of the Week move under the hero, or fold behind "Read more"? `decisions/05-spec-matchup-blurb.md`.
- Which other heroes get a scene, and what does each scene show? `decisions/07-spec-scene-per-hero.md`.
- The handoff to the spec. `decisions/04-spec-handoff.md`.

## OUT OF SCOPE

- A canvas on any surface other than the first hero of a page. ADR 0027 allows the hero scene only. Another surface needs its own ADR.
- A change to the content of a hero, such as a new number or new copy. The spec moves the content that exists into the slots, and the scene draws data that is already published.
- Motion from the tilt of the phone. iOS asks for a permission first, and a prompt on a stats page is a bad trade.
- A new font weight under 300. Tide sets 250, but Space Grotesk starts at 300.
- Three.js or WebGL. A few lights need no 3D engine.
