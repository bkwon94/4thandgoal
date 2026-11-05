/**
 * Holds the color tokens to their role names and to the CPC values, and the fonts and the radii to the look. The colors come
 * from clients/cpc/brand.toml through the brand CSS of the design package, and globals.css adds the tokens that no brand sets (AT-8).
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "smol-toml";
import { describe, expect, it } from "vitest";
import { brandCss, type BrandFile } from "@cpc/design/brand/brand";

const ROOT = join(process.cwd(), "..", "..");
const BRAND = parse(readFileSync(join(ROOT, "clients", "cpc", "brand.toml"), "utf8")) as unknown as BrandFile;
const GLOBALS = readFileSync(join(process.cwd(), "src/app/globals.css"), "utf8");
const CSS = brandCss(BRAND, { source: "clients/cpc/brand.toml" }) + GLOBALS;

function declarations(block: string): Map<string, string> {
  const map = new Map<string, string>();
  for (const [, name, value] of block.matchAll(/(--[a-z0-9-]+):\s*([^;]+);/g)) map.set(name, value.trim());
  return map;
}

/* The text of each block that starts at the opener, by brace depth. */
function blocksAt(css: string, opener: RegExp): string[] {
  const blocks: string[] = [];
  for (const match of css.matchAll(new RegExp(opener, "g"))) {
    const open = css.indexOf("{", match.index);
    let depth = 0;
    for (let i = open; i < css.length; i++) {
      if (css[i] === "{") depth++;
      if (css[i] === "}" && --depth === 0) {
        blocks.push(css.slice(open + 1, i));
        break;
      }
    }
  }
  return blocks;
}

function resolve(value: string, map: Map<string, string>): string {
  return value.replace(/var\((--[a-z0-9-]+)\)/g, (_, name: string) => resolve(map.get(name) ?? `MISSING(${name})`, map));
}

/* A short hex such as #fff and its long form #ffffff are one color, so each hex compares in its long form. */
function longHex(value: string): string {
  return value.toLowerCase().replace(/#([0-9a-f])([0-9a-f])([0-9a-f])(?![0-9a-f])/g, "#$1$1$2$2$3$3");
}

let stripped = CSS.replace(/\/\*[\s\S]*?\*\//g, "");
for (const block of blocksAt(stripped, /@theme inline/)) stripped = stripped.replace(block, "");
const darkBlocks = blocksAt(stripped, /\.dark\s*\{/);
const lightMap = declarations(darkBlocks.reduce((css, block) => css.replace(block, ""), stripped));
const darkMap = new Map([...lightMap, ...darkBlocks.flatMap((block) => [...declarations(block)])]);

function value(theme: "light" | "dark", token: string): string {
  const map = theme === "light" ? lightMap : darkMap;
  return longHex(resolve(map.get(`--color-${token}`) ?? `MISSING(${token})`, map));
}

/* The resolved value of each color token of CPC, light and dark. The key is the token name. */
const CPC: Record<string, [string, string]> = {
  "accent": ["#b8342a", "#b8342a"],
  "band": ["#141414", "#141414"],
  "card": ["#fff", "#1f1f1f"],
  "page": ["#f4f4f4", "#141414"],
  "raised": ["#ebebeb", "#262626"],
  "grid": ["#1c1c1c", "#1c1c1c"],
  "accent-text": ["#f2a59e", "#f2a59e"],
  "accent-ink": ["#a52e25", "#f2a59e"],
  "accent-glow": ["color-mix(in srgb, #b8342a 45%, transparent)", "color-mix(in srgb, #b8342a 45%, transparent)"],
  "card-band": ["#141414", "#262626"],
  "ink": ["#141414", "#fff"],
  "ink-2": ["#3a3a3a", "#ccc"],
  "mute": ["#666", "#999"],
  "rule": ["#e0e0e0", "#333"],
  "bar-off": ["#ddd", "#777"],
  "divider": ["color-mix(in srgb, #141414 20%, #f4f4f4)", "#555"],
  "on-dark": ["#fff", "#fff"],
  "on-dark-2": ["#ccc", "#ccc"],
  "on-dark-muted": ["#999", "#999"],
  "rule-dark": ["#333", "#444"],
  "chip-dark": ["#262626", "#313131"],
  "pick": ["color-mix(in srgb, #b8342a 10%, #fff)", "color-mix(in srgb, #b8342a 22%, #1f1f1f)"],
  "move-up": ["#3987e5", "#3987e5"],
  "move-down": ["#e05a4f", "#e05a4f"],
};

describe("the color tokens of the site", () => {
  it.each(Object.entries(CPC))("%s keeps its CPC value in both themes", (token, [light, dark]) => {
    expect(value("light", token)).toBe(longHex(light));
    expect(value("dark", token)).toBe(longHex(dark));
  });

});

/* The @theme static block of globals.css, where the look keeps its tokens beside the spacing and the type scale. */
const LOOK = declarations(blocksAt(GLOBALS.replace(/\/\*[\s\S]*?\*\//g, ""), /@theme static/)[0] ?? "");

describe("the fonts and the radii of the look", () => {
  it("set Space Grotesk for text and headings and JetBrains Mono for numbers, from the font variables of the root layout", () => {
    expect(LOOK.get("--font-sans")).toBe("var(--font-space-grotesk), Arial, sans-serif");
    expect(LOOK.get("--font-heading")).toBe("var(--font-sans)");
    expect(LOOK.get("--font-mono")).toBe('var(--font-jetbrains-mono), Menlo, "Courier New", monospace');
  });

  it("set 24px for the hero, 20px for a card, 18px for a tile, and a full pill for a button and a bar", () => {
    expect(LOOK.get("--radius-hero")).toBe("24px");
    expect(LOOK.get("--radius-card")).toBe("20px");
    expect(LOOK.get("--radius-tile")).toBe("18px");
    expect(LOOK.get("--radius-pill")).toBe("9999px");
    // rounded-sm paints the tags and the bars, so it takes the pill.
    expect(LOOK.get("--radius-sm")).toBe("var(--radius-pill)");
  });

  it("come from no brand, so each client gets the same look", () => {
    expect(brandCss(BRAND, { source: "clients/cpc/brand.toml" })).not.toMatch(/--(font|radius)-/);
  });
});

/* Lists the files of src with a class or a token of an old color name. The names are built from parts so this file does not match itself. */
const OLD_NAMES = ["re" + "d", "bl" + "k", "gr" + "y", "wh" + "t"];

describe("the source of the site (AT-8)", () => {
  it("has no class or token of the old color names", () => {
    const pattern = new RegExp(`(?<=-)(${OLD_NAMES.join("|")})(?![a-z])`);
    const hits = sourceFiles(join(process.cwd(), "src"))
      .filter((file) => !file.endsWith("brand-tokens.test.ts"))
      .flatMap((file) =>
        readFileSync(file, "utf8")
          .split("\n")
          .map((text, index) => ({ at: `${file}:${index + 1}`, text }))
          .filter(({ text }) => pattern.test(text))
          .map(({ at, text }) => `${at}: ${text.trim()}`),
      );
    expect(hits).toEqual([]);
  });
});

describe("the fonts of the site", () => {
  it("load from no outside host: no next/font, no font service, and no remote url in a stylesheet", () => {
    const pattern = /next\/font|fonts\.googleapis|fonts\.gstatic|use\.typekit|url\(\s*["']?(https?:)?\/\//;
    const dirs = [join(process.cwd(), "src"), join(ROOT, "packages", "design", "site")];
    const hits = dirs
      .flatMap((dir) => sourceFiles(dir))
      .filter((file) => !file.endsWith("brand-tokens.test.ts") && !file.includes("node_modules"))
      .filter((file) => pattern.test(readFileSync(file, "utf8")));
    expect(hits).toEqual([]);
  });
});

function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return sourceFiles(path);
    return /\.(css|tsx?|md)$/.test(entry.name) ? [path] : [];
  });
}
