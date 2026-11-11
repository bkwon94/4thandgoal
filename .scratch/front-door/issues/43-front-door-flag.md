# 43: A flag per client keeps the old home page until the commissioner turns the front door on

Spec: `.scratch/front-door/PRD.md`. Source: H30 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** `client.toml` of each client gets `front_door = true | false`. Both clients merge with `false`.

- With `false`, `/` is the old home page of `main` (`apps/site/src/app/page.tsx` and `home-chapter` on `origin/main`), and the `[menu]` holds the items of `main`, including Midseason Report and Trade Analyzer. The front door is live at the hidden route `/ask/`: no menu item and no link reach it, and its page has `noindex`.
- With `true`, `/` is the front door, and the menu is the 4 items of the spec. `/ask/` serves nothing (404), since the front door is at `/`.

The flag is read at build time, through the generated client values, like the other client keys.

**Blocked by:** none

**Status:** in-progress

- [ ] `front_door = false` builds the home page and the menu of `main`, and the front door at `/ask/`, with `noindex`.
- [ ] `front_door = true` builds the front door at `/` and the 4-item menu, and no `/ask/` page.
- [ ] Both clients have `front_door = false`.
- [ ] `check:export` and `check:floor` pass for both clients.
