# packages/eggs/site/hunt: the find card, the claim sheet, and the claim ticket

## Knows

- The egg hunt of a page in `egg-hunt.tsx`: it mounts the listener once the board names a drop, and opens the find card after a match, or the limit card on a 429 of the check.
- The find in `find-card.tsx`, in the look of ADR 0024: the blur, the ring, the egg that bobs, the crack, and the red letter tile.
- The shape of the crack in `crack.ts`: the tap point, the six lines that spread from it, the shards, and the zigzag of the halves. A fresh seed on each tap gives a new crack. A tap by the keyboard cracks from the middle of the egg.
- The art in `egg-art.tsx`: the egg, and the row of letter tiles of an egg word. The slots of each tile in `slots.ts`.
- The claim sheet in `claim-sheet.tsx`: the team pills, a card per egg word with its gift card, count, tiles, leader, and ghost tile, the block notice, and the passphrase field only when the browser has none.
- The claim ticket in `claim-ticket.tsx` at the foot of the sheet: the letter tile, the egg word or the block, the team, and the stub. The locked stub names the next step that is missing. A tap, Enter, or Space tears the stub and sends the claim. A claim stamps CLAIMED and another manager first stamps TAKEN, each before the end card. A wrong passphrase brings the stub back.
- The hero card at the end of each path in `end-card.tsx`: the claim, the block, another manager first, and the limit.
- Reduced motion shows each part at rest. The find then shows the tile at once, with no crack. The keyframes live in `apps/site/src/app/globals.css`.

## Ports

- `EggsApi` of `../lib/api.ts`. The app gives the real client, and a test gives the one fake.

## Does not do

- It shows no pill for the commissioner, because the board lists only the managers who hunt.
- It names no page and no spot.
