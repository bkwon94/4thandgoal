# 02: What does each Open card show closed and open?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** done

## Question

The Open card serves GameCard, LadderCard, ManagerCard, AwardTile, and TradeCard. Each card needs a closed line and an open panel with chips and a short text. Start with GameCard and LadderCard, because they hold the duplicated accordion. Brian must see the cards at 390px in both themes before the spec fixes the content of each one.

## Decision

Brian chose after a prototype on the live week 8 page and `/rankings/` at 390px, on 2026-11-07. Three variants ran per card: A Showcase (full shell, a plain raised panel as the media), B Card native (the closed card of now plus the Showcase drawer), and C Compact line (one dense row closed).

1. One Open card part serves both cards: the shell, the chevron toggle, and the Showcase drawer with the overview line, the chips, the rule line, and the text. Only the head of the card differs.
2. GameCard takes B. The closed card keeps both teams, both avatars, and the share bar. A was too tall (about 1.5 games per screen) and blew up 80px avatars until they looked soft. C cut the loser and the avatars, and it truncated the names.
3. LadderCard takes A. The rank number is large in the plain media panel, with the team, the record, the move, the odds bar, and the playoff chip under it.
4. The GameCard chips are three: the best player of the winner, the best player of the loser, and both records. Margin goes, because the scores and the share bar show it. Vs projection goes, because the Game Changer owns it.
5. "Winner top" and "Loser top" are unclear (Brian). The first try for the spec: each chip starts with the small avatar of its team, then "Best", the player, and the points. The spec fixes the words.
6. The LadderCard chips stay: Stand, Form, Sched, Pts, Move, Bye, and Seed. The overview line is the rank, the record, and the move. The text is the blurb.
7. The "Manager page" pill keeps a solid fill under its label, because text on the frosted blur fails the axe floor.

ManagerCard, AwardTile, and TradeCard use the same part. The spec sets their head and chips from this pattern, with no new prototype.

The prototype code is deleted. It was never committed.
