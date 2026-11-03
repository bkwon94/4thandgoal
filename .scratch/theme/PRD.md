# A light and dark theme with a theme button

Status: ready-for-agent
Date: 2026-10-27

Glossary: `GLOSSARY.md`. Decisions: `docs/adr/0006-report-look-at-every-width.md` and
`docs/adr/0007-dark-theme-is-one-override-block.md`. Read both before you touch the look.

## Problem Statement

A reader opens the site at night and gets a white page under black cards. The mix reads as
"some pages are light, some are dark", and the white page is bright in a dark room. The reader
has no way to pick a dark look, and the site ignores the choice a reader makes elsewhere.

## Solution

The site offers two themes, light and dark. The light theme is the report look and stays the
default. The reader presses the theme button in the masthead or the compact bar to switch. The
choice holds across visits on that device. In the dark theme the page goes black, the black
card lifts one step to grey so it keeps its edge, and the masthead and the compact bar stay black
and flush with the page. Every text pair on the dark surfaces meets the contrast rule.

## User Stories

1. As a reader, I want a theme button in the masthead, so that I switch the theme on any page.
2. As a reader, I want the theme button in the compact bar, so that I switch after I scroll.
3. As a desktop reader, I want the theme button at the end of the menu row, so that it sits where the menu button sits on a phone.
4. As a reader, I want one press to switch the theme, so that I do not open a menu to find it.
5. As a reader, I want the site to remember my choice, so that the next visit opens in my theme.
6. As a first-time reader, I want the light theme, so that the site matches the report look.
7. As a reader, I want the page to paint in my theme on load, so that I never see a flash of the other theme.
8. As a reader in the dark theme, I want the page black, so that the page is not bright in a dark room.
9. As a reader in the dark theme, I want the black card to keep its edge, so that a section still reads as a card.
10. As a reader in the dark theme, I want the masthead and the compact bar flush with the page, so that the header reads as one dark band.
11. As a reader in the dark theme, I want every line of text to meet the contrast rule, so that I can read the small print.
12. As a reader in the dark theme, I want red accents to stay red, so that the brand holds.
13. As a reader in the dark theme, I want red text to read as light red, so that it passes the contrast rule on black.
14. As a reader in the dark theme, I want the movement arrows of the power rankings to keep their colors, so that up and down read the same in both themes.
15. As a reader in the dark theme, I want the rules and dividers to stay visible, so that the layout holds its structure.
16. As a reader in the dark theme, I want the report images to look as the pipeline made them, so that no image is inverted or dimmed.
17. As a reader in the dark theme, I want the form controls and the scrollbars in the dark scheme, so that no bright control stands out.
18. As a reader in the dark theme, I want the passphrase dialog and the menu sheet in the dark theme, so that no overlay flashes white.
19. As a screen reader user, I want the theme button to say what a press does, so that I know the result before I press.
20. As a keyboard user, I want the theme button in the tab order next to the menu button, so that I reach it without a hunt.
21. As a phone reader, I want the theme button at least 44px, so that a thumb hits it.
22. As a reader with motion off, I want the switch to flip at once, so that no transition plays.
23. As a reader with scripts off, I want the light theme and no theme button, so that the page still reads as the report.
24. As a reader in a private window, I want the switch to work for this visit, so that blocked storage does not break the button.
25. As a maintainer, I want the dark theme in one override block, so that a new token gets its dark partner in one place.
26. As a maintainer, I want a contrast ratio in the comment of every dark pair, so that I can check a change without a tool.
27. As a maintainer, I want the black card painted with its own token, so that the card can lift while the masthead stays black.
28. As a maintainer, I want tests that press the button through the masthead, so that the tests read what a reader sees.

## Implementation Decisions

- The dark theme is one `.dark` block on the root element. It re-points the light tokens to dark partners: the white page to the brand black, the ink tokens to the on-dark tokens, the page rule to the dark rule, the light grey to the raised dark surface. It sets the color scheme to dark, so native controls follow.
- The root element gets the class from a stored choice only. The site does not follow the system setting. The export ships no theme class, so the light theme is the default.
- A new token paints the black card. It is the brand black in the light theme and the raised dark surface in the dark theme. The six components that paint a black card switch to it. The masthead, the compact bar, and the menu keep the brand black, so they sit flush with the dark page.
- Red never re-points, because white text sits on red fills. A new token carries red text on the page: brand red in the light theme, light red in the dark theme. Red text on the page switches to it. Red text already on a black card keeps light red. Fills, borders, and the glow keep brand red.
- The dark rule re-points one step lighter in the dark theme, because the card lifts and the old rule vanishes on it. The divider and the off bar take dark partners the same way.
- Every new or re-pointed pair carries a contrast comment with its ratio on each surface, in the style of the movement arrows. Text pairs meet 4.5 to 1. Graphic pairs meet 3 to 1. Measured: white on the raised surface 15.1, light grey text 9.4, muted text 5.3, light red 7.7, blue arrow 4.2, red arrow 4.1. Brand red on black is 3.1 and on the raised surface 2.6, so it never carries text on a dark surface. Rules, dividers, and the off part of a meter are decorative, so the 3 to 1 graphic rule does not bind them. The on part of a meter carries the value.
- The light grey re-points to `#1f1f1f`, one step between the page and the lifted black card, so a checked row still shows a change.
- The raised dark surface `chip-dark` re-points to `#313131`. An off tab and a waiver box keep an edge on the lifted black card, and muted text on it passes 4.5 to 1.
- The shadcn primary pair re-points to ink on page, so a default button has an edge on the dark page.
- The theme button is a 44px icon button from the icon set the site already ships. It shows a moon in the light theme and a sun in the dark theme. Its accessible name says the action of a press: "Switch to dark theme" or "Switch to light theme". It is a plain button, not a switch role.
- The theme button is one shared component, as the menu button is. It renders left of the menu button in the masthead and in the compact bar at every tier where the menu button shows. On the desktop tier it renders at the end of the menu row. With scripts off it does not render.
- A storage helper holds the choice under one key with the value light or dark, in the shape of the passphrase helper: every access guarded, a blocked storage returns no choice and a failed write is silent. Nothing is stored until the reader presses the button.
- A press flips the class on the root element and stores the choice. The button reads the class from the root on mount, so a stored dark choice set by the boot script shows the sun at once.
- A small inline script in the root layout runs before the first paint. It reads the stored choice and adds the class when the choice is dark. It guards the storage read. It is the one script that runs before React, and it stays under a few lines.
- The switch has no transition. Colors flip at once in both themes, so no reduced-motion case is needed.
- Images from the pipeline are untouched in both themes. No filter, no inversion, no matte change.
- The comment on the color scheme line that says the page stays in the light scheme is replaced, because ADR 0007 reverses it.

## Testing Decisions

- A good test reads what a reader sees or does: a button by its name, a class on the root element, a stored key. No test reads a class name of a component or a token value.
- Seam 1, the masthead render. Render the masthead as its existing tests do. Find the theme button by its accessible name. Press it. The root element gains the class, the stored key holds dark, and the button renames itself. Press again and the class and the key go back. A second render with a stored dark choice shows the sun name. The same tests cover the button in the compact bar once the masthead scrolls out, and the button at the end of the desktop row. A blocked storage still flips the class for this visit. The storage helper gets no test of its own, because a press through the masthead reaches it.
- Seam 2, the boot script. Export the script as a string from one place. Run it against jsdom with a stored dark choice and read the class on the root element. Run it with no choice and with a blocked storage and read no class.
- No seam for the CSS. jsdom does not compute the tokens. The ratio comments and a browser capture of the week page at 390 in both themes are the check, as the arrows are today.
- Prior art: the masthead tests for the render seam and the compact bar helpers, the reduced-motion tests for a preference under test, the passphrase helper for guarded storage.
- Before a push: typecheck, test, build, then the export check.

## Out of Scope

- A system theme option, or any follow of the system setting.
- A transition or crossfade on the switch.
- A dark matte for the pipeline images, or any change in the pipeline repo.
- A theme control inside the menu sheet.
- A third theme, or a per-page theme.
- The pages under public that the pipeline publishes. They do not load the site stylesheet.

## Further Notes

- The handoff said brand red on black is about 4.0 to 1. The measured ratio is 3.1. The decision to keep red off dark text rests on the measured number.
- The black card keeps its glossary name in the dark theme, where it is grey. The name is the brand, not the hex.
- Branch before code. The site deploys on a push to main.
- The chapter rail keeps a hover color transition that also fades on a theme flip. It predates the feature and is left as is.
- The waiver page did not build in the pass because no published week has waiver data, so the waiver surfaces are checked by ratio only.
