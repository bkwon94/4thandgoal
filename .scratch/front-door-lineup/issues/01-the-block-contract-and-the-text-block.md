# 01: The block contract and the text block

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-36, AT-37, AT-41.

**App:** both

**What to build:** Every Answer can carry one block with a `kind`, on the API stream and in the site. The site renders the text of every Answer as the text block: bold, italic, bullet lists, numbered lists, and paragraphs. A link, an image, a heading, raw HTML, or a table in the text shows as plain text. The Jev check reads the text with the marks stripped. The `list`, `table`, and `player` kinds of the free answer still render, and a `topics.json` of version 1 still renders as today.

**Blocked by:** none

**Status:** in-review

- [x] The site block schema is one union over `kind`, and the free answer kinds `list`, `table`, and `player` still pass it.
- [x] The data part of a personal Topic carries a `kind`.
- [x] A vitest renders bold, italic, a bullet list, and a numbered list as marks (AT-36).
- [x] A vitest shows a link, an image, a heading, and raw HTML as plain text, with no such element on the page (AT-37).
- [x] A pytest shows that the Jev check gets the text with no markdown marks.
- [x] A vitest renders a version 1 `topics.json` with no `block` as today (AT-41).
