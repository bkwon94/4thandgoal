# 01 notes: how the brand schema drops the fonts and the radii

Ticket: `01-research-brand-schema-drops-fonts.md`. Map: `../MAP.md`.
Worktree: `.claude/worktrees/site-redesign`, branch `site-redesign`. Each source is a file of this repo, read on 2026-11-05.
Each line number is the line in that file now.

## Summary

- Only the site build and the design package read `fonts`, `radius_card`, and `radius_small`. The pipeline and the API do not read `brand.toml` at all.
- The brand CSS writes four tokens from the brand: `--font-sans`, `--font-heading`, `--radius-sm`, `--radius-card`. About 30 component files use them through `rounded-card`, `rounded-sm`, `font-sans`, `font-heading`, and the shadcn `--radius` scale. The class names can stay. Only the source of the four values moves.
- The rule "both sets required" breaks more checks than the fonts do. It also collides with ADR 0007, which says light is the default. The map says dark is the default.
- Recommendation: move the four tokens into the `@theme static` block of `apps/site/src/app/globals.css`, beside the spacing and type tokens of the look. Move the font-face code out of `brand.ts`. Decision 02 decides where the font files live.

## 1. The readers of `fonts`, `radius_card`, and `radius_small`

A search with `git grep` over `packages`, `apps`, `clients`, `scripts`, and `docs/adr` found these readers.
The search found no reader in `apps/pipeline`, `apps/api`, or any `packages/*/python`.

### The values

- `clients/cpc/brand.toml:1` the header comment names "the two radii, the two font stacks".
- `clients/cpc/brand.toml:4-11` `radius_card = "8px"`, `radius_small = "3px"`, and the `[fonts]` table with `body` and `heading` set to `"Helvetica Neue", Arial, sans-serif`.
- `clients/norcal/brand.toml:1` the header comment names the radii and the font stacks.
- `clients/norcal/brand.toml:4-10` `radius_card = "4px"`, `radius_small = "2px"`, and `[fonts]` with the `system-ui` stack.
- `clients/norcal/brand.toml:12` the comment "No [light] table: one dark set, no theme button."
- No client has `assets/fonts/`. `clients/cpc/assets/` holds only `logo.png`. `clients/norcal/` has no `assets/`.

### The design package

- `packages/design/site/brand/brand.ts:45-46` the type `FontFace`.
- `packages/design/site/brand/brand.ts:49-55` the type `BrandFile`, with `radius_card`, `radius_small`, `fonts`, and the optional `light` and `dark`.
- `packages/design/site/brand/brand.ts:127-144` `FONT_FORMAT`, `FONT_PATH = "/brand/fonts/"`, and `fontFaceText`, which writes each `@font-face`.
- `packages/design/site/brand/brand.ts:147-165` `brandCss`. It takes `faces`, writes the `@font-face` blocks, and writes `--font-sans`, `--font-heading`, `--radius-sm`, and `--radius-card` at lines 158-161.
- `packages/design/site/brand/brand.ts:276-313` `BRAND_SCHEMA`, with the three keys in `required` and in `properties`.
- `packages/design/site/brand/README.md:7-8` the README names the fonts, the radii, and the `@font-face` of each font file.
- `packages/design/README.md:9` names the brand schema. It does not name the fonts, so it can stay.

### The site build

- `apps/site/scripts/client-build.mjs:12` imports `FONT_PATH` from the design package.
- `apps/site/scripts/client-build.mjs:281-296` `copyAssets` reads `brand.fonts.faces`, checks each file in `clients/<slug>/assets/fonts/`, and copies it to `public/brand/fonts/`.
- `apps/site/scripts/client-build.mjs:339-342` `buildClient` passes `brand.fonts.faces` to `brandCss`.

### The site styles

- `apps/site/src/app/globals.css:2-3` the file comment says the brand adds "the color roles, the fonts, and the radii".
- `apps/site/src/app/globals.css:8` the comment on the import of `../generated/brand.css` says the same.
- `apps/site/src/app/globals.css:36-37` the comment in `@theme static` says the same.
- `apps/site/src/app/globals.css:213-218` the shadcn radius scale `--radius-md` to `--radius-4xl`, from `--radius`.
- `apps/site/src/app/globals.css:248` `--radius: var(--radius-card);`.
- `apps/site/src/app/globals.css:349` `html { @apply font-sans; }`.

### The users of the tokens in components

These files read the tokens through a utility class. They need no change if the token names stay.

- `rounded-card`: 19 files. They are under `packages/analyzer/site/form/`, `packages/managers/site/page/`, `packages/rankings/site/chapters/power-rankings.tsx`, `packages/waiver/site/`, and `packages/week/site/chapters/`.
- `rounded-sm`: `packages/analyzer/site/form/analyze-result.tsx:153`, `teams-skeleton.tsx:19,37`, `trade-form.tsx:145`, `trade-side.tsx:49,111`, `packages/design/site/parts/tag.tsx:13`, `packages/waiver/site/war-chest.tsx:70,73`, `packages/week/site/chapters/median-game.tsx:50`.
- `font-heading`: `packages/design/site/ui/dialog.tsx:137`.
- `--radius-md`: `packages/design/site/ui/select.tsx:47`, through the shadcn scale.

### The tests

- `packages/design/site/brand/brand.test.ts:27` the fixture `brand()` sets `radius_card`, `radius_small`, and `fonts`.
- `packages/design/site/brand/brand.test.ts:85-97` the test "the fonts of a brand".
- `apps/site/scripts/brand-contrast.test.mjs:36-42` the fixture `DARK_ONE_SET` has the radii and `[fonts]`.
- `apps/site/scripts/client-build.test.mjs:297` expects `--radius-card: 8px;` in the brand CSS.
- `apps/site/scripts/client-build.test.mjs:361-377` two tests of `[[fonts.faces]]`: the copy of a font file, and the failure on a missing file.
- `apps/site/src/app/brand-tokens.test.ts:90-96` the test "keeps the CPC fonts and radii".
- `apps/site/src/app/brand-tokens.test.ts:118-128` the test "the fonts of the site" bans `next/font` and remote font hosts. It reads no brand key.

## 2. `BRAND_SCHEMA` now, and the proposed shape

### Now

Source: `packages/design/site/brand/brand.ts:276-313`.

```ts
export const BRAND_SCHEMA = {
  $schema: "http://json-schema.org/draft-07/schema#",
  title: "brand.toml",
  type: "object",
  additionalProperties: false,
  required: ["radius_card", "radius_small", "fonts"],
  anyOf: [{ required: ["light"] }, { required: ["dark"] }],
  properties: {
    radius_card: CSS_TEXT,
    radius_small: CSS_TEXT,
    fonts: { /* body, heading, and faces[] of { family, file, weight, style } */ },
    light: COLOR_SET,
    dark: COLOR_SET,
  },
};
```

`COLOR_SET` (lines 258-272) requires the six base roles and allows `derived` overrides. Keep it as it is.

### Proposed

```ts
/* The JSON Schema of brand.toml. Each brand gives both sets. A missing set, a missing base role, an unknown role, or an unknown key fails. */
export const BRAND_SCHEMA = {
  $schema: "http://json-schema.org/draft-07/schema#",
  title: "brand.toml",
  type: "object",
  additionalProperties: false,
  required: ["light", "dark"],
  properties: {
    light: COLOR_SET,
    dark: COLOR_SET,
  },
};

export type BrandFile = { light: ColorSet; dark: ColorSet };
```

- `additionalProperties: false` stays. An old `brand.toml` with `radius_card` or `[fonts]` then fails with "is not a known key". That failure is the guard against a stale file.
- `CSS_TEXT` (line 273) has no other user after the change. Remove it.
- `FontFace`, `FONT_FORMAT`, `FONT_PATH`, and `fontFaceText` leave `brand.ts`. See section 4.
- `brandCss(brand, { source })` loses the `faces` option and the four lines 158-161.
- The logo is not in `brand.toml`. It is `clients/<slug>/assets/logo.*` (`client-build.mjs:119`). The copy is `copy.toml`. So `brand.toml` holds only the two color sets. No schema change is necessary for the logo or the copy.

### The other code that "both sets required" changes

- `setsOf` (`brand.ts:95-97`) always gives two sets. The paint order must follow the map: dark first. The comment cites ADR 0007, which says light first.
- `onDark` (`brand.ts:90-92`) has a branch for a brand with no light set. That branch then never runs. Remove it, or keep it only if the look changes the `on_dark` formula.
- `brandCss` puts the first set in `@theme static` and the second under `.dark`. With dark as the default, there are two choices. One: keep `.dark` as the override, and put the class on `<html>` at build time. Then the boot script removes it for a stored light choice. Two: put the dark set in `@theme static` and the light set under a `.light` block. The second choice inverts ADR 0007 and every `dark:` variant in components. The first choice keeps each `dark:` class. Decision 03 or the spec must pick one.
- `packages/design/site/lib/theme.ts:27` `BOOT_SCRIPT` adds the dark class only for a stored `"dark"`. With dark as the default, it must apply the default when no choice is stored.
- `packages/design/site/lib/theme.ts:37-44` `paintOf` keeps branches for a one-set brand. With both sets required, `themeButton` is always true.
- `apps/site/src/app/layout.tsx:18` and `apps/site/src/app/globals.css:258,262` hold comments on a one-set brand and on light as the default.
- `apps/site/scripts/check-export.mjs:96-99` checks the theme button by the count of sets. It stays correct, but the "no theme button" branch never runs.
- `clients/norcal/brand.toml` needs a `[light]` set and `[light.derived]` overrides. Decision 09 gives the colors.

## 3. The checks and the tests that break

### The drop of the fonts and the radii

1. `apps/site/src/app/brand-tokens.test.ts:90-96` "keeps the CPC fonts and radii". It reads the four tokens from `brandCss` plus `globals.css`. Change the test to read the look values from `globals.css`. Rename it, for example "keeps the fonts and the radii of the look". The new values come from decision 03.
2. `apps/site/src/app/brand-tokens.test.ts:13` calls `brandCss(BRAND, { source, faces: [] })`. Remove `faces` when the option goes.
3. `packages/design/site/brand/brand.test.ts:27` the fixture `brand()`. Remove the three keys. The fixture must then give both sets, so the type `Partial<Pick<...>>` changes.
4. `packages/design/site/brand/brand.test.ts:38,87-90` the calls with `faces`. Remove the option.
5. `packages/design/site/brand/brand.test.ts:85-97` "the fonts of a brand". Move it to the test of the module that writes the `@font-face`, or remove it if decision 02 drops font files.
6. `apps/site/scripts/client-build.test.mjs:297` `--radius-card: 8px;`. Remove the line, or change it to expect no `--radius` token in the brand CSS.
7. `apps/site/scripts/client-build.test.mjs:361-377` the two tests of `[[fonts.faces]]`. Replace them with one test: a `brand.toml` with `radius_card` or `[fonts]` fails with "is not a known key" and names the file.
8. `apps/site/scripts/brand-contrast.test.mjs:36-42` `DARK_ONE_SET` has the radii and `[fonts]`. The schema then rejects it. Remove the keys.
9. The type check of `client-build.mjs`, if one runs, fails on `brand.fonts` at lines 288 and 341. Remove the font loop from `copyAssets` and the `faces` argument.

### The rule "both sets required"

10. `packages/design/site/brand/brand.test.ts:50-53` the case "the text of a dark set with no light set". Remove the one-set half.
11. `packages/design/site/brand/brand.test.ts:70-75` "paints a two-set brand light first". Change it to the new paint order.
12. `packages/design/site/brand/brand.test.ts:77-83` "paints a brand with one dark set dark, with no .dark block". Replace it with a test that a one-set brand fails the schema.
13. `apps/site/scripts/brand-contrast.test.mjs:73-81` "lists each text pair of a dark brand with one set". `DARK_ONE_SET` fails the schema. Give the fixture both sets, or remove the test, because the `it.each` over real clients already covers both brands.
14. `apps/site/scripts/client-build.test.mjs:290-299` "the light set first, then the dark set under .dark". Change it to the new paint order.
15. `apps/site/scripts/client-build.test.mjs:324-334` "writes the sets of the brand" expects `["light", "dark"]`. Change the order if `setsOf` changes.
16. `apps/site/scripts/client-build.test.mjs:336-345` "gives a brand with one dark set the dark set first and no .dark block (AT-10)". Replace it with a test that a brand with one set fails and names the missing set.
17. `packages/design/site/lib/theme.test.ts:21-36` the boot script tests assume light as the default. Change them for dark as the default.
18. `packages/design/site/lib/theme.test.ts:48-57` the `paintOf` tests of a one-set brand, AT-10 among them. Remove the one-set cases.
19. `apps/site/scripts/check-export.mjs:96-99` fails for NorCal after it gains a light set, until the NorCal export shows the theme button. That is the wanted result.

### Acceptance tests of the old spec

- `.scratch/clients/ACCEPTANCE.md:83` AT-10 "NorCal has no theme button". The map reverses it. The new `ACCEPTANCE.md` must replace it.
- `.scratch/clients/ACCEPTANCE.md:139` AT-17 "Each text pair of each brand passes WCAG AA". It still holds. It then runs on four sets, not three.

### Checks that do not break

- `apps/site/src/app/brand-tokens.test.ts:118-128` bans `next/font` and remote font hosts. It reads no brand key. It breaks only if decision 02 picks `next/font/local`. That decision must then change the pattern.
- `apps/site/src/app/brand-tokens.test.ts:84-88` the color values of CPC. It still holds. The dark column changes only if the CPC dark set changes.

## 4. Where the fonts and the radii of the look live

### Options

- **A. `apps/site/src/app/globals.css`, in its `@theme static` block.** This file already holds the tokens of the look that no brand sets: the spacing scale (lines 47-55), the fixed sizes, and the type scale (lines 148-154, with tier overrides at lines 330-344). Its comment says "Every other hex color and pixel size lives here." The four tokens become fixed lines, for example `--font-sans`, `--font-heading`, `--radius-sm`, `--radius-card`.
- **B. A token file in the design package**, for example `packages/design/site/look/look.css`, imported by `globals.css`. It puts the look beside the components that use it.
- **C. A TypeScript module in the design package** that `brandCss` or a second generator writes into `src/generated/`. It adds a generator for values that never change per client.

### Recommendation: A, with the font-face code in the design package

- The value is the same for every client, so no generator is necessary. A fixed CSS line is the simplest form.
- `globals.css` already owns the spacing and the type scale of the look. One place for every look token is one place to read. Option B splits the tokens of the look over two files, unless the spacing and the type scale move too. That move is a larger change with no gain for this spec.
- `brand-tokens.test.ts` already reads `globals.css`, so test 1 above needs only a new source and new values.
- Tailwind keeps each utility, because `@theme static` makes `rounded-card`, `rounded-sm`, `font-sans`, and `font-heading` from the tokens. No component file changes.
- Option B is a good later step if a second app ever uses the look. Today one site app serves every client.

For the font files:

- If decision 02 picks self-hosted files, keep them in one place for every client, not in `clients/<slug>/assets/fonts/`. Two places fit: `apps/site/public/fonts/`, which the export serves with no copy step, or `packages/design/site/look/fonts/` with a copy step in `client-build.mjs`.
- Move `fontFaceText` and `FONT_PATH` with the files, or write the `@font-face` blocks as fixed CSS in `globals.css`. Fixed CSS is the simplest, because the faces do not change per client.
- Decision 02 owns this choice. Do not fix it in this ticket.

## 5. The ADRs that the change touches

- **ADR 0006** `docs/adr/0006-report-look-at-every-width.md:3`. It fixes "the black masthead, the red accents, Helvetica, and the type and color tokens" at every width, and rejects "a full new design". The redesign is a full new design and moves the fonts to the look. Supersede ADR 0006 with a new ADR on the look.
- **ADR 0007** `docs/adr/0007-dark-theme-is-one-override-block.md:3,7`. Line 7 says "Light is the default" and "The export ships no theme class". The map makes dark the default for every client. Supersede line 7 at least. Line 3 can hold if the spec keeps the `.dark` override block and puts the class on `<html>` at build time. Line 9 already names `card-blk`, an old token name, so the ADR is stale there too.
- **ADR 0022** `docs/adr/0022-a-client-is-one-root-folder-that-both-apps-read.md:10,13`. Line 10 says `brand.toml` holds "the color roles, the fonts, and the radii". Line 13 says `assets/` holds "the logo, the favicon, the fonts". Change both lines: `brand.toml` holds the light and the dark color set, and `assets/` holds the logo and the favicon.
- **ADR 0023** `docs/adr/0023-a-package-holds-one-domain-in-both-languages.md:15-16,26-27`. It puts the primitives, the parts, and the shell in the design package. It does not break. If the spec picks option B or puts the font files in `packages/design`, the look fits the design package as this ADR says. No change is necessary.
- `GLOSSARY.md:908-914` already defines **Brand** with "a light set and a dark set" and **Look** with the fonts and the radii. It agrees with the proposed shape. No change is necessary.

## Open points for the spec

1. The paint order and the class strategy for dark as the default: keep `.dark` with a build-time class, or invert to `.light`.
2. The values of the fonts and the radii of the look. Decision 03 gives them.
3. The font files and their loader. Decision 02 gives them.
4. The NorCal light set. Decision 09 gives it.
