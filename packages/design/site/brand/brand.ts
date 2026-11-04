/**
 * The brand of a client: the JSON Schema of brand.toml and copy.toml, the formula of each derived role, and the brand CSS.
 * The client build checks the files with the schemas and writes the CSS. The contrast test reads the colors of each set.
 */

/* The six roles that each set must give. */
export const BASE_ROLES = ["accent", "band", "page", "card", "text", "muted"] as const;
export type BaseRole = (typeof BASE_ROLES)[number];

/* The roles that derive from the base roles. A brand can override each one under [light.derived] or [dark.derived]. */
export const DERIVED_ROLES = [
  "accent_text",
  "accent_ink",
  "accent_glow",
  "pick",
  "card_band",
  "ink_2",
  "rule",
  "divider",
  "bar_off",
  "on_dark",
  "on_dark_2",
  "on_dark_muted",
  "rule_dark",
  "chip_dark",
] as const;
export type DerivedRole = (typeof DERIVED_ROLES)[number];
export type Role = BaseRole | DerivedRole;

/* The two sets of a brand. A brand gives one of them or both. */
export const SETS = ["light", "dark"] as const;
export type SetName = (typeof SETS)[number];

/* A color as a hex value, such as #b8342a. */
export type Hex = string;

/* One color mixed over a second color, as CSS color-mix in srgb: `percent` of `mix`, the rest of `over`. */
export type Mix = { mix: Role; percent: number; over: Role | "transparent" };

/* The value of a derived role: a hex, the value of a second role, or a mix. */
export type Formula = Hex | { role: Role } | Mix;

export type ColorSet = Record<BaseRole, Hex> & { derived?: Partial<Record<DerivedRole, Hex | Mix>> };

/* One font file of assets/fonts/. The build copies it into the site and writes its @font-face. */
export type FontFace = { family: string; file: string; weight?: string; style?: "normal" | "italic" };

/* The values of brand.toml, after the check. */
export type BrandFile = {
  radius_card: string;
  radius_small: string;
  fonts: { body: string; heading: string; faces?: FontFace[] };
  light?: ColorSet;
  dark?: ColorSet;
};

/* The values of copy.toml, after the check. */
export type CopyFile = { site_name: string; masthead: string; tagline: string };

/* The CSS token of each role. `ink` and `mute` keep their names, so the text roles map to them. */
const TOKEN: Record<Role, string> = {
  accent: "accent",
  band: "band",
  page: "page",
  card: "card",
  text: "ink",
  muted: "mute",
  ...(Object.fromEntries(DERIVED_ROLES.map((role) => [role, role.replaceAll("_", "-")])) as Record<DerivedRole, string>),
};

/* The formula of each derived role, for a brand with no override. `on_dark` is not here, because its formula reads the
   light set: see onDark. */
const FORMULA: Record<Exclude<DerivedRole, "on_dark">, Formula> = {
  accent_text: { role: "accent" },
  accent_ink: { role: "accent" },
  accent_glow: { mix: "accent", percent: 45, over: "transparent" },
  pick: { mix: "accent", percent: 10, over: "page" },
  card_band: { role: "band" },
  ink_2: { mix: "text", percent: 85, over: "page" },
  rule: { mix: "text", percent: 10, over: "page" },
  divider: { mix: "text", percent: 20, over: "page" },
  bar_off: { mix: "text", percent: 20, over: "page" },
  on_dark_2: { mix: "on_dark", percent: 80, over: "band" },
  on_dark_muted: { mix: "on_dark", percent: 60, over: "band" },
  rule_dark: { mix: "on_dark", percent: 15, over: "band" },
  chip_dark: { mix: "on_dark", percent: 10, over: "band" },
};

/* The text that sits on a dark band in both themes. It is the page of the light set, else the text of the one dark set. */
function onDark(brand: BrandFile): Formula {
  return brand.light ? brand.light.page : { role: "text" };
}

/* The sets of the brand, in paint order. The first set paints first. A two-set brand paints light first (ADR 0007). */
export function setsOf(brand: BrandFile): SetName[] {
  return SETS.filter((name) => brand[name] !== undefined);
}

/* The formula of each role of one set: each base role is its own hex, and each derived role takes its override or its formula. */
export function formulasOf(brand: BrandFile, name: SetName): Record<Role, Formula> {
  const set = brand[name];
  if (!set) throw new Error(`The brand has no ${name} set.`);
  const formulas = {} as Record<Role, Formula>;
  for (const role of BASE_ROLES) formulas[role] = set[role];
  for (const role of DERIVED_ROLES) {
    formulas[role] = set.derived?.[role] ?? (role === "on_dark" ? onDark(brand) : FORMULA[role]);
  }
  return formulas;
}

function cssVar(role: Role | "transparent"): string {
  return role === "transparent" ? "transparent" : `var(--color-${TOKEN[role]})`;
}

function cssValue(formula: Formula): string {
  if (typeof formula === "string") return formula;
  if ("role" in formula) return cssVar(formula.role);
  return `color-mix(in srgb, ${cssVar(formula.mix)} ${formula.percent}%, ${cssVar(formula.over)})`;
}

/* The color declarations of one set: one CSS custom property per role. */
function colorLines(brand: BrandFile, name: SetName): string[] {
  const formulas = formulasOf(brand, name);
  return [...BASE_ROLES, ...DERIVED_ROLES].map((role) => `    --color-${TOKEN[role]}: ${cssValue(formulas[role])};`);
}

const FONT_FORMAT: Record<string, string> = { woff2: "woff2", woff: "woff", ttf: "truetype", otf: "opentype" };

/* The URL path in the site of a font file. The client build copies each file of assets/fonts/ there. */
export const FONT_PATH = "/brand/fonts/";

function fontFaceText(face: FontFace): string {
  const format = FONT_FORMAT[face.file.split(".").pop() ?? ""] ?? "woff2";
  return [
    "@font-face {",
    `    font-family: ${JSON.stringify(face.family)};`,
    `    src: url("${FONT_PATH}${face.file}") format("${format}");`,
    `    font-weight: ${face.weight ?? "400"};`,
    `    font-style: ${face.style ?? "normal"};`,
    // The text shows in the fallback font at once, so a slow font file never hides the page.
    "    font-display: swap;",
    "}",
  ].join("\n");
}

/*
 * The brand CSS of the site. Its @theme block gives the first set, the fonts, and the radii, so Tailwind makes a utility
 * for each role. A two-set brand adds a .dark block with the dark set, which the theme button turns on (ADR 0007).
 * Each set names every role, so a set never reads a value of the other set.
 */
export function brandCss(brand: BrandFile, { source, faces }: { source: string; faces: FontFace[] }): string {
  const [first, second] = setsOf(brand);
  const lines = [`/* GENERATED by apps/site/scripts/client-build.mjs from ${source}. Do not edit. */`];
  for (const face of faces) lines.push(fontFaceText(face));
  lines.push(
    "@theme static {",
    ...colorLines(brand, first),
    `    --font-sans: ${brand.fonts.body};`,
    `    --font-heading: ${brand.fonts.heading};`,
    `    --radius-sm: ${brand.radius_small};`,
    `    --radius-card: ${brand.radius_card};`,
    "}",
  );
  if (second) lines.push(".dark {", ...colorLines(brand, second), "}");
  return `${lines.join("\n")}\n`;
}

/* An sRGB color with alpha, each channel from 0 to 1. */
export type Rgba = [number, number, number, number];

function hexToRgba(hex: Hex): Rgba {
  const digits = hex.slice(1);
  const long = digits.length === 3 ? [...digits].map((digit) => digit + digit).join("") : digits;
  const [r, g, b] = [0, 2, 4].map((at) => parseInt(long.slice(at, at + 2), 16) / 255);
  return [r, g, b, 1];
}

/* The color of each role of one set, as the browser mixes it: color-mix in srgb, with the alpha premultiplied. */
export function colorsOf(brand: BrandFile, name: SetName): Record<Role, Rgba> {
  const formulas = formulasOf(brand, name);
  const colors = {} as Record<Role, Rgba>;
  const colorOf = (role: Role | "transparent"): Rgba => {
    if (role === "transparent") return [0, 0, 0, 0];
    colors[role] ??= evaluate(formulas[role]);
    return colors[role];
  };
  const evaluate = (formula: Formula): Rgba => {
    if (typeof formula === "string") return hexToRgba(formula);
    if ("role" in formula) return colorOf(formula.role);
    const p = formula.percent / 100;
    const a = colorOf(formula.mix);
    const b = colorOf(formula.over);
    const alpha = a[3] * p + b[3] * (1 - p);
    const channel = (i: number) => (alpha === 0 ? 0 : (a[i] * a[3] * p + b[i] * b[3] * (1 - p)) / alpha);
    return [channel(0), channel(1), channel(2), alpha];
  };
  for (const role of [...BASE_ROLES, ...DERIVED_ROLES]) colorOf(role);
  return colors;
}

function luminance([r, g, b]: Rgba): number {
  const linear = (c: number) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b);
}

/* The WCAG contrast ratio of two opaque colors, from 1 to 21. */
export function contrastRatio(a: Rgba, b: Rgba): number {
  const [light, dark] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (light + 0.05) / (dark + 0.05);
}

/*
 * Each pair of a text role and the surface it sits on in the site. Each pair must reach 4.5 to 1 in each set (WCAG AA).
 * The page text sits on the page, the card, and the pick wash. The on-dark text sits on the band, the black card,
 * the chip of the black card, and the accent fills.
 */
export const TEXT_PAIRS: [text: Role, surface: Role][] = [
  ["text", "page"],
  ["text", "card"],
  ["text", "pick"],
  ["ink_2", "page"],
  ["ink_2", "card"],
  ["muted", "page"],
  ["muted", "card"],
  ["muted", "pick"],
  ["accent_ink", "page"],
  ["accent_ink", "pick"],
  ["on_dark", "band"],
  ["on_dark_2", "band"],
  ["on_dark_muted", "band"],
  ["accent_text", "band"],
  ["on_dark", "card_band"],
  ["on_dark_2", "card_band"],
  ["on_dark_muted", "card_band"],
  ["accent_text", "card_band"],
  ["on_dark", "chip_dark"],
  ["on_dark_2", "chip_dark"],
  ["on_dark_muted", "chip_dark"],
  ["on_dark", "accent"],
];

/* The ratio of each text pair of one set, in the order of TEXT_PAIRS. */
export function textPairsOf(brand: BrandFile, name: SetName): { text: Role; surface: Role; ratio: number }[] {
  const colors = colorsOf(brand, name);
  return TEXT_PAIRS.map(([text, surface]) => ({ text, surface, ratio: contrastRatio(colors[text], colors[surface]) }));
}

const HEX = { type: "string", pattern: "^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$" };
const ROLE_NAMES = [...BASE_ROLES, ...DERIVED_ROLES];
const MIX = {
  type: "object",
  additionalProperties: false,
  required: ["mix", "percent", "over"],
  properties: {
    mix: { enum: ROLE_NAMES },
    percent: { type: "number", minimum: 0, maximum: 100 },
    over: { enum: [...ROLE_NAMES, "transparent"] },
  },
};
const COLOR_SET = {
  type: "object",
  additionalProperties: false,
  required: [...BASE_ROLES],
  properties: {
    ...Object.fromEntries(BASE_ROLES.map((role) => [role, HEX])),
    derived: {
      type: "object",
      additionalProperties: false,
      properties: Object.fromEntries(DERIVED_ROLES.map((role) => [role, { anyOf: [HEX, MIX] }])),
    },
  },
};
const CSS_TEXT = { type: "string", minLength: 1, pattern: "^[^;{}]*$" };

/* The JSON Schema of brand.toml. A missing base role, an unknown role, or an unknown key fails. A brand gives one set or both. */
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
    fonts: {
      type: "object",
      additionalProperties: false,
      required: ["body", "heading"],
      properties: {
        body: CSS_TEXT,
        heading: CSS_TEXT,
        faces: {
          type: "array",
          items: {
            type: "object",
            additionalProperties: false,
            required: ["family", "file"],
            properties: {
              family: { type: "string", minLength: 1, pattern: '^[^"]*$' },
              // A file name in assets/fonts/, with no folder, so a face never points outside the client.
              file: { type: "string", pattern: "^[A-Za-z0-9._-]+\\.(woff2|woff|ttf|otf)$" },
              weight: { type: "string", pattern: "^[0-9]{3}( [0-9]{3})?$" },
              style: { enum: ["normal", "italic"] },
            },
          },
        },
      },
    },
    light: COLOR_SET,
    dark: COLOR_SET,
  },
};

/* The JSON Schema of copy.toml: the site name, the masthead text, and the tagline. */
export const COPY_SCHEMA = {
  $schema: "http://json-schema.org/draft-07/schema#",
  title: "copy.toml",
  type: "object",
  additionalProperties: false,
  required: ["site_name", "masthead", "tagline"],
  properties: {
    site_name: { type: "string", minLength: 1 },
    masthead: { type: "string", minLength: 1 },
    tagline: { type: "string", minLength: 1 },
  },
};
