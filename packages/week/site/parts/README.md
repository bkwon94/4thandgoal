# packages/week/site/parts: the parts of the league that the week chapters share

## Knows

- The chapter frame of the week page in the look, in `week-chapter.tsx`: a region named by its heading, with a mono note.
- The share bar of a game, in `share-bar.tsx`, and the share of the lead side.
- The headshot of a player for the round photo frame, or none, in `photo.ts`. The frame then shows the initials.
- The data of the Matchup scene of the hero, in `matchup-scene.ts`: 12 lights from low to high, the league median,
  and the two teams of the Matchup as the flare with the margin mark.

## Ports

None.

## Does not do

- It holds no part with no league term. The design package holds those, such as the hero, the card, and the photo frame.
- It builds no manager href. `@cpc/league/hrefs` holds the builders, because the week and the managers both link a manager page.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
