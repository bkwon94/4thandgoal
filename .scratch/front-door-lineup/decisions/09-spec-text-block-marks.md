# 09: Which marks of markdown does the text block allow?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

The text block is the default for the text of every Answer. Today the text renders as plain paragraphs (`apps/site/src/app/front-door/answer-card.tsx:80`). The spec sets the allowed marks, the renderer, and the strip of the marks before the Jev check.

The proposal: allow bold, italic, bullet lists, numbered lists, and paragraphs. Block links, images, headings, raw HTML, and markdown tables. A table has its own block. A link or an image from Claude is a risk on a public site. A heading competes with the title of the card. Code strips the marks before the check, so Jev reads the same plain sentences.

## Decision

Brian approved the spec on 2026-11-12. The spec records the choice under "The text block (decision ticket 09)" in `PRD.md`: bold, italic, bullet lists, numbered lists, and paragraphs. A blocked mark shows as plain text.
