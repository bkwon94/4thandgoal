# packages/eggs/site/hunt: the find card and the claim sheet

## Knows

- The egg hunt of a page in `egg-hunt.tsx`: it mounts the listener and opens the find card after a match.
- The plain find card, the plain claim sheet with the team pills and the egg words, and the card at the end of each path.
- The claim button names the next step that is missing.

## Ports

- `EggsApi` of `../lib/api.ts`. The app gives the real client, and a test gives the one fake.

## Does not do

- It shows no pill for the commissioner, because the board lists only the managers who hunt.
- It names no page and no spot.
