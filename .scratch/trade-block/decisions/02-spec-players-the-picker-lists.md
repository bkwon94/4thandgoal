# 02: Which players the picker lists

Map: `.scratch/trade-block/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

The Finder never puts a handcuff, a player out with no return week, or an unlisted player (a kicker or a defense) in a trade. The lean is that the picker lists only the players that can be in a trade, so the manager cannot pick a player who gives an empty list for that reason. The spec records the list and its order.

## Decision

The strip lists the QB, RB, WR, and TE of the asker's roster, in that order, then by name. It never lists a kicker or a defense. It does not hide a handcuff or a player out with no return week, because `/teams` reads only the roster snapshot; the search drops such a player with no error. Recorded in `PRD.md`, which Brian approved on 2026-11-21.
