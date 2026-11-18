# 02: What a Stop and its motion look like

Map: `.scratch/front-door-tour/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** open

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

None yet.
