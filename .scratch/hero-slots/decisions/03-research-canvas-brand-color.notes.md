# 03: Notes on how the canvas gets the brand colors

Ticket: `.scratch/hero-slots/decisions/03-research-canvas-brand-color.md`. Research of 2026-11-07.

## 1. Short answer

Keep the grid and the glow in the CSS `.hero-texture` layer under the canvas, as ADR 0027 already says. The canvas then needs only three opaque roles: `accent`, `on-dark`, and `on-dark-muted`. Each is a plain hex in every client.

At mount, the scene reads each role from a hidden probe span with `color: var(--color-<role>)`. `getComputedStyle(probe).color` gives an `rgb(r, g, b)` string, and the scene passes that string to `fillStyle` as is. A dim light uses `globalAlpha`, so no code parses a color.

Add one brand test that each hero role has the same value in the light set and the dark set. This keeps the scene correct after a theme switch with no listener.

## 2. Repo facts

### How a brand color reaches CSS

1. `clients/<slug>/brand.toml` holds a `[light]` set and a `[dark]` set. Each set has the base roles and an optional `derived` table.
2. The schema allows only a hex for a base role: `HEX` pattern `^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$` (`packages/design/site/brand/brand.ts:220`, `:237`). A derived role takes a hex or a mix (`brand.ts:241`). No brand value can be `oklch` or any other space.
3. A derived role with no override takes a formula (`brand.ts:67-80`). For example, `accent_glow` is 45% `accent` over `transparent` (`brand.ts:70`), and `on_dark_muted` is 60% `on_dark` over `band` (`brand.ts:77`).
4. `cssValue` writes a hex as is, a role as `var(--color-<role>)`, and a mix as `color-mix(in srgb, var(...) N%, var(...))` (`brand.ts:108-112`).
5. `apps/site/scripts/client-build.mjs:339` writes `apps/site/src/generated/brand.css` with `brandCss`. The light set goes in `@theme static`, the dark set goes in `.dark` (`brand.ts:125-135`).
6. `apps/site/src/app/globals.css:9` imports the generated file. The `.dark` class on `<html>` turns on the dark set (`globals.css:274-276`).
7. Tailwind 4 and Lightning CSS keep each hex, but shorten it, such as `#999`. For a `color-mix` token they add an 8-digit hex fallback, then the `color-mix` under `@supports (color:color-mix(in lab, red, red))`. Proof: a compile of the CPC `brand.css` with `@tailwindcss/node` 4.3.3 in the scratchpad gave `--color-accent-glow:#b8342a73}@supports (color:color-mix(in lab, red, red)){:root,:host{--color-accent-glow:color-mix(in srgb, var(--color-accent) 45%, transparent)}}`.
8. `brand.ts:150-170` already has `colorsOf(brand, set)`. It gives the sRGB `Rgba` of each role of one set, with the mix done the way the browser does it. The contrast test uses the same module (`apps/site/scripts/brand-contrast.test.mjs:9`).

### The four roles per client

| Role | Token | CPC light | CPC dark | NorCal light | NorCal dark | Form |
| --- | --- | --- | --- | --- | --- | --- |
| brand red | `--color-accent` | `#b8342a` (`clients/cpc/brand.toml:8`) | `#b8342a` (`:47`) | `#c2410c` (`clients/norcal/brand.toml:10`) | `#c2410c` (`:41`) | hex |
| on-dark | `--color-on-dark` | `#ffffff` (`cpc:34`) | `#ffffff` (`cpc:67`) | `#f5f0e6` (`norcal:33`) | `#f5f0e6` (`norcal:59`) | hex override |
| on-dark-muted | `--color-on-dark-muted` | `#999999` (`cpc:36`) | `#999999` (`cpc:83`) | `#a8a29a` (`norcal:35`) | `#a8a29a` (`norcal:61`) | hex override; formula is a `color-mix` |
| grid | `--color-grid` | `#1c1c1c` (`cpc:18`) | `#1c1c1c` (`cpc:52`) | `#181818` (`norcal:20`) | `#1d1d1d` (`norcal:50`) | hex |
| glow | `--color-accent-glow` | mix of `accent` 45% (`brand.ts:70`) | same | mix of `accent_text` 35% (`norcal:28`) | mix of `accent` 45% (formula) | `color-mix` |
| hero rule | `--color-rule-dark` | `#333333` (`cpc:37`) | `#444444` (`cpc:85`) | `#2e2e2e` (`norcal:36`) | `#2e2e2e` (`norcal:62`) | hex |

The clients are `cpc` and `norcal`. No client uses `oklch`.

### Theme differences

1. `accent`, `on-dark`, and `on-dark-muted` are the same in both sets of both clients.
2. `grid` differs in NorCal: `#181818` in light, `#1d1d1d` in dark.
3. `rule-dark` differs in CPC: `#333333` in light, `#444444` in dark. If the dashed median line uses `rule-dark`, its color changes with the theme.
4. The NorCal glow differs: light mixes the gold `accent_text`, dark takes the formula on `accent`.
5. The equality in item 1 is a convention of the brand files. The schema does not enforce it. The comments say it: "the hero stays dark in both themes, so they equal the hero roles of the dark set" (`norcal:31-32`).
6. The theme button switches the theme at run time with `classList.toggle` (`packages/design/site/shell/theme-button.tsx:33`). A color read once at mount goes stale after a switch, unless the role is the same in both sets.

### Tokens the hero uses

1. `Hero` paints `bg-band`, `text-on-dark`, and `border-rule-dark` (`packages/design/site/parts/hero.tsx:31`). The brackets use `border-on-dark-muted` (`hero.tsx:42`).
2. `.hero-texture` draws `--color-accent-glow` as a radial gradient over two linear gradients of `--color-grid` (`apps/site/src/app/globals.css:406-415`).
3. ADR 0027 keeps the grid texture and the brand glow when the scene replaces the scan line (`docs/adr/0027-the-hero-scene-settles-on-a-canvas.md:7`). So the canvas does not have to draw the grid or the glow.

### What the client values expose

1. `ClientValues.brand` is `{ sets: BrandSets; logo: string | null }` (`apps/site/src/lib/client-values.ts:26`). It holds no color.
2. `clientValuesText` writes only `{ sets, logo }` for the brand (`apps/site/scripts/client-build.mjs:338`, generated `apps/site/src/generated/client-values.ts:44-50`).
3. ADR 0012 says a component reads no file and no env, and takes data as props (`docs/adr/0012-a-component-takes-data-and-returns-markup.md:3-7`). The test bans an import of `node:fs`, of the config module, of a `lib/data` loader, and a read of `process.env` (`apps/site/src/component-rule.test.ts:1-4`). A read of `getComputedStyle` in a client component is not in that list.
4. For path B, the page reads `clientValues` in the app layer and passes the colors down as a prop: page, then `Hero`, then the scene.

## 3. Primary-source facts

1. A legacy sRGB color, such as a hex, has a computed value that serializes as `rgb()` or `rgba()`. https://www.w3.org/TR/css-color-4/#serializing-sRGB-values
2. A `color-mix()` with no `currentColor` serializes as a `<color>` in the form of its mix space. `in srgb` gives `color(srgb r g b)`, not `rgb()`. https://www.w3.org/TR/css-color-5/#serial-color-mix
3. An `oklch()` value keeps the `oklch()` form. https://www.w3.org/TR/css-color-4/#serializing-oklab-oklch
4. An unregistered custom property computes to its "specified value with variables substituted". The browser replaces each `var()`, but does not evaluate `color-mix()`. https://www.w3.org/TR/css-variables-1/#defining-variables
5. A property registered with `syntax: '<color>'` computes to a computed color. https://www.w3.org/TR/css-properties-values-api-1/#calculation-of-computed-values
6. The `fillStyle` setter parses a string as a CSS color. On failure it returns and keeps the old style. The getter returns the "HTML-compatible serialization": `#rrggbb` for an opaque 8-bit sRGB color. https://html.spec.whatwg.org/multipage/canvas.html#fill-and-stroke-styles and https://www.w3.org/TR/css-color-4/#serializing-sRGB-values
7. MDN browser compat data gives Safari, with iOS as a mirror: hex and `rgb()` from 1, `color()` from 15, `oklch()` from 15.4, `color-mix()` from 16.2. Chrome gives 111 for each of the last three. https://github.com/mdn/browser-compat-data/blob/main/css/types/color.json
8. MDN compat data for `CanvasRenderingContext2D.fillStyle` has no entry for each color function. https://github.com/mdn/browser-compat-data/blob/main/api/CanvasRenderingContext2D.json
9. WebKit draws wide-gamut CSS colors, such as `color(display-p3 ...)`, in a 2D canvas from iOS 15.1 and macOS 12.1. https://webkit.org/blog/12058/wide-gamut-2d-graphics-using-html-canvas/ and https://webkit.org/blog/12140/new-webkit-features-in-safari-15-2/
10. WebKit parses a canvas color string with its main CSS color parser. https://webkit.googlesource.com/WebKit/+/62c15071e892ba610c3477e054612dec44c8d322/Source/WebCore/html/canvas/CanvasStyle.cpp

### Proof in the browser

The page `color-research/page.html` and the script `color-research/run.mjs` run in Playwright 1.64.1. The engines are HeadlessChrome 156 and WebKit 27.2. Both engines gave the same results:

| Input | `getComputedStyle(el).color` | `fillStyle` read back | pixel |
| --- | --- | --- | --- |
| `var(--color-accent)`, hex | `rgb(184, 52, 42)` | `#b8342a` | 184 52 42 255 |
| `var(--color-on-dark-muted)`, hex | `rgb(153, 153, 153)` | `#999999` | 153 153 153 255 |
| `var(--color-accent-glow)`, `color-mix` with `transparent` | `color(srgb 0.721569 0.203922 0.164706 / 0.45)` | same string | 184 51 42 115 |
| `color-mix(in srgb, #fff 60%, #141414)` | `color(srgb 0.631373 0.631373 0.631373)` | same string | 161 161 161 255 |
| `oklch(0.55 0.17 28)` | `oklch(0.55 0.17 28)` | same string | 193 61 52 255 |
| `"var(--color-accent)"` given to `fillStyle` | n/a | rejected, old style kept | old color |

1. `getPropertyValue("--color-accent-glow")` gave `color-mix(in srgb, #b8342a 45%, transparent)`. The `var()` is substituted, but the mix is not evaluated.
2. The same property, registered as `<color>`, gave `color(srgb 0.721569 0.203922 0.164706 / 0.45)`.
3. After the `.dark` class goes off, the NorCal grid probe changed from `rgb(29, 29, 29)` to `rgb(24, 24, 24)`. A read at mount follows the theme of that moment only.

Playwright WebKit on macOS is not Safari on iOS. The iOS facts come from items 7 to 10 above.

Paths, all under the scratchpad:

- `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/9834a161-8303-4eb7-b790-3811aa5dfb8b/scratchpad/color-research/page.html`
- `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/9834a161-8303-4eb7-b790-3811aa5dfb8b/scratchpad/color-research/run.mjs`
- `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/9834a161-8303-4eb7-b790-3811aa5dfb8b/scratchpad/color-research/out.txt`
- `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/9834a161-8303-4eb7-b790-3811aa5dfb8b/scratchpad/color-research/tw.mjs`

## 4. Comparison

- **A.** Read the computed color of a probe at mount.
- **B.** Write triplets at build time into the client values, and pass them as props.
- **C.** The canvas draws only opaque hex roles, and alpha comes from `globalAlpha`. The grid and the glow stay in CSS. Each of A and B can use C.

| | A: read at mount | B: build triplets | C + A (recommended) |
| --- | --- | --- | --- |
| Per client | Correct, because the CSS of the build is the source. | Correct, from `colorsOf` of the same `brand.toml`. | Correct. |
| Per theme | Correct at mount. Stale after a theme switch for a role that differs, such as the NorCal `grid` or the CPC `rule-dark`, unless a `MutationObserver` reads again. | Needs both sets plus a theme read in the browser. A single set is wrong for the NorCal `grid` in light. | Correct, because the three roles are the same in both sets, and a test holds that. |
| Safari on iOS | Low risk for a hex: `rgb()`. A `color-mix` token gives `color(srgb ... / a)`, which needs `color()` in canvas (iOS 15+) and `color-mix` (16.2+). Older engines get the hex8 fallback of Lightning CSS. | Lowest risk: the scene gets `rgb()` strings or numbers. | Low risk: `rgb()` strings only, accepted since Safari 1. |
| ADR 0012 | Fits. A DOM read is not a file, an env, or a config read. The scene still takes its data as props. | Fits best: the colors arrive as data. Every page with a scene must pass one more prop. | Fits, as A. |
| Code size | About 10 lines in the scene: probe spans and one read. | About 15 lines: the build, the `ClientValues` type, and a prop on each page and on `Hero`. | About 10 lines, and the canvas draws no grid and no glow. |
| What a test checks | Playwright, per client: the canvas pixel of a red light equals the `accent` of `brand.toml`. | Vitest: generated triplets equal `colorsOf(brand, set)`. Playwright still checks the pixel. | Vitest: hero roles equal in both sets for each client. Playwright: pixel per client, in both themes. |
| Source of truth | CSS, one source. | `brand.toml` through `colorsOf`, a second copy in JS. | CSS, one source. |

Path B is a good fallback. Take it if Brian wants the scene to read nothing from the DOM. Then write one triplet set from `colorsOf(brand, "dark")` for the three hero roles, and keep the same equality test.

## 5. Risks and what the spec must test

1. **Theme drift.** A future brand can give a hero role a different value in light. The probe then reads the theme at mount and goes stale after a switch. Test: a vitest beside `apps/site/scripts/brand-contrast.test.mjs` checks that `accent`, `on_dark`, and `on_dark_muted` of `colorsOf` are equal in both sets, for each client under `clients/`.
2. **The grid or the glow moves into the canvas.** NorCal has a grid and a glow that differ by theme, and the glow is a `color-mix`. Keep them in `.hero-texture`. If the spec moves them, it must read them again on a theme switch and it must accept a `color(srgb ... / a)` string.
3. **A `color-mix` token in the canvas.** The serialized form is `color(srgb ...)`, not `rgb()`. A regex for `rgb()` fails on it. Pass the string to `fillStyle` as is, or keep the canvas to hex roles. The spec must not parse a color with a regex.
4. **A raw `var()` in `fillStyle`.** Canvas rejects it with no error and keeps the last style. Test: a red light pixel is not black.
5. **A read before the CSS loads.** The scene is a client component and the CSS sits in the `<head>` of the static export, so the read at mount sees the tokens. Test: Playwright reads the canvas pixel of a red light after the settle, for `cpc` and `norcal`, in dark and in light. Each must equal the `accent` hex of its `brand.toml`.
6. **The NorCal accent is orange.** The "brand red" of the scene is the `accent` role: `#c2410c` in NorCal, not a red. Brian may want the gold `accent_text` for the NorCal flare. The spec must name the role, not the hue.
7. **The dashed median line.** If it uses `rule-dark`, CPC changes it by theme. Use `on-dark-muted` with `globalAlpha`, or add `rule-dark` to the equality test.

### Facts not confirmed

1. No primary source says, line by line, that Safari on iOS accepts `oklch()` or `color-mix()` as a string in `fillStyle`. MDN has no canvas row for each color function. The WebKit parser and the WebKit 27.2 run suggest yes, from 15.4 and 16.2. The recommended path does not depend on it.
2. Real iOS Safari was not tested.
