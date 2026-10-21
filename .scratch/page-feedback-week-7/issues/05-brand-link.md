# 05: The brand block links home

**What to build:** A reader taps the logo or the "Cornerstone League Weekly" text in the masthead and lands on the season index. The link works on a week page and on the index page. The masthead looks the same as before.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The whole brand block in the shared shell is one link to the season index, built from the `root` the page already receives.
- [ ] On a week page the link goes up two levels to the index. On the index page the link points at the page itself.
- [ ] The link has no underline and keeps the current colors and layout.
- [ ] Tests at the render seam check the link on the week page and on the index page.
- [ ] `uv run pytest -q` passes.
