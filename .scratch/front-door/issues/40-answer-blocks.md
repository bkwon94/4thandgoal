# 40: A free answer can show a list, a table, or a player card

Spec: `.scratch/front-door/PRD.md`. Source: H27 of `.scratch/front-door/HANDS-ON.md`.

**App:** API and site

**What to build:** a free answer can only return text, so "order my players by performance" reads as one long paragraph. Claude now can return one block from a small catalog, through a typed display tool, after a short lead sentence. Plain text stays the default.

- **list:** a ranked list. Each row has a rank, a player or team, a small tag (position or team), a value, and an optional short note.
- **table:** at most 4 columns and 12 rows, for a comparison.
- **player card:** one player: name, position, NFL team, fantasy team, status (can play now or not), up to 4 stats, and a short note.

The block args are a Pydantic discriminated union, so a bad block fails validation, not the page. The API streams the block as a `data-block` part. The Jev check reads each row of the block like a sentence, against the tool results; a block that fails gets the rewrite, like text. The site switches on `kind` and renders the component, in the style of the data block rows, with the same reveal. The chat turn of the Answer carries the block as short text.

**Blocked by:** none

**Status:** in-progress

- [ ] "order my players by performance" for Bo Girds gives a lead sentence and a list.
- [ ] "compare Bo Girds and Teehee" gives a table.
- [ ] "how is Lamar Jackson doing" gives a player card that says he cannot play now.
- [ ] "who won week 1" still gives text.
- [ ] A row that the tool results do not hold fails the check.
- [ ] Each component renders at 390 px with no horizontal scroll.
