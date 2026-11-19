# 02: What a Stop and its motion look like

Map: `.scratch/front-door-tour/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** done

## Question

Brian wants a clean Tour with strong motion. The spec needs one chosen look for the spotlight, the Stop card, the move between Stops, the entry, and the exit.

Build three different variations on the front door, with the parts that ticket 01 chooses. Use the design bar: `transitions-dev`, scrolltide, `apple-design`, `animate`, `critique`, and `polish`. Show each on the iPhone viewport 390x660, then on the tablet and desktop sizes. Brian chooses one on his phone. Then delete the prototype code.

Check these points from the research of ticket 01 in the prototype:

1. `scrollIntoView` still moves the page under the scroll lock of the modal card, on iPhone WebKit.
2. A tap on the dim never reaches the control inside the spotlight.
3. The `box-shadow` dim looks as good as an SVG dim.
4. A hold during the Tour starts no egg.
5. The overlap assert passes on the four standard viewports.

## Decision

Brian chose look A, Spotlight glide, on his iPhone on 2026-11-18, after two rounds. The prototype is on the local branch `front-door-tour-proto`: `af82b8ef` holds the three looks, and `ee3b8111` holds round 2 of A. The prototype code never touched the Spec branch.

1. **The look.** One dim with a rounded hole glides from control to control on the `GLIDE` spring. The card rides beside the hole. Dots show the place.
2. **The hole.** It sits on the visual box of the control, not the hit box. A control with its own fill, border, or shadow counts whole. A plain control counts only what shows, such as the menu icon. The pad is equal on all sides: 6 px, or 10 px for a box under 28 px tall. The round menu button gets a circle. The other controls get a pill. Brian asked for this after round 1, because the hole sat off center on the menu button.
3. **The card.** A header names the control on the left, and "1 of 4" sits on the right of the same line. Under it sit the line, the dots, Skip, and Next or Done. The header and the line swap with Text swap soft (34). The card height never changes, because the line box holds all four lines in one grid cell.
4. **The move.** The card moves on the same `GLIDE` spring as the hole, so the two never part. When the card changes side, it fades out, holds its place, and comes back once the hole lands. This changes decision 01 at one point: the ui-sdk `Popover` still makes the page modal and owns focus and dismiss, but it no longer places the card. Its positioner lagged the glide by up to 181 px.
5. **The buttons.** Next and Done use `bg-accent text-on-dark` in both themes, as the send button and the passphrase submit do. No theme setting changed on `main`.

The five checks passed on WebKit at 390x660, 810x980, and 1080x740, and on Chromium at 1280x800, in both themes: scroll under the lock, a tap in the hole, the `box-shadow` dim (an SVG dim gives no gain), no egg on a long press, and the overlap assert. One point is open for the spec: on a move that scrolls the page, the card drifted 5.1 px for about one frame.
