# 09: What are the light sets of both brands in the look?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** prototype

**Blocked by:** 03

**Status:** done

## Question

Every client has a light option, so NorCal needs a light set. Brian asked Claude to pick the NorCal light colors. Settle the light set of CPC and of NorCal in the look. Each text pair meets 4.5 to 1. Brian approves both sets on the canvas.

## Decision

The light set of each brand is board "Light 3 · Dark hero". Brian chose this on 2026-11-05, on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8. He agreed with Claude's recommendation.

The rule: in light, the page and the cards are light, but the hero stays dark in both themes. The hero sits on the `band` color of the brand, with the grid, the glow, the brackets, and the accent text of dark mode. So the site has one hero, and the light reader still gets a light page.

The light sets:

| Role | CPC | NorCal |
| --- | --- | --- |
| page | `#f4f4f4` | `#f5f3ef` |
| card | `#ffffff` | `#ffffff` |
| raised, such as the active dock item | `#ebebeb` | `#ecebe8` |
| rule | `#e0e0e0` | `#e2e0dc` |
| text | `#141414` | `#1c1917` |
| ink 2 | `#3a3a3a` | `#3f3a35` |
| muted | `#666666` | `#6b6359` |
| accent ink, the accent as text on the page and the card | `#a52e25` | `#9a3412` |
| accent, the fills with white text | `#b8342a` | `#c2410c` |
| bar off | `#dddddd` | `#e2ddd3` |
| band, the hero surface | `#141414` | `#0a0a0a` |
| the grid lines of the hero | `#1c1c1c` | `#181818` |
| the glow of the hero | `#b8342a` at 45% | `#e0a526` at 35% |
| hero text | `#ffffff` | `#f5f0e6` |
| hero ink 2 | `#cccccc` | `#d6d0c4` |
| hero muted | `#999999` | `#a8a29a` |
| hero accent text | `#f2a59e` | `#e0a526` |
| hero rule | `#333333` | `#2e2e2e` |
| hero raised, such as the share bar track | `#262626` | `#232323` |

Each text pair meets 4.5 to 1. The lowest pair is 5.2 to 1: muted on the CPC page, and white on the NorCal accent. The board lists each ratio.

NorCal gold, `#e0a526`, is too light for text on a light surface. In light it shows only as the hero glow and as the hero accent text. The spec maps each row to a key of `brand.toml`. The hero rows match the dark roles that the light set has now, such as `on_dark_2`, `on_dark_muted`, `rule_dark`, and `chip_dark`.

Brian rejected board "Light 1 · Paper" and board "Light 2 · Warm". On a light hero, the grid, the glow, and the brackets go faint, so the hero loses the first reaction.

The light sets use no data, so the list of ideas that need new data stays empty. The decision adds one consequence to ADR 0024: the hero stays dark in both themes.

The prototype lives on the canvas, not in the repo, so no prototype code needs a delete.
