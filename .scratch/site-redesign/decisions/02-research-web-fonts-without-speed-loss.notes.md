# 02 notes: web fonts with no loss of speed

Research for `02-research-web-fonts-without-speed-loss.md`. Date: 2026-11-05. Next.js in the site: 16.4.2.

## Summary

Self-host two variable woff2 files, Latin only, with `next/font/local`. The cost is 53,660 bytes in all.
Space Grotesk is 22,320 bytes. JetBrains Mono, cut to weights 500 to 800, is 31,340 bytes.
The variable files are smaller than the static files: 53,660 bytes against 117,800 bytes.
Both fonts use the SIL Open Font License 1.1, which lets us self-host.
The site already has a test that bans `next/font`. The spec must narrow that test to ban only outside hosts.

## 1. How the site builds and serves today

- `apps/site/next.config.ts` sets `output: "export"`, `trailingSlash: true`, and `images: { unoptimized: true }`.
- `wrangler.jsonc` serves `./out` as static assets of one Cloudflare Worker per client. No Node server runs.
- `pnpm build` runs `scripts/client-build.mjs` first. That script writes `src/generated/brand.css` from `clients/<slug>/brand.toml`.
- The fonts now come from `clients/cpc/brand.toml`: `"Helvetica Neue", Arial, sans-serif` for body and heading. No font file loads.
- The brand code can already self-host a font. `packages/design/site/brand/brand.ts` writes one `@font-face` per entry of `brand.fonts.faces`, with `font-display: swap`. `client-build.mjs` copies each file from `clients/<slug>/assets/fonts/` to `public/brand/fonts/`. No client uses it now.
- `apps/site/src/app/brand-tokens.test.ts` has the test "load from no outside host". Its pattern bans `next/font`, `fonts.googleapis`, `fonts.gstatic`, `use.typekit`, and any remote `url(`, in `src/` and `packages/design/site/`. Commit `8159f80b` (Clients) added it.

### Does `next/font` work with `output: "export"`?

Yes, by the docs and by the code. It was not built in this repo.

- The static export guide lists the unsupported features. `next/font` is not on the list. Source: https://nextjs.org/docs/app/guides/static-exports, "Unsupported Features".
- The font docs say: "CSS and font files are downloaded at build time and self-hosted with the rest of your static assets. No requests are sent to Google by the browser." Source: https://nextjs.org/docs/app/api-reference/components/font.
- The loader emits each file at build time and puts the self-hosted URL in the CSS. Source: `node_modules/next/dist/compiled/@next/font/dist/google/loader.js`, the loop that replaces `googleFontFileUrl` with `selfHostedFileUrl`.
- `next/font/google` fetches from Google at build time. In `next dev` a failed fetch logs "Failed to download ... Using fallback font instead". In `next build` the error is thrown, so the build fails with no network. Source: the same `loader.js`, the `catch (err)` block with `if (isDev)`.

## 2. The load method

| Method | Runtime host | Build needs network | Preload | Fallback metrics | Fits the repo test |
| --- | --- | --- | --- | --- | --- |
| `next/font/google` | own origin | yes, Google | automatic, per `subsets` | automatic | no |
| `next/font/local` | own origin | no | automatic | automatic, Arial only | no, until the test changes |
| own `@font-face` in `brand.ts` | own origin | no | by hand in the root layout | by hand | yes |
| CSS `<link>` to Google Fonts | Google | no | no | no | no |

### Facts behind the table

- `display` defaults to `'swap'` in both loaders. Source: font docs, `display`.
- `preload` defaults to `true`. A font in the root layout preloads on all routes. Source: font docs, `preload` and "Preloading".
- `subsets` exists only in `next/font/google`. It sets which subsets get a preload tag. `next/font/local` ships the file as it is, so we must subset the file ourselves. Source: font docs, reference table and `subsets`.
- `adjustFontFallback` defaults to `true` for Google and to `'Arial'` for local. The only local values are `'Arial'`, `'Times New Roman'`, and `false`. Source: font docs, `adjustFontFallback`.
- The automatic fallback picks Times New Roman for a serif font and Arial for all others. A monospace font gets Arial. Source: `node_modules/next/dist/server/font-utils.js`, `calculateSizeAdjustValues`.
- The docs say "We recommend using variable fonts for the best performance and flexibility." Source: font docs, "Google Fonts" and "Local Fonts".
- `declarations` in `next/font/local` adds any `@font-face` descriptor, for example `ascent-override`. Source: font docs, `declarations`.
- web.dev: "of these approaches, `font-display: swap` delays text render the least". Its cost is a shift when the font arrives late. `optional` waits no more than 100 ms and then keeps the fallback. Source: https://web.dev/articles/font-best-practices.
- web.dev: a layout shift occurs when the web font and the fallback take different space. `size-adjust` and the metric overrides reduce it. Source: the same page.
- web.dev: font files must be fetched over CORS, so a hand-written preload needs `crossorigin`. Source: the same page.
- web.dev: "Use only WOFF2 and forget about everything else." Source: the same page, quote of Bram Stein.

### The fallback metrics

Next.js holds the metrics of both fonts in `node_modules/next/dist/server/capsize-font-metrics.json`. The formula in `font-utils.js` gives these values over Arial:

| Font | size-adjust | ascent-override | descent-override | line-gap-override |
| --- | --- | --- | --- | --- |
| Space Grotesk | 109.69% | 89.71% | 26.62% | 0.00% |
| JetBrains Mono | 134.59% | 75.79% | 22.29% | 0.00% |

The Space Grotesk values are good. The JetBrains Mono values are poor. Arial is proportional, so a scaled Arial does not keep the columns of numbers in line.

A better fallback for JetBrains Mono is a local monospace font. JetBrains Mono has an advance of 0.600 em (`xWidthAvg` 600 of 1000). Courier New has 0.600 em (1229 of 2048). So `size-adjust: 100%` matches the width. The vertical overrides come from JetBrains Mono: `ascent-override: 102%`, `descent-override: 30%`, `line-gap-override: 0%`.

Set `adjustFontFallback: false` on the JetBrains Mono call. Then write one fallback `@font-face`, for example "JetBrains Mono Fallback", with `src: local("Menlo"), local("Courier New")` and the overrides above.
Android may have neither font. There the stack falls to the generic `monospace`, with no override. That is a small shift, not a wrong layout. This was not tested on a device.

## 3. The cost in bytes

All files are the `latin` subset as woff2. The Google files come from the Google Fonts CSS2 API with a Chrome user agent, on 2026-11-05. The static files come from Fontsource on jsDelivr, which repackages the Google files. Each size is the byte count of the download.

### Space Grotesk, weights 400, 500, 600, 700

| File | Bytes |
| --- | --- |
| Google variable, `wght@300..700` | 22,320 |
| Google, `wght@400;500;600;700` | 22,320, the same variable file |
| Google, `wght@400..700` | 22,320, the same variable file |
| Fontsource variable | 22,288 |
| Fontsource static 400 | 13,388 |
| Fontsource static 500 | 13,312 |
| Fontsource static 600 | 13,284 |
| Fontsource static 700 | 12,840 |
| Sum of the four static files | 52,824 |

URL: `https://fonts.gstatic.com/s/spacegrotesk/v22/V8mDoQDjQSkFtoMM3T6r8E7mPbF4C_k3HqU.woff2`.

### JetBrains Mono, weights 500, 700, 800

| File | Bytes |
| --- | --- |
| Google variable, full range `wght@100..800` | 40,480 |
| Google, `wght@500..800`, cut by Google | 31,340 |
| Google, `wght@500;700;800` | 31,340, the same cut file |
| Fontsource variable, full range | 40,404 |
| Fontsource static 500 | 21,832 |
| Fontsource static 700 | 21,908 |
| Fontsource static 800 | 21,236 |
| Sum of the three static files | 64,976 |

URL of the cut file: `https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwgknk-4.woff2`.

### Result

- The variable file is smaller in both cases. Space Grotesk: 22,320 against 52,824 bytes. JetBrains Mono: 31,340 against 64,976 bytes.
- Google now serves a variable file even for a list of weights. For JetBrains Mono it cuts the weight axis to the range we ask for.
- Two files and 53,660 bytes in all. That is two requests on the first visit and none after, if the cache holds them.
- Each Latin file covers `U+0000-00FF` and some punctuation and symbols. A character outside it shows in the fallback font.

## 4. The licenses

| Font | License | Copyright | Reserved Font Name |
| --- | --- | --- | --- |
| Space Grotesk | SIL Open Font License 1.1 | Copyright 2020 The Space Grotesk Project Authors | none |
| JetBrains Mono | SIL Open Font License 1.1 | Copyright 2020 The JetBrains Mono Project Authors | none |

Sources: https://github.com/google/fonts/blob/main/ofl/spacegrotesk/METADATA.pb, `ofl/spacegrotesk/OFL.txt`, `ofl/jetbrainsmono/METADATA.pb`, and `ofl/jetbrainsmono/OFL.txt` in the same repo. Neither OFL.txt names a Reserved Font Name on its first lines.

What the OFL lets us do. Source: https://openfontlicense.org/open-font-license-official-text/.

- The grant lets anyone "use, study, copy, merge, embed, modify, redistribute, and sell modified and unmodified copies".
- Condition 2: the font may be "bundled, redistributed and/or sold with any software, provided that each copy contains the above copyright notice and this license."
- Condition 3: a Modified Version may not use a Reserved Font Name. Neither font has one, so a subset may keep its name.
- Condition 5: the font stays under the OFL. A document made with the font does not.

So self-host is allowed. The repo is public, so it distributes the files. Keep the `OFL.txt` of each font next to its woff2 file in the repo.

## 5. Recommendation

Use `next/font/local` with the two variable files.

1. Put the files in the look, not in a client. Ticket 01 moves the fonts out of the brand, so one copy serves both clients.
2. Download the two Google Latin files above. Commit each with its `OFL.txt`.
3. Make one fonts file that calls `localFont` twice, with `variable` set to a CSS variable, and import it in the root layout.
4. Space Grotesk: `weight: "300 700"`, `display: "swap"`, `preload: true`, and the default Arial fallback.
5. JetBrains Mono: `weight: "500 800"`, `display: "swap"`, `preload: true`, and `adjustFontFallback: false`. Add the monospace fallback face from section 2.

### Why this method

- It loads from our own origin, with no request to Google at build time or at run time. That keeps the intent of the existing test.
- Next.js writes the preload tags, the fallback face of Space Grotesk, and hashed file names under `_next/static/media/`. The hash lets the files cache for a long time with no stale copy.
- It needs less code than the own `@font-face` path. That path needs a hand-written preload and hand-written fallback faces.
- `next/font/google` fetches from Google on each build of each client and in CI. A Google outage then fails the build.
- A CSS link to Google adds a third-party connection and a render-blocking stylesheet. The phones of our readers pay that cost on each first visit.
- `swap` matches the current code and the Next.js default. With the metric overrides the swap moves very little.

### Cost of this method

- The test "load from no outside host" in `brand-tokens.test.ts` fails, because it bans the text `next/font`. Change its pattern to ban `next/font/google` and keep the other host bans.
- `brandCss` and the `faces` copy in `client-build.mjs` may become dead code. Ticket 01 decides that.

### Checks to add

1. A byte budget test in vitest. It reads each woff2 file in the fonts folder and checks that its first four bytes are `wOF2`. It fails if Space Grotesk is over 24,000 bytes, JetBrains Mono over 33,000 bytes, or the sum over 56,000 bytes.
2. A count test. The fonts folder holds exactly two woff2 files, so a new weight or font needs a choice.
3. An export check in `check-export.mjs`. Each `index.html` has exactly two `rel="preload"` links with `as="font"`. `out/_next/static/media/` holds exactly two woff2 files, each under the same budget.
4. The changed host test. No source file names `next/font/google`, `fonts.googleapis`, `fonts.gstatic`, `use.typekit`, or a remote `url(`.
5. A license test. Each woff2 file in the fonts folder has an `OFL.txt` next to it.

## Not checked

- No build of the site with `next/font/local` ran in this repo. The first spec ticket must build both clients and run `check:export`.
- The fallback of JetBrains Mono was not tested on iOS or Android.
- The cache headers that the Cloudflare Worker sends for `_next/static/media/` were not checked.
- The layout shift was not measured. A Lighthouse run on a phone profile, before and after, can measure it.
