# The hero grid bends on a canvas

ADR 0024 gave the hero a scan line on entry, and it limited motion to transform and opacity. Most readers use a phone, and a hero has no motion that a phone shows after the scan line. So the grid of the first hero of a page now bends toward one point on a canvas: once toward the brand glow when the hero enters the view, and toward the tap point after a tap. A canvas redraws its pixels, so it is not transform or opacity. We allow it for this one canvas, because the cost is small and bounded. A phone hero has about 340 grid points, the bend runs for about 1.5 s on entry and about 0.6 s after a tap, and then the loop stops. We chose this over one DOM node for each point moved by `transform`, because about 340 moving nodes cost more than one canvas and the code is harder to read. We chose it over no motion, because the look aims at a first reaction of "wow" (ADR 0024). Brian decided this in the grill of `hero-slots` on 2026-11-07.

## Consequences

- The pull on entry replaces the scan line. The hero keeps the grid texture, the brand glow, and the corner brackets.
- Only the hero that the page marks with the `mesh` prop gets the canvas. Every other hero keeps the static CSS grid.
- Under reduced motion the canvas does not run, and the static CSS grid shows.
- The canvas runs in a client component. `Hero` stays a server component, and the static HTML shows the CSS grid.
- All other motion of the site keeps the rule of ADR 0024: transform and opacity only, a strong ease-out, and none under reduced motion. A canvas on any other surface needs its own ADR.
- The method comes from the Mesh Flow component of Scrolltide. We wrote our own code, and the source of the template is not in the repo.
- This ADR supersedes two lines of the Consequences of ADR 0024 for the hero canvas only: "a scan line on entry" and "transform and opacity only".
