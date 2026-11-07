# 09: One even row of slots

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-34, AT-37, and AT-51.

**App:** site

**What to build:** The slot row of ticket 08 is still uneven on a phone. On the end card at 340 px the row overflows the padding of the card. The empty dashed slots touch, so two dashed borders read as one doubled line. The filled tile is wider than the empty slots. Each tile of the row must have the same width, with a visible gap, inside the padding of its card at 340 px and 390 px.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Each tile of a slot row has the same width, the filled tile too.
- [ ] A visible gap sits between two tiles.
- [ ] The row stays inside the padding of the end card and of each word card of the claim sheet at 340 px and 390 px.
