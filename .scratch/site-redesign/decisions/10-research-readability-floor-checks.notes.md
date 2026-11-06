# 10: Research notes, the readability floor as checks

Ticket: `10-research-readability-floor-checks.md`. Map: `MAP.md`. Date: 2026-11-05. Branch: `site-redesign`.

The floor has four checks. Each check runs on each route, in each client, in each theme:

- Body text is 16px or more.
- Each text pair has a contrast of 4.5 to 1 or more.
- Each tap target is 44px or more.
- No page scrolls sideways at 390px.

## Answer in short

Add Playwright Test with `@axe-core/playwright` to `apps/site`. Run it on the two static exports that `pnpm check` builds now. Use axe for the contrast. Use a short script in the page for the text size, the tap targets, and the scroll width. Run it in a new `check:floor` script that `pnpm check` calls, so CI runs it on each PR. Keep it out of `check:fast`. The full run of 56 page loads takes about 1 to 2 minutes in CI, plus about 1 minute for the Chromium install.

## 1. The tests and tools of the site now

Sources: `apps/site/package.json`, `apps/site/CLAUDE.md`, `apps/site/vitest.config.mts`, `apps/site/scripts/*.mjs`, `Makefile`, `.pre-commit-config.yaml`, `.github/workflows/check.yml`.

- **Vitest 5 in jsdom.** `pnpm test` runs `vitest run`. The config includes `apps/site/src/**/*.test.{ts,tsx}`, `apps/site/scripts/**/*.test.mjs`, and `packages/*/site/**/*.test.{ts,tsx}`. jsdom has no layout, so a Vitest test cannot measure a computed size, a box, or a scroll width.
- **The rule tests** in `apps/site/src/` read source files and fail on a broken rule: `component-rule.test.ts`, `readme-rule.test.ts`, `suppression-rule.test.ts`, `tracker-rule.test.ts`, and `reduced-motion.test.tsx`. `rule-report.ts` formats their failures.
- **A token contrast test exists.** `apps/site/scripts/brand-contrast.test.mjs` (AT-17) reads each `clients/<slug>/brand.toml`. It checks each text pair of each set at 4.5 to 1 with `TEXT_PAIRS` and `textPairsOf` from `@cpc/design/brand/brand.ts`. It checks the tokens, not the rendered page. It cannot see text on a tile, on a gradient, on the grid texture, or at an opacity.
- **No Playwright, no axe.** The repo has no `playwright.config.*` and no Playwright or axe package in `node_modules/.pnpm`. The Playwright browser cache `~/Library/Caches/ms-playwright` holds `chromium-1208` from another project. That cache does not help CI.
- **The export check.** `scripts/check-export.mjs` reads `out/` as text. It checks the copy of `public/`, the team names in each week page, the absent packages, the copy, the theme button, and the finder. It runs no browser.

How a build per client works:

1. `CLIENT=<slug> node scripts/client-build.mjs` reads `clients/<slug>/client.toml`, `brand.toml`, and `copy.toml`. It writes the generated route files and copies `clients/<slug>/published/` into `public/`. `predev` and `prebuild` run it.
2. `CLIENT=<slug> pnpm build` runs `next build` with `output: "export"` and `trailingSlash: true` (`next.config.ts`). The export goes to `apps/site/out/`.
3. `scripts/build-each-client.mjs` runs `build` and then `check:export` for each folder under `clients/` with a `client.toml`, in order. `pnpm check` runs it after `check:fast`.

One `out/` folder holds one client at a time. The second build replaces the first. A floor check must run on each export before the next build, or copy each `out/` to its own folder.

Route facts for the floor:

- `cpc` builds week 6, 7, and 8. `norcal` builds week 8. Both have `managers.json` and `rankings.json`.
- Both clients list `packages = ["week", "rankings", "managers", "analyzer"]`. Neither lists `waiver`, so no client builds the waiver route now. The waiver route is at `<season>/<week>/waiver/`, and it builds only for a client with the package and a `waiver.json` (`client-build.mjs`, line 168 to 175). The floor check must skip the waiver route for a client that omits it, or the spec must name a client that has it.
- The 404 page is `src/pages/404.tsx`. The export writes it as `out/404.html`.
- The analyzer page fetches teams from the live API (`packages/analyzer/site/lib/api.ts`, `teams-prefetch.tsx`). The check sees only the first state of the analyzer, before any passphrase. The result card needs the real API, so the screenshots cover it, not the floor check.

CI timing of the site part of `make check`, from run 42070645702 on 2026-11-05: `check:fast` takes about 42 seconds, the `cpc` build about 12 seconds, and the `norcal` build about 5 seconds. The whole job takes about 10 minutes, because the pipeline check takes about 7 minutes.

## 2. The best tool for each check

### Contrast: `@axe-core/playwright`

- Use `new AxeBuilder({ page }).withRules(["color-contrast"]).analyze()`. Source: https://playwright.dev/docs/accessibility-testing.
- The rule `color-contrast` has the tags `wcag2aa` and `wcag143`, and it is on by default. It uses 4.5 to 1 for normal text and 3 to 1 for large text. Source: https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md.
- **Large text gets 3 to 1 in axe.** Our floor says 4.5 to 1 for every text pair. The rule `color-contrast-enhanced` does not fit, because it is AAA at 7 to 1 for normal text. Pick one of these two in the spec:
  1. Accept the WCAG AA split: 4.5 to 1 for normal text, 3 to 1 for large text. This is the plain axe run.
  2. Keep 4.5 for all text. Then the custom scan below also reads each large text element and computes its own ratio when axe gives a sure foreground and background.
- **What axe does not decide.** axe returns these cases as `incomplete`, not as a pass or a fail. Source: https://raw.githubusercontent.com/dequelabs/axe-core/develop/locales/_template.json, the `color-contrast` messages.
  - `bgImage`: a background image, such as the grid texture or a pipeline image behind text.
  - `bgGradient`: a background gradient, such as a tile glow.
  - `imgNode`: the element holds an image.
  - `bgOverlap`, `elmPartiallyObscured`, `elmPartiallyObscuring`: another element overlaps the text, such as a sticky bar.
  - `fgAlpha`: the text color has alpha, such as a muted label at 60% opacity.
  - `pseudoContent`: a pseudo element paints the background.
  - `complexTextShadows`, `outsideViewport`, `shortTextContent`, `nonBmp`.
- The default axe run reports violations only. The look of board C has a grid texture and tiles, so many text nodes may land in `incomplete`. The check must fail on each `incomplete` result of `color-contrast`, or list each one by its selector so a person checks it. A check that reads only `violations` passes text on the texture with no test.
- axe also skips text that is hidden or at opacity 0. The reveal starts each section at opacity 0 (`check-export.mjs` notes it). Run the check with `reducedMotion: "reduce"` in the Playwright context, and wait for the reveal to settle. `reduced-motion.test.tsx` already proves the reduced-motion path.

### Tap targets: a custom script in Playwright, not axe

- axe has the rule `target-size`, but it checks WCAG 2.5.8 at 24px. It is off by default, with the tag `wcag22aa`. It also passes a small target that has enough space around it. Source: rule-descriptions.md, and the `target-size` help text "All touch targets must be 24px large, or leave sufficient space" in `_template.json`. Our floor is 44px for each target, the WCAG 2.5.5 AAA size, so axe does not fit.
- Use `page.evaluate` to list each visible `a[href]`, `button`, `input`, `select`, `textarea`, `summary`, `label[for]`, and `[role=button]`, `[role=link]`, `[role=tab]`. Fail when `getBoundingClientRect()` gives a width or a height under 44.
- Decide in the spec if a link inside a sentence is exempt. WCAG 2.5.5 exempts an inline link, and a 44px line height for body text is not practical.

### Sideways scroll: Playwright

- Set the viewport to 390 by 844. Fail when `document.documentElement.scrollWidth > document.documentElement.clientWidth`. Name the widest element in the failure message: the element with the largest `getBoundingClientRect().right` past 390.
- A wide table inside its own `overflow-x: auto` box does not make the page scroll. The check allows it, because the page itself does not scroll.

### Body text size: a computed-style scan in Playwright

- No axe rule checks a minimum font size. Use `page.evaluate` with a `TreeWalker` over the text nodes. For each visible text node with text, read `getComputedStyle(parent).fontSize`. Fail under 16px.
- Decide in the spec what "body text" means. The look has small labels, such as tile captions, eyebrows, and axis labels, and these may be under 16px. Two options:
  1. Every text is 16px or more. This is strict and simple. It may block the look.
  2. Every text is 16px or more, except an element in a short list of named label classes or a `data-` marker in the look. The check prints each exempt element, so the list stays short and visible.
- Read the size at 390px. A fluid `clamp()` size is smallest at the phone width.

## 3. Where the checks run, and the cost

- **Not in `check:fast`.** The hook runs `make check-fast` before each commit. A floor check needs two `next build` runs and a browser. That adds about 20 seconds of builds, plus browser time, to each commit.
- **In `pnpm check`, so in CI.** `check.yml` runs `make check` on each PR and on each push to `main`. `make check` runs `pnpm --dir apps/site check`. Add the floor run to `scripts/build-each-client.mjs` after `check:export` of each client, while `out/` holds that client. Then no second build runs, and CI runs the floor with no change to the Makefile.
- **CI needs a browser.** Add one step to `check.yml` before "Run the check": `pnpm --dir apps/site exec playwright install --with-deps chromium`. Source: https://playwright.dev/docs/ci. Chromium alone is enough, because the floor reads layout and color, and Chromium gives the same result for both.
- **A local run on its own.** A `check:floor` script lets a person run one client: `CLIENT=cpc pnpm build && pnpm check:floor`.

The server. Playwright `webServer` starts a command and waits on a `url`, and it accepts an array of servers. Source: https://playwright.dev/docs/test-webserver. The export is static, so a small static file server on `out/` is enough. A Node script with `node:http` needs no new package. `next start` does not serve an `output: "export"` build.

Run time for 7 routes x 2 clients x 2 themes x 2 widths:

- That is 56 page loads. The waiver route has no build in either client now, so the real count is 48.
- One static page load in local Chromium takes about 0.3 to 0.5 seconds. One axe run with one rule takes about 0.3 to 1 second on a long page. The three custom scans take under 0.2 seconds together. So each case takes about 1 to 2 seconds.
- With 2 Playwright workers on the GitHub `ubuntu-latest` runner, the 56 cases take about 30 to 60 seconds. Add about 2 to 3 seconds for each browser start.
- The Chromium install with `--with-deps` takes about 30 to 60 seconds with no cache.
- The total adds about 1.5 to 2 minutes to a CI job that takes about 10 minutes now. The 20-minute `timeout-minutes` of the job holds.

These run times are estimates from the CI log above and from common Playwright speeds. The first build ticket must measure them.

The contrast and the tap targets need both widths, because the layout changes between them. The text size and the scroll width need only 390px. For one simple matrix, run the contrast, the tap targets, and the text size at both widths. Run the scroll check at 390px only.

## 4. How a check picks the theme

Source: `docs/adr/0007-dark-theme-is-one-override-block.md`, `packages/design/site/lib/theme.ts`, `packages/design/site/shell/theme-button.tsx`, `apps/site/src/app/layout.tsx`.

- The theme is the class `dark` on `<html>` (`DARK_CLASS`). The theme button toggles the class and stores `"dark"` or `"light"` in `localStorage` under the key `cpc.theme` (`THEME_KEY`).
- An inline boot script in `<head>` (`BOOT_SCRIPT`) reads `cpc.theme` before the body paints. Now it adds `dark` only when the stored value is `"dark"`, so light is the default. ADR 0007 says the site does not follow the system setting.
- `paintOf` gives a boot script and a theme button only to a two-set brand. `cpc` has `[light]` and `[dark]`. `norcal` has only `[dark]` now, so its export carries the class `dark` at build time and no theme button. Ticket 09 adds the NorCal light set.
- The redesign makes dark the default for every client (MAP). So the boot script and ADR 0007 change in the build. The check must not depend on the default. It sets each theme on purpose.

How the check sets the theme:

1. Before the load, call `context.addInitScript(() => localStorage.setItem("cpc.theme", theme))`. Playwright runs it "after the document was created but before any of its scripts were run". Source: https://playwright.dev/docs/api/class-browsercontext. So the boot script reads the value on the first paint.
2. After the load, assert the class: `expect(page.locator("html")).toHaveClass(/dark/)` for dark, and no `dark` class for light. A failed assert means the key or the boot script changed. The check then fails loud and does not test the wrong theme.
3. Import `THEME_KEY` and `DARK_CLASS` from `@cpc/design/lib/theme`, so the check and the boot script use the same names.

Do not use `colorScheme: "dark"` of Playwright. It sets `prefers-color-scheme`, and the site does not read it. `storageState` with an `origins` list also works, but `addInitScript` is shorter and does not need the origin.

## 5. Recommendation

Use Playwright Test with `@axe-core/playwright`, on the static export of each client, in `pnpm check`. Reasons:

1. **It measures the real page.** jsdom has no layout, so Vitest cannot measure a size, a box, or a scroll width. The token test AT-17 cannot see text on a texture, at an opacity, or on a tile. A browser sees all of them.
2. **axe owns the contrast math.** It handles the large-text sizes and the stacked backgrounds. We do not write a second color engine.
3. **The custom scans are short.** The text size, the tap targets, and the scroll width are each one `page.evaluate`. axe has no 16px rule, and its `target-size` rule is 24px with a space rule, so it does not fit.
4. **It reuses the builds of `pnpm check`.** The floor runs in `build-each-client.mjs` while `out/` holds each client. CI already runs that on each PR. The commit hook stays fast.
5. **It fails loud on what axe does not decide.** Each `incomplete` result of `color-contrast` fails the check with its selector. A person then fixes the color or the spec lists the element.

Open points for the spec:

- Does large text get 3 to 1, the WCAG AA split, or 4.5 to 1 like all text?
- What is "body text": all text, or all text except a short named list of labels?
- Is an inline link in a sentence exempt from 44px?
- Which client, if any, proves the waiver route? Neither client builds it now.
- The check scans the first state of each page. The open menu, the analyzer result, and a manager page past the first roster are not in the matrix. Add a case for each state the spec names.

Files a later ticket adds or changes:

- Add `apps/site/playwright.config.ts`. It sets the 2 widths, `reducedMotion: "reduce"`, the static server on `out/`, Chromium only, and 2 workers.
- Add `apps/site/e2e/floor.spec.ts`. It lists the routes of the current client from `out/` and the theme sets from `brand.toml`, then runs the four checks per route, theme, and width.
- Add `apps/site/e2e/floor.ts`. It holds the three `page.evaluate` scans and the axe call with the `incomplete` rule.
- Add `apps/site/scripts/serve-out.mjs`. It is a small `node:http` server for `out/` that serves `404.html` for a missing path.
- Change `apps/site/package.json`. It adds the dev dependencies `@playwright/test` and `@axe-core/playwright`, and the script `check:floor`.
- Change `apps/site/scripts/build-each-client.mjs`. It runs `check:floor` after `check:export` for each client.
- Change `.github/workflows/check.yml`. It adds the Chromium install step before "Run the check".
- Change `apps/site/vitest.config.mts` only if Vitest picks up `e2e/`. The include globs now do not match `apps/site/e2e/`, so no change is likely.
- Change `apps/site/CLAUDE.md`. It names `check:floor` in the command list.
- Add an ADR in `docs/adr/` if the spec fixes the floor as a rule, as ADR 0016 does for the other rules.
