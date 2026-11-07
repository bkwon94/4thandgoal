# 08: What the claim form looks and feels like

Map: `.scratch/easter-eggs/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

When a manager finds an egg, the egg plays an animation and a claim form opens. The form asks for the manager and the egg word for the letter. It shows the status of that manager in each egg word, so the choice is clear. It says plainly when the letter fits no egg word. Brian wants it to feel great, so he must see it before the decision.

Brian set the design tool on 2026-11-06: Claude Design, the Design artifact type built into Claude, makes the design of the claim form, the egg, the animations, and the egg board.

## Decision

Brian approved the design on 2026-11-06, after two rounds in Claude Design. The canvas is https://claude.ai/artifact/2pe6Z3X2vAiTVAfEwbHSJF, with three artboards: the egg and the claim form, the egg banner, and the egg board. The spec builds from the canvas.

The look is the look of the site, not a new one:

- The dark theme is the default. Each big moment uses the hero: the 24px grid, the red glow, the four corner brackets, and one scan line.
- The labels are red uppercase at 10px with 0.16em spacing. The numbers use JetBrains Mono. The motion uses the rise curve and the 0.98 tap scale of `motion.ts`.
- The letter tiles take the colors of the logo: a claimed letter is a white square, and the new letter is the red square.

The flow of a find:

1. The page blurs, and a red ring ripples out from the spot. A hero card rises in, and its brackets close in.
2. The egg is black with the grid inside and the CPC house on it. It bobs and wobbles.
3. A tap draws a red zigzag crack. The halves fly apart, and a big red letter tile springs up with a burst.
4. "Claim N" opens a sheet. Step 1 picks the team from pills. Bo Girds is not in the list, because the commissioner cannot hunt.
5. Step 2 shows a card for each egg word: its gift card value, its count, its tiles, and its leader. A ghost tile pulses where the letter lands. A word with no open slot for the letter is faded and disabled.
6. If the letter fits no egg word, a dashed notice offers a block. The passphrase field shows only if the browser has none. The button label names what is still missing.
7. A claim opens a second hero card. The count rises, and the red tile drops into its slot. A full word says the gift card is the manager's.

Each other end has its own hero card: another manager claimed first, the claim was a block, or the limit of the egg check hit.

Copy rules from Brian:

- Write "manager" or "another manager", never "rival".
- Never name Brian on the site. Write "the commissioner".

