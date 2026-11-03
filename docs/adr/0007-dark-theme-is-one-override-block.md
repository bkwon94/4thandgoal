# The dark theme is one override block that lifts the black card

The brand is a black card on a white page, and the site paints it with one set of color tokens. The site now offers a dark theme next to the light one, and the reader switches with the theme button. The dark theme is one `.dark` block on `<html>` that re-points the light tokens to dark partners, so the components keep their classes. The page goes black, the black card lifts one step to grey so it keeps its edge, and the masthead and the compact bar stay black and sit flush with the page. We chose this over a second full palette because one block is one place to read and to check. We chose the lifted card over a flush black card because a flush card loses its edge.

## Consequences

- Light is the default, because the light theme is the report look of ADR 0001. The export ships no theme class. A stored choice is the only way to the dark theme; the site does not follow the system setting.
- Red never re-points, because white text sits on red fills. Red text on the page uses `red-ink`, which is red in light and light red in dark, since brand red on black is 3.1 to 1 and fails for text.
- The black card paints with `card-blk`, not `blk`, so the card can lift while the masthead stays black.
- Images from the pipeline keep their own matte in both themes. A matte mismatch is a pipeline fix.
- The switch has no transition, so no surface shows a mid-color.
