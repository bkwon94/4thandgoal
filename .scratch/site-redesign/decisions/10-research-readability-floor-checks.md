# 10: How does the readability floor run as checks?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The readability floor is part of the proof of the goal: body text of 16px or more, text pairs of 4.5 to 1 or more, tap targets of 44px or more, and no sideways scroll at 390px. Each check runs on every route, in both clients and both themes. Find the tool that runs it, such as axe or Playwright in the site tests, and its cost per run. The spec needs the tool and the place of each check.

## Decision

The floor runs in Playwright against the static export of each client. `@axe-core/playwright` with the rule `color-contrast` checks the contrast, and the check fails on an `incomplete` result too, because axe gives no verdict on text over an image, a gradient, alpha, or an overlap. A `page.evaluate` scan checks the tap targets, the scroll width at 390px, and the text size, because axe has no font size rule and its `target-size` rule checks 24px only. The check sets the theme with `addInitScript` on the `localStorage` key `cpc.theme`, then asserts the class on `<html>`.

The check runs in `build-each-client.mjs` after `check:export` for each client, so CI runs it on each PR with no extra build. It stays out of `check:fast`. `check.yml` needs a Chromium install step. The estimate is 30 to 60 seconds for the matrix, plus 30 to 60 seconds for the install. The first build ticket measures the real time.

Notes: `decisions/10-research-readability-floor-checks.notes.md`. Claude decided from the research, 2026-11-05. Ticket 13 holds the four open choices for Brian.
