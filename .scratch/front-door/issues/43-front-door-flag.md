# 43: A flag per client keeps the old home page until the commissioner turns the front door on

Spec: `.scratch/front-door/PRD.md`. Source: H30 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** `client.toml` of each client gets `front_door = true | false`. Both clients merge with `false`.

- With `false`, `/` is the old home page of `main` (`apps/site/src/app/page.tsx` and `home-chapter` on `origin/main`), and the `[menu]` holds the items of `main`, including Midseason Report and Trade Analyzer. The front door is live at the hidden route `/ask/`: no menu item and no link reach it, and its page has `noindex`.
- With `true`, `/` is the front door, and the menu is the 4 items of the spec. `/ask/` serves nothing (404), since the front door is at `/`.

The flag is read at build time, through the generated client values, like the other client keys.

**Blocked by:** none

**Status:** done

- [x] `front_door = false` builds the home page and the menu of `main`, and the front door at `/ask/`, with `noindex`.
- [x] `front_door = true` builds the front door at `/` and the 4-item menu, and no `/ask/` page.
- [x] Both clients have `front_door = false`.
- [x] `check:export` and `check:floor` pass for both clients.

## Notes

- The two menus: `[menu] items` stays the menu of main, and `[menu] front_door_items` holds the 4 items. With the flag on, the build takes `front_door_items`. NorCal has no `items`, so its menu off is Home, then the package list, as on main.
- The front door page is `src/app/front-door/door-page.tsx`. `/` picks it or the Front page (`src/app/front-page.tsx`) by `clientValues.frontDoor`. The client build writes `(client)/ask/page.tsx` only with the flag off.
- `check:export` checks the flag: off, `out/ask/index.html` has noindex and no page links to it; on, the export has no `/ask/` page.
- The evidence steps of AT-1 and AT-50 open `/`. With the flag off, the front door is at `/ask/`.

## Comments
- Closes with the squash merge of the spec PR.
