# The hero scene settles on a canvas

ADR 0024 gave the hero a scan line on entry, and it limited motion to transform and opacity. Most readers use a phone, and the goal of the look is a first reaction of "wow" (ADR 0024). So the first hero of a page now draws a scene of its own data on a canvas. Points of light start scattered, drift in, and settle into a small chart of real data, such as the 12 scores of the week or the weeks of one team. A reader taps or slides across the scene to read a light. A canvas redraws its pixels, so it is not transform or opacity. We allow it for this one canvas, because the cost is small and bounded. A scene has about 8 to 12 lights and a faint dust of under 100 points, the settle runs for about 1.9 s, and then the loop stops. We chose Canvas 2D over three.js or WebGL, because a few lights need no 3D engine and no new dependency. We chose one canvas over one DOM node for each light moved by `transform`, because the dust, the lines, and the glow are simpler to draw on one canvas. We chose a scene of real data over a bend of the grid, because it says something true about the week. Brian decided this in decision 06 of `hero-slots` on 2026-11-07, after two rounds of a prototype on his phone.

## Consequences

- The scene replaces the scan line. The hero keeps the grid texture, the brand glow, and the corner brackets.
- Only a hero that the page gives a `scene` gets the canvas. Every other hero keeps the static CSS grid.
- The scene draws data that the pipeline already publishes. It invents no number.
- The loop runs on entry and each time the hero comes back into view, and it stops at rest. A tap or a slide redraws one frame.
- Under reduced motion the settled chart draws at once.
- The canvas runs in a client component. `Hero` stays a server component.
- All other motion of the site keeps the rule of ADR 0024: transform and opacity only, a strong ease-out, and none under reduced motion. A canvas on any other surface needs its own ADR.
- The idea of a scene that settles comes from the Astera template of Scrolltide. We wrote our own code, and no source of a template is in the repo.
- This ADR supersedes two lines of the Consequences of ADR 0024 for the hero canvas only: "a scan line on entry" and "transform and opacity only".
