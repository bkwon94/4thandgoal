# 03: The tokens of a brand

Map: `.scratch/clients/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Which tokens does a brand give? A brand has a light set, a dark set, or one set only. The spec needs the token interface: which colors, fonts, radii, and spacings exist, and how a client with one set hides the theme button. ADR 0006 and ADR 0007 hold the look of CPC today. A new token is a change that each client must answer.

## Decision

Brian decided each item in the grill of 2026-11-03.

### The file for CPC

```toml
# clients/cpc/brand.toml
radius_card = "8px"
radius_small = "3px"

[fonts]
body = '"Helvetica Neue", Arial, sans-serif'
heading = '"Helvetica Neue", Arial, sans-serif'
# A brand with font files puts them in assets/fonts/ and names them here.

# The six base roles are required in each set.
[light]
accent = "#b8342a"      # red today: the fills with white text
band = "#141414"        # blk today: the masthead and the compact bar
page = "#ffffff"        # wht today
card = "#ececec"        # gry today
text = "#1a1a1a"        # ink today
muted = "#666666"       # mute today

# A brand with no [dark] table has no theme button.
[dark]
accent = "#b8342a"      # ADR 0007: the accent never re-points
band = "#141414"
page = "#141414"
card = "#1f1f1f"
text = "#ffffff"
muted = "#999999"

# CPC overrides each derived role where the formula does not give today's value.
# The spec fills this list after the formulas exist.
[dark.derived]
accent_text = "#f2a59e" # red-lt today: the accent text on a dark page
card_band = "#262626"   # card-blk today: the lifted black card
```

### The choices and the reasons

1. **The colors take role names.** `red`, `blk`, `gry`, and `wht` become `accent`, `band`, `card`, and `page`, with the rest named by role too. A brand with a blue accent then has no class `bg-red` that paints blue. The rename is one mechanical ticket, before the design package moves: about 280 uses in 41 files, with an empty golden diff.
2. **A brand sets six base roles, and the rest derive.** Each derived role has a formula in the design package, and a brand can override it. A new brand sets six colors and gets a full theme. CPC overrides each derived role where the formula does not give its value today, so its look stays exact.
3. **The brand file decides the set count.** A brand with no `[dark]` table has no theme button and paints light. A brand with only `[dark]` paints dark and has no theme button. A two-set brand defaults to light (ADR 0007).
4. **A brand sets two font roles.** The body and the heading are each a font stack. Font files go in `assets/fonts/`, and the design package loads them with `@font-face` from the site. The build fetches no font from an outside host.
5. **A brand sets only the two radii.** The spacing, the type scale, the breakpoints, and the tracking stay in the design package, because fixed widths such as the standings columns are tuned to the type scale.
6. **The file is `brand.toml`.** The design package exports a JSON Schema for it, as each package does for `client.toml`. The build writes the CSS custom properties. An unknown role or a missing base role fails the check. The name follows the glossary: **Theme** is the reader's choice of light or dark.

### What stays in the design package

- `move-up` and `move-down`: the data colors of a rank move, with one meaning on every site.
- Every spacing, type, breakpoint, and tracking token.
- The shadcn layer, which points at the role tokens.
- The formula of each derived role: `ink-2`, `rule`, `red-ink`, `pick`, `red-glow`, `card-blk`, `on-dark`, `on-dark-2`, `on-dark-muted`, `rule-dark`, `divider`, `bar-off`, and `chip-dark` today. The spec names each formula and each new role name.
