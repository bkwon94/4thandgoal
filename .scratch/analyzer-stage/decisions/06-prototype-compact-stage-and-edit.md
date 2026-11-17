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

## Comments

### Round 1, 2026-11-17

The prototype ran on the real `/analyze/` page with three variants. A copy is in `~/plans/analyzer-stage-prototype/stage-06-round1/`.

- `A` "Pans": the team avatar over an overlapped stack of headshots, then "+N". The labels cut the team names short at 390 px.
- `B` "Rows": one slim row per side with the full team name and the headshots on the right. It was the cleanest at 390 px.
- `C` "Beam": the sides on a beam that tips toward the favored side under a result. Its floating Edit pill covered the text of the result.

Brian: "i like it. I think overall it looks really good." He then named two redundancies, and no variant is chosen yet:

1. On the result, the side cards under the hero list the players and headshots again. On a phone, that is one long column.
2. While the reader builds the trade, the hero stage and the cards of the form both show the players.

The orchestrator proposed, and Brian agreed to prototype:

- Result: the hero is the one place that shows the players. The side cards keep only the fairness line and the reason of each side, and a long reason can fold. Other options: the hero rows act as the side tabs, or each side card starts closed.
- Idle: "the stage waits". While the reader builds, the hero shows only the teams, or nothing. The headshots go up to the stage on the tap of Grade, as one motion. Other options: the stage is the editor, which is a large change, or slim cards with no headshots.
- Edit: still open. Under the hero, it sits below the first screen on a phone. A floating pill covers content.

Round 2 must use scrolltide, transitions.dev, and ui-sdk as needed (Brian, 2026-11-17).

