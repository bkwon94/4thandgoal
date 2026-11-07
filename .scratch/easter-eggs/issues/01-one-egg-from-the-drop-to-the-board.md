# 01: One egg from the drop to the board

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-1, AT-2, AT-5, AT-8, AT-14, AT-18, AT-24, AT-26, and AT-51.

**App:** both

**What to build:** One test egg goes live, and a manager finds it with a 3-tap, claims its letter, and sees the claim on a plain egg board. The new `eggs` package holds the store, the routes of the API, and the site part. Only the CPC client takes it. The API keeps the eggs and the claims in one SQLite file on the Fly volume. The look stays plain: ticket 05 and ticket 06 build the look of the site.

**Blocked by:** None. It can start now.

**Status:** ready-for-agent

- [x] The package `eggs` has a Python part, a site part, and a README with the headings Knows, Ports, and Does not do. Only `clients/cpc/client.toml` lists it.
- [x] The API makes one SQLite file for each client on the volume at `/data`, with the tables `eggs` and `claims` of the spec. The `egg_id` of `claims` is unique.
- [x] The API serves `check`, `claim`, `board`, `drop`, and `undo` under the slug of the client. `check` and `board` need no key, `claim` needs the passphrase, and `drop` and `undo` need the commissioner key.
- [x] The commissioner key is a setting of the API. The start of the API fails for a client of the package with no key. Brian sets the Fly secret, with the exact command from the agent.
- [x] The listener of the site sends one check on a multi-tap, with the page, the stable id, the action, and the theme. A match opens a plain find card and a plain claim sheet. `/eggs/` lists each manager in each egg word.
- [x] The NorCal build has no listener, no egg button, and no `/eggs/` route.
- [x] The API tests run the routes through the FastAPI test client with a temp SQLite file. One Playwright run finds, claims, and sees the claim on the board.
