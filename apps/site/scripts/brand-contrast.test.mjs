/**
 * The contrast test of the brands (AT-17). It reads each brand.toml under clients/ and lists each text pair of each set.
 * Each pair must reach 4.5 to 1 (WCAG AA). A temp dark brand with one set shows that a one-set brand is checked too.
 */
// @vitest-environment node
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { setsOf, TEXT_PAIRS, textPairsOf } from "@cpc/design/brand/brand.ts";
import { readBrand, REPO_ROOT } from "./client-build.mjs";

/* WCAG AA for body text. */
const AA = 4.5;

/* Each client folder under `root` with a brand.toml. A new client, such as norcal, joins the test when its folder exists. */
function brandSlugs(root) {
  const clients = join(root, "clients");
  return readdirSync(clients)
    .filter((name) => existsSync(join(clients, name, "brand.toml")))
    .sort();
}

/* One line per text pair of each set of the brand: the slug, the set, the pair, and the ratio. */
function pairLines(root, slug) {
  const brand = readBrand(root, slug);
  return setsOf(brand).flatMap((set) =>
    textPairsOf(brand, set).map(({ text, surface, ratio }) => ({
      line: `${slug} ${set}: ${text} on ${surface} ${ratio.toFixed(2)}`,
      ratio,
    })),
  );
}

/* A dark brand with one set, in a temp repo. Its colors are those of a dark site with a blue accent. */
const DARK_ONE_SET = `radius_card = "6px"
radius_small = "2px"

[fonts]
body = "Inter, sans-serif"
heading = "Inter, sans-serif"

[dark]
accent = "#1f5fbf"
band = "#0b1020"
page = "#0b1020"
card = "#151b2e"
text = "#f2f4f8"
muted = "#a3acbf"

[dark.derived]
accent_text = "#8fb4ff"
accent_ink = "#8fb4ff"
`;

const temp = mkdtempSync(join(tmpdir(), "brand-contrast-"));
afterAll(() => rmSync(temp, { recursive: true, force: true }));

describe("the contrast of each text pair of each brand (AT-17)", () => {
  const slugs = brandSlugs(REPO_ROOT);

  it("finds the brand of cpc", () => {
    expect(slugs).toContain("cpc");
  });

  it.each(slugs)("lists each text pair of %s at 4.5 or more", (slug) => {
    const pairs = pairLines(REPO_ROOT, slug);
    // The output lists each pair, so the evidence of AT-17 is the command and its output.
    console.log(pairs.map(({ line }) => line).join("\n"));
    expect(pairs.length).toBe(TEXT_PAIRS.length * setsOf(readBrand(REPO_ROOT, slug)).length);
    expect(pairs.filter(({ ratio }) => ratio < AA).map(({ line }) => line)).toEqual([]);
  });

  it("lists each text pair of a dark brand with one set at 4.5 or more", () => {
    mkdirSync(join(temp, "clients", "dark"), { recursive: true });
    writeFileSync(join(temp, "clients", "dark", "brand.toml"), DARK_ONE_SET);
    const pairs = pairLines(temp, "dark");
    console.log(pairs.map(({ line }) => line).join("\n"));
    expect(pairs.length).toBe(TEXT_PAIRS.length);
    expect(pairs.every(({ line }) => line.startsWith("dark dark:"))).toBe(true);
    expect(pairs.filter(({ ratio }) => ratio < AA).map(({ line }) => line)).toEqual([]);
  });
});
