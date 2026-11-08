# Hero slots: map

App: site.
Spec branch: `hero-slots`.

## DESTINATION

Every hero on the site has the same structure and the same type on a phone. `Hero` takes six fixed hero slots, each with one style, and the first hero of a page gets a grid that bends on entry and on a tap.

## DECISIONS SO FAR

- The goal: the heroes read as one family on a phone. The hero art gets one moment of motion that a phone shows. Brian, 2026-11-07.
- One spec, site only. The tickets of the slots come first and the tickets of the mesh come last, so the mesh can leave the spec and the slots still ship. Brian, 2026-11-07.
- The layout and the type come from the Tide template of Scrolltide. The motion of the grid comes from the Mesh Flow component of Scrolltide. We adapt the method and write our own code. The raw prompts are paid source and never enter the repo. Brian, 2026-11-07.
- `Hero` takes six hero slots in a fixed order: `eyebrow`, `title`, `meta`, `feature`, `stats`, `action`. Only `title` is required. `Hero` takes no `children`. Brian, 2026-11-07.
- `feature` holds the one part that is unique to a page, such as the team rows, the avatar with its grade, or the fairness block. `action` holds the links, the buttons, and the share bar. Brian, 2026-11-07.
- The `title` has one style on every hero: `text-headline`, Space Grotesk 300, `tracking-tight`. A prop sets the heading level. The big "404" moves to `feature`, and the title of the 404 reads "Page not found". Brian, 2026-11-07.
- One faded hairline in the `rule-dark` color sits above `stats`, from the `tablet` tier up only. Brian, 2026-11-07.
- A `mesh` prop turns the bent grid on. The page sets it on its first hero only. Power rankings on the home page, each act title, and the analyzer result keep the static grid. Brian, 2026-11-07.
- The grid bends once toward the center of the brand glow when the hero enters the view, for about 1.5 s. A tap bends it toward the tap point for about 0.6 s. A fine pointer bends it on desktop. The loop stops at rest. Brian, 2026-11-07.
- At the peak of the bend, the grid takes the grid color, made brighter toward `on-dark-muted`. Brian, 2026-11-07.
- The pull on entry replaces the scan line. On the analyzer form, the loading `Sweep` runs alone, with no tap pulse. Brian, 2026-11-07.
- ADR 0027 lets the canvas of the hero redraw on entry and on a tap. It supersedes the scan line and the rule of transform and opacity only of ADR 0024 for that canvas alone. `docs/adr/0027-the-hero-grid-bends-on-a-canvas.md`.
- The term Hero slot goes into `GLOSSARY.md`, and the term Hero names its slots. Brian, 2026-11-07.
- A phone shows one column in the slot order. From the `tablet` tier up, the hero takes the two-row split of Tide. `meta` stays one or two lines at 16px, the week chips of the manager move to `feature`, the title of the Matchup is words, and an empty slot takes no space. `decisions/01-prototype-slot-layout.md`.

## NOT YET SPECIFIED

- Does the blurb of the Matchup of the Week move under the hero, or fold behind "Read more"? `decisions/05-spec-matchup-blurb.md`.
- What values of reach, depth, and peak alpha look right on a phone, and does the canvas grid line up with the CSS grid? `decisions/02-prototype-mesh-tune.md`.
- How does the canvas get plain RGB numbers for the grid color and the glow center of each client? `decisions/03-research-canvas-brand-color.md`.
- The handoff to the spec. `decisions/04-spec-handoff.md`.

## OUT OF SCOPE

- A canvas on any surface other than the first hero of a page. ADR 0027 allows the hero grid only. Another surface needs its own ADR.
- A change to the content of a hero, such as a new number or new copy. The spec moves the content that exists into the slots.
- Motion from the tilt of the phone. iOS asks for a permission first, and a prompt on a stats page is a bad trade.
- A new font weight under 300. Tide sets 250, but Space Grotesk starts at 300.
