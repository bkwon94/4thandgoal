# 04: Design pass on the position leader boards

**What to build:** The five boards read well on a phone and on a wide screen. At 390px the boards stack and no row wraps or clips, even with a long fantasy team name such as "Amon-Ra Dawg Your Team". At a wider width the boards sit in a grid. The look follows the existing tokens and the rest of the page.

**Blocked by:** 03 (Position leaders, end to end)

**Status:** done

- [ ] At a 390 by 844 viewport, the five boards stack and every row holds on one line, measured with `agent-browser` on a rendered page.
- [ ] At a wide viewport the boards sit in a grid.
- [ ] A long fantasy team name truncates or wraps inside its own cell and never pushes the points off the row.
- [ ] The design pass uses the `emil-design-eng` and `apple-design` skills and the existing style tokens. No new color or font tokens.
- [ ] Screenshots at 390px and at a wide width are saved for Brian's review.
- [ ] `uv run pytest -q` passes.
