/**
 * The contrast test of the brands (AT-17). It reads each brand.toml under clients/ and lists each text pair of each set.
 * Each pair must reach 4.5 to 1 (WCAG AA). Each brand gives both sets, so each pair runs in the light and the dark set.
 */
// @vitest-environment node
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
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

describe("the contrast of each text pair of each brand (AT-17)", () => {
  const slugs = brandSlugs(REPO_ROOT);

  it("finds the brand of cpc", () => {
    expect(slugs).toContain("cpc");
  });

  it.each(slugs)("lists each text pair of %s at 4.5 or more", (slug) => {
    const pairs = pairLines(REPO_ROOT, slug);
    // The output lists each pair, so the evidence of AT-17 is the command and its output.
    console.log(pairs.map(({ line }) => line).join("\n"));
    expect(pairs.length).toBe(TEXT_PAIRS.length * 2);
    expect(pairs.filter(({ ratio }) => ratio < AA).map(({ line }) => line)).toEqual([]);
  });

  /* The pairs of the look: the text on the raised surface and the accent text on the card, and the hero pairs on the
     band, which stays dark in both themes. */
  const LOOK_PAIRS = [
    "text on raised",
    "ink_2 on raised",
    "muted on raised",
    "accent_ink on card",
    "on_dark on band",
    "on_dark_2 on band",
    "on_dark_muted on band",
    "accent_text on band",
  ];

  it.each(slugs)("holds the pairs of the look and the hero pairs of %s in the light and the dark set", (slug) => {
    const lines = pairLines(REPO_ROOT, slug).map(({ line }) => line.replace(/ [0-9.]+$/, ""));
    for (const set of ["light", "dark"]) {
      for (const pair of LOOK_PAIRS) expect(lines).toContain(`${slug} ${set}: ${pair}`);
    }
  });
});
