# eggs: the egg hunt across the site of a client

## Knows

- The package values in `values.py` (`cpc-eggs`, imported as `eggs`), under `[values.eggs]`: `words`, the egg words and the gift card of each, `first_week` and `last_week` of the hunt, `drop_size`, the count of each egg drop, and `commissioner`, the roster id of the commissioner. The defaults are CORNERSTONE $50, LANSDALE $30, EAGLES $20, weeks 9 to 17, 6 eggs, and no commissioner.
- The store in `store.py`: one SQLite file per client with the tables `eggs` and `claims`. The first claim of an egg wins, and an undo keeps the row with its undo time.
- The letter rule of the drop in `letters.py`: per egg, the letter that the most managers still need over the open egg words, with no repeat in one drop and the guard of the last letter of each leader.
- The egg file of the commissioner in `eggfile.py`, at `~/cpc-eggs/<season>.toml` outside the repo, and the egg draft in `draft.py` with the agent prompt `draft_prompt.md`.
- The check matcher in `conditions.py`: each condition of an egg must hold in the state that the listener sends. A list in the state, such as the open states, holds each value that the egg wants. The trail of a tap combo must match in order. The clock window, such as `"23:00-00:00"`, and the weekday, such as `"thu"`, hold on the clock of the client, in the timezone of the client.
- The one-time claim tokens in `tokens.py`, each good for 15 minutes, and the limit of the egg check in `tunables.py`: 60 checks per hour of each address, apart from the limit of the other routes.
- The eggs routes of the API in `routes.py`: `check` and `board` are open, `check` has its own group `check_router` for its own limit, `claim` needs the passphrase, and `drop` and `undo` need the commissioner key. The board holds no page and no spot. It names the week, the count, and the time of the last drop for the egg banner.
- The site part in `site/`: the listener, the find card, the claim sheet, the egg board, the egg button, the egg banner, and the client of the eggs routes.

## Ports

- `Propose` in `draft.py`: the agent of the egg draft. The pipeline gives one headless run of the `claude` CLI.
- `Rosters` in `routes.py`: the team name of each roster. The API app gives the live rosters of the client.
- `EggsApi` in `site/lib/api.ts`: the eggs routes for the site parts. A test gives the one fake of `site/lib/fixtures/eggs-api.ts`.

## Does not do

- It imports no app and no other core package, only `league`.
- It mounts no route and reads no client folder. The API app mounts the routes at `/clients/<slug>/eggs/` and holds the guards.
- It holds no real egg spot. The spots live only in the file of the commissioner and in the API.
