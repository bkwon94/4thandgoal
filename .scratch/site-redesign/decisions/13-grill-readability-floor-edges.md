# 13: Where are the edges of the readability floor?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Ticket 10 chose the tool. The check needs four choices before the spec can state the floor:

1. What counts as body text for the 16px floor? Labels, chips, and table figures are often smaller.
2. Does large text keep 4.5 to 1, or does it get the 3 to 1 that axe allows?
3. Is an inline link in a recap exempt from the 44px tap target?
4. Which page states does the check scan? The result view of the analyzer needs the live API. Neither client builds the waiver route now.

See `decisions/10-research-readability-floor-checks.notes.md`.

## Decision

Brian and Claude settled the four edges in a grill on 2026-11-05. Brian took each recommendation of Claude.

1. **Text size has two tiers.** Prose is 16px or more. All other text is 11px or more: labels, chips, sub lines, table figures, tile captions, and dock labels. The check counts a `<p>` element, or an element with a `data-prose` marker, as prose. It prints the count of each tier. The approved boards change in the build: blurbs and recaps go to 16px, and the dock labels go from 10px to 11px.
2. **Contrast on the page uses the WCAG AA split of axe:** 4.5 to 1 for normal text, and 3 to 1 for large text. The token test `brand-contrast.test.mjs` still holds every text pair of each set at 4.5 to 1. So the page check catches only what the tokens cannot see, such as text at an opacity, on the grid, or under an overlap. A 4.5 rule for large text on the page needs a second contrast engine next to axe, for little gain.
3. **A link inside prose is exempt from 44px,** as WCAG 2.5.5 allows. The check skips an `<a>` inside a prose element and prints each exempt link. Every other link and button is 44px or more. For a team in a row, the whole row is the link. A game card that opens its recap stays one button, so its team names are plain text, and the open recap gets one "Manager page" link of 44px.
4. **The scope has three depths.**
   - The full floor, all four rules in both themes at both widths, runs on 7 pages per client: home, the latest week, rankings, the managers index, the manager page with the longest team name, the empty analyzer, and 404.
   - The full floor also runs on three open states, each one tap from the first load: an open recap card on the week page, an open card on the Ladder, and the open week strip.
   - A fast sweep loads every other built page once, in dark at 390px, and checks only the text size and the sideways scroll.
   - The analyzer states that need the live API stay out of the check: the team list, the picker sheet, loading, the result, and the error. Brian's verdict on the screenshots covers them, because a fake API is a mock.

The estimate is 1.5 to 2.5 minutes in CI, plus the install of Chromium. The first build ticket measures the real time. The waiver route stays out, as decision 07 set.

The glossary gets two site terms: **Readability floor** and **Prose**. The spec writes the ADR that fixes the floor as a rule, beside ADR 0016, when the check is built.
