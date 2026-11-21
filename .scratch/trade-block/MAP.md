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

## NOT YET SPECIFIED

- What is the look and the place of the Trade block picker in the Find hero? `decisions/01-prototype-block-picker-look.md`.
- Which players does the picker list? `decisions/02-spec-players-the-picker-lists.md`.
- How do the cards spread across the block players, and what does the Advisor pick get told about the block? `decisions/03-spec-card-spread-and-pick.md`.
- How long does the block live? `decisions/04-spec-block-lifetime.md`.

## OUT OF SCOPE

- Players of other rosters in the block. The analyzer grades a trade for a known target.
- A Trade block of more than one player in the front door chat. A later spec can add it.
- Three-team trades. Brian scrapped them in deadline-week decision 11.
