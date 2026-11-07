# eggs: the egg hunt across the site of a client

## Knows

- The package values in `values.py` (`cpc-eggs`, imported as `eggs`), under `[values.eggs]`: `words`, the egg words and the gift card of each, `first_week` and `last_week` of the hunt, `drop_size`, the count of each egg drop, and `commissioner`, the roster id of the commissioner. The defaults are CORNERSTONE $50, LANSDALE $30, EAGLES $20, weeks 9 to 17, 6 eggs, and no commissioner.
- The store in `store.py`: one SQLite file per client with the tables `eggs` and `claims`. The first claim of an egg wins, and an undo keeps the row with its undo time.
- The one-time claim tokens in `tokens.py`, each good for 15 minutes.
- The eggs routes of the API in `routes.py`: `check` and `board` are open, `claim` needs the passphrase, and `drop` and `undo` need the commissioner key. The board holds no page and no spot.
- The site part in `site/`: the listener, the find card, the claim sheet, the egg board, and the client of the eggs routes.

## Ports

- `Rosters` in `routes.py`: the team name of each roster. The API app gives the live rosters of the client.
- `EggsApi` in `site/lib/api.ts`: the eggs routes for the site parts. A test gives the one fake of `site/lib/fixtures/eggs-api.ts`.

## Does not do

- It imports no app and no other core package, only `league`.
- It mounts no route and reads no client folder. The API app mounts the routes at `/clients/<slug>/eggs/` and holds the guards.
- It holds no real egg spot. The spots live only in the file of the commissioner and in the API.
