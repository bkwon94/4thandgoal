# waiver: the waiver board, its price, its research, and the War chest page

## Knows

- The waiver board: the pool, the buckets, the board scores, the drops, and the budget table (`cpc-waiver`, imported as `waiver`).
- The price of each player, the last like him, and the outbid counts, from the bid history of the season.
- The research step and its rule prompt `prompts/research.md`, read with `load_prompt` of the facts package.
- The rank score, its own `tunables`, and the waiver file `waiver.json` with its schema version.
- The War chest page of the site (`@cpc/waiver`): the schema and the types of `waiver.json`, the budget ring, the drift field, the player sheet, and the team pick in local storage.

## Ports

- `SearchCall` in `research.py`: the one web search call. The build passes the real Claude call, and a test passes a fake.
- `TeamPicker` of `@cpc/waiver/war-chest`: the list of teams that the War chest shows with no pick. The app route passes it.
- The War chest takes the teams and the avatars of the week as props. Their types say only the keys that the page reads.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks the Python.
- It calls no loader and reads no file on the site. The route of the app reads `waiver.json` and passes the board.
- It writes no blurb. The research claims go into the board, and the site renders them as given.
