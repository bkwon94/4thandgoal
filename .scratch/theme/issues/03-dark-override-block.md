# 03: The dark override block

**What to build:** With the theme class on the root element, the whole site turns dark with no component edit. One override block re-points the light tokens: the page to brand black, the ink tokens to the on-dark tokens, the page rule to the dark rule, the light grey to the raised dark surface, the card token to the raised dark surface, the red text token to light red. The dark rule, the divider, and the off bar take one-step-lighter partners so they stay visible on the lifted card. The block sets the dark color scheme so native controls follow. Every pair carries a contrast comment with its ratio on each dark surface, in the style of the movement arrows. The old comment that says the page stays in the light scheme goes, with a pointer to ADR 0007. Demo: add the class on the root element in devtools.

**Blocked by:** 01 (card token), 02 (red text token).

**Status:** done

- [x] With the class on the root element the page is black, the card is the raised dark surface, and the masthead and the compact bar are flush brand black.
- [x] Every text pair on the dark surfaces meets 4.5 to 1. Every graphic pair meets 3 to 1. The ratios sit in the token comments.
- [x] Brand red carries no text on a dark surface. Red fills, borders, and the glow stay brand red.
- [x] The rules and dividers are visible on the lifted card and on the dark page.
- [x] The dark color scheme is on under the class. The old light-scheme comment is gone.
- [x] Typecheck, test, and build pass. The light site looks the same without the class.
