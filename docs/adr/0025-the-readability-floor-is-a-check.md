# The readability floor is a check

A manager reads the site on a phone, often in sun or in the dark. A page that is hard to read fails the goal of the site, even when every test of its markup passes. A rule with no check is no rule (ADR 0016). So the readability floor is a check, and a PR that breaks it fails CI. We decided this in decisions 10 and 13 of `site-redesign`.

## The four rules

- **Text size.** Prose is 16px or more. Prose is a `<p>` element or an element with the `data-prose` marker. All other text is 11px or more: labels, chips, sub lines, table figures, tile captions, and dock labels.
- **Contrast.** Each text meets the WCAG AA split: 4.5 to 1 for normal text and 3 to 1 for large text. The token test `brand-contrast.test.mjs` still holds each text pair of each set at 4.5 to 1. So the page check catches only what the tokens cannot see, such as text at an opacity, on the grid, or under an overlap.
- **Tap targets.** Each link, button, and form control is 44px or more on each side, the WCAG 2.5.5 size. A link inside prose is exempt, as WCAG 2.5.5 allows. The check prints each exempt link, so the exemption stays visible.
- **No sideways scroll at 390px.** A wide box that scrolls on its own is allowed, because the page itself does not scroll.

## How the check runs

- Playwright runs the check in Chromium on the static export of each client. It is the highest seam of the site, because it measures the real page. jsdom has no layout, so a Vitest test cannot measure a size, a box, or a scroll width.
- axe with the one rule `color-contrast` checks the contrast. An `incomplete` result fails too, because axe gives no verdict on text over an image, a gradient, alpha, a pseudo element, or an overlap. A check that read only the violations would pass that text with no test.
- A scan in the page checks the text size, the tap targets, and the scroll width. axe has no rule for the font size, and its `target-size` rule checks 24px only.
- The check sets the theme with `addInitScript` on the `localStorage` key `cpc.theme`, then asserts the class on `<html>`. So the boot script is the one path to a theme in the check, as for a reader.
- `build-each-client.mjs` runs `check:floor` after `check:export` for each client, while `out/` holds that client. `pnpm check` runs it, so CI runs it on each PR with no extra build. `check.yml` installs Chromium.
- The floor stays out of `check:fast`. It needs a build of each client and a browser, and the hook must stay fast.
- The project `rules` of `apps/site/playwright.config.ts` proves each rule on small real pages in Chromium. `pnpm check` runs it once, before the builds.

## The depths of the check

- The **full floor** runs all four rules in both themes, at 390px and at 1280px, on each page of `FULL_FLOOR_PAGES` in `apps/site/e2e/floor.spec.ts`.
- The **fast sweep** loads every other built page once, in dark at 390px. It checks the text size and the sideways scroll only.
- A state that needs the live API, such as the result of the analyzer, stays out of the check. Brian's verdict on the screenshots covers it, because a fake API is a mock.

## Consequences

- A failure names the page, the theme, the width, the element, and its measure, such as `p.m-0 "Joe Burrow swept Top Scorer and Game Cha" is 14px, under the prose floor of 16px`.
- The check prints the count of each text tier and the time of each page, so a slow page and a shift of the tiers show in the log.
- No allow list holds a known failure. A page that breaks the floor fails the check, old page or new. This follows the rule of ADR 0016 that no suppression silences a rule.
- A page that comes out of the redesign joins `FULL_FLOOR_PAGES`. The page ticket adds it when the page passes.
