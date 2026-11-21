# Trade block: map

App: both. The site, the API, and the analyzer package that the API imports. The weekly pipeline does not change.
Spec branch: `trade-block`.

## DESTINATION

One spec adds the Trade block to Find mode of the analyzer. The manager adds up to 3 players of their own roster, and each Finder trade sends at least one of them, so a manager with players to move gets ideas built around those players.

## DECISIONS SO FAR

- The picks come only from the asker's own roster. A trade for a player of another roster is the job of the analyzer. Brian, in the Stage 1 grill.
- Each trade sends at least one block player, not every block player. Brian, in the Stage 1 grill.
- The term is Trade block. The page never says "anchor". `GLOSSARY.md`. Brian, in the Stage 1 grill.
- The Trade block, "Trade with", and the position chips combine. Each one is a hard rule, and the empty list is a real answer. Brian, in the Stage 1 grill.
- The Trade block holds at most 3 players. Brian, in the Stage 1 grill.
- The "gives" ask of the front door chat becomes a Trade block of one player. The "gets" ask stays as it is now. Brian, in the Stage 1 grill.
- The picker is a roster strip of headshots under "Your team". A pick gets a ring and moves to the front, and a tap takes it off. `decisions/01-prototype-block-picker-look.md`.
- The picker lists QB, RB, WR, and TE only. The search drops a handcuff or a player out with no return week. `decisions/02-spec-players-the-picker-lists.md`.
- `varied` puts the best offer of each block player first, and the pick sends each block player that has a fair offer. The field is `trade_block`. `decisions/03-spec-card-spread-and-pick.md`.
- The block is page state only. A team change clears it, and a partner or chip change keeps it. `decisions/04-spec-block-lifetime.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- Players of other rosters in the block. The analyzer grades a trade for a known target.
- A Trade block of more than one player in the front door chat. A later spec can add it.
- Three-team trades. Brian scrapped them in deadline-week decision 11.
