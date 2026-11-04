/**
 * Holds the color tokens of globals.css to their role names and to the CPC values.
 * A token keeps its value through a rename, so the CPC look does not change (AT-8).
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const CSS = readFileSync(join(process.cwd(), "src/app/globals.css"), "utf8");

/* The CSS with comments and the shadcn mapping block removed, so only the brand tokens and the shadcn values stay. */
function declarations(block: string): Map<string, string> {
  const map = new Map<string, string>();
  for (const [, name, value] of block.matchAll(/(--[a-z0-9-]+):\s*([^;]+);/g)) map.set(name, value.trim());
  return map;
}

/* Cut the text of the block that starts at the opener, by brace depth. */
function blockAt(css: string, opener: RegExp): string {
  const start = css.search(opener);
  if (start < 0) return "";
  const open = css.indexOf("{", start);
  let depth = 0;
  for (let i = open; i < css.length; i++) {
    if (css[i] === "{") depth++;
    if (css[i] === "}" && --depth === 0) return css.slice(open + 1, i);
  }
  return "";
}

function resolve(value: string, map: Map<string, string>): string {
  return value.replace(/var\((--[a-z0-9-]+)\)/g, (_, name: string) => resolve(map.get(name) ?? `MISSING(${name})`, map));
}

const stripped = CSS.replace(/\/\*[\s\S]*?\*\//g, "");
const withoutInline = stripped.replace(blockAt(stripped, /@theme inline/), "");
const darkBlock = blockAt(withoutInline, /\.dark\s*\{/);
const lightMap = declarations(withoutInline.replace(darkBlock, ""));
const darkMap = new Map([...lightMap, ...declarations(darkBlock)]);

function value(theme: "light" | "dark", token: string): string {
  const map = theme === "light" ? lightMap : darkMap;
  return resolve(map.get(`--color-${token}`) ?? `MISSING(${token})`, map);
}

/* The resolved value of each color token before the rename, light and dark. The key is the new name. */
const CPC: Record<string, [string, string]> = {
  "accent": ["#b8342a", "#b8342a"],
  "band": ["#141414", "#141414"],
  "card": ["#ececec", "#1f1f1f"],
  "page": ["#fff", "#141414"],
  "accent-text": ["#f2a59e", "#f2a59e"],
  "accent-ink": ["#b8342a", "#f2a59e"],
  "accent-glow": ["color-mix(in srgb, #b8342a 45%, transparent)", "color-mix(in srgb, #b8342a 45%, transparent)"],
  "card-band": ["#141414", "#262626"],
  "ink": ["#1a1a1a", "#fff"],
  "ink-2": ["#333", "#ccc"],
  "mute": ["#666", "#999"],
  "rule": ["#e3e3e3", "#333"],
  "bar-off": ["#cfcfcf", "#777"],
  "divider": ["#cfcfcf", "#555"],
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
    expect(value("light", token)).toBe(light);
    expect(value("dark", token)).toBe(dark);
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

function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return sourceFiles(path);
    return /\.(css|tsx?|md)$/.test(entry.name) ? [path] : [];
  });
}
