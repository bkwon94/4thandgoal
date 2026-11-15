# 08: How does the menu sheet feel as a ui-sdk Drawer?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** prototype

**Blocked by:** 07

**Status:** done

## Question

Brian must feel it on a phone before the spec fixes it. Build a throwaway `Drawer side="top"` with the rows of `menu-sheet` and decide:

1. One snap point or more, and if a handle or a plain bar shows.
2. The `physics` values: the default `sheetPhysics.ios`, or a tune.
3. If the dim and the scale of the page follow `--drawer-progress` and `--drawer-dim`.
4. If a tap on a row still opens the row after a short drag.

Check it on an iPhone through the LAN URL, and in a narrow desktop window. Then delete the prototype code.

## Decision

The menu sheet is a `Drawer side="top"` with one snap point, the default `"content"`, and a small grab handle at its bottom edge. It uses the default `sheetPhysics.ios` with no tune. The scrim dims with `--drawer-dim`, and the page under the band does not scale. Brian agreed on 2026-11-14.

1. **One snap point, with a handle.** The menu has few rows, so a second snap point gives nothing. In a top `Drawer` the smaller snap point shows the bottom slice of the sheet, so it hid "Past weeks" above the rows. The handle shows that the sheet drags.
2. **The default `sheetPhysics.ios`.** The tune of variant C, `response 0.28` and `momentumDampingRatio 0.95`, was a guess. Each custom value must follow each bump of ui-sdk.
3. **The dim only.** The scale of the page fits a stack of cards, not a short menu. `--drawer-progress` does not inherit, so a scale needs a script on each frame.
4. **A short drag still taps.** In all variants, a 5 px touch drag opened the row, and a 20 px drag gave no tap. The `Drawer` drops the click past its `touchSlop` of 8 px, the same as the current sheet. So the spec keeps no `onClickCapture` guard of its own.

A sheet from the bottom, variant D, lost: the sheet must move in from the edge of the button that opens it, and it covers the chat box of the front door.

Facts for the spec, from the prototype:

- The `Drawer` puts its viewport in the top layer, over the band. A CSS rule must move the top edge of the viewport and the backdrop under the band, and `persistentElements` keeps the band usable while the sheet is modal.
- A mouse drag on a row does not move the sheet on desktop, in the current sheet too. The browser starts a native drag of the link. Touch is not affected.
- `next dev` rewrites `apps/site/AGENTS.md` and `next-env.d.ts`. Restore both before a commit.

The prototype has four variants on `?variant=` of the front door. It is on the branch `ui-sdk-sheet-08-prototype` at `896e43f6`, with the Tailscale origin uncommitted. The prototype code is deleted from the worktree.
