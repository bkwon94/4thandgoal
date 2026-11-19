# packages/sim/site/tile: the Sim tile of the week page

## Knows

- `simTileOf`: the lines of the Sim tile from one week sim file, one tile per team, and the league fact of the build.
- In the regular season, the tile of a team shows its playoff odds and the sentence of more wins of the build.
- In a playoff week, a team still in shows its title odds, with its game of the round, its bye, or its seed.
- A team out of the playoffs, and each team after the final, has no tile of its own. It shows the league fact: the favorite, or the champion.
- `SimTile`: one card link to the sim page with the tile, or the league fact for a visitor with no team.
- With no team and no fact, the card asks the visitor to pick a team.

## Ports

- The props of `SimTile`: the tile of Your team or null, the league fact, and the path of the sim page.

## Does not do

- It reads no storage. The app reads Your team and picks the tile.
- It reads no file. The week part of the app reads `week-NN/sim.json` at build time.
