# 01: The look and the place of the Trade block picker

Map: `.scratch/trade-block/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

Find mode needs a control to add up to 3 players of the asker's roster, to show them, and to remove one. Where does it sit in the Find hero, beside Your team, "Trade with", and the position chips? What does it look like on a 390 px phone, a tablet, and a desktop? It follows the design bar and uses ui-sdk through its wrapper (ADR 0037). Brian must see it on a phone before the decision, so the kind is prototype.

## Decision

Brian chose B2 · Strip, picks pinned on 2026-11-21, after two rounds on the phone. The prototype is on the branch `trade-block-01-proto` at `285f2789`, in `packages/analyzer/site/form/block-proto/`. It stays off `main` as the primary source. The worktree is removed and the preview servers are stopped.

1. **The place.** The Trade block sits under "Your team" and above "Trade with" in the Find hero. The label reads "Trade block · tap to add", with the counter "2 of 3" on the right.
2. **The strip.** One horizontal scroll row of the asker's roster: a headshot, the last name, and the position for each player. The strip edge fades, so the scroll is obvious.
3. **A pick.** A tap puts a red ring and a check on the player, and the pick moves to the front of the strip with a spring of 0.4 s and no bounce. With motion turned off, the move is instant. The picks lead in the order of the taps, so a pick never scrolls out of view.
4. **A remove.** A tap on a pick takes it off. At 3 of 3, the label reads "Trade block · tap a pick to take it off".
5. **The cap.** A tap on a 4th player adds nothing. The strip scrolls back to the picks, and the reason line reads "Your block holds 3 players. Take one off to add another."
6. **The empty block.** The line reads "No one on the block. The search can offer any of your players."
7. **The part.** The ui-sdk `ToggleGroup` with `multiple`, through the wrapper `packages/design/site/ui/toggle-group.tsx`, in a ui-sdk `ScrollArea` (ADR 0037).

Out: A (pills, which Brian called ugly), A2 (rows cost height), C and C2 (search field), and D (sentence). Round 1 was at `39ff9aad`.
