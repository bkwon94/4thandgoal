# 06: How the stage stays compact, and where the trade summary and Edit go

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** open

## Question

Brian checked tickets 04 and 06 on his iPhone on 2026-11-17 and raised two problems.

1. The stage has no cap. A trade has up to 4 sides and any number of players per side, and each player gets a full chip with name and position. A big trade fills the hero and repeats the cards under it.
2. Under a result, the `FoldLine` card, with the avatars, the player names, and Edit, sits right on top of the hero. Brian finds it ugly. The stage already shows the trade, so the card repeats it.

Brian's answers so far:

- The change goes in this spec.
- The stage shows a headshot token for each player, not a full chip. Each side shows a few tokens, then a count such as "+2".
- Edit leaves the `FoldLine` card. Brian is not sure where it goes, maybe not in the hero. The prototype tries a few places.

The prototype runs on the real analyzer page, with a big trade of 3 or 4 sides and a result.

## Decision

None yet.
