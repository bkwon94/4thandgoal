/**
 * Tests of the brand: the formula of each derived role, an override, the paint order of the two sets, and the contrast.
 * Each test reads the brand CSS or the colors that a real brand gives.
 */
import { describe, expect, it } from "vitest";
import { brandCss, colorsOf, contrastRatio, setsOf, textPairsOf, type BrandFile, type ColorSet } from "./brand";

const LIGHT: ColorSet = {
  accent: "#1d4ed8",
  band: "#0b1020",
  page: "#ffffff",
  card: "#eef1f6",
  raised: "#e2e6ee",
  text: "#111111",
  muted: "#555555",
  grid: "#161c30",
};

const DARK: ColorSet = {
  accent: "#2f6fe4",
  band: "#0b1020",
  page: "#0b1020",
  card: "#151b2e",
  raised: "#1d2540",
  text: "#f2f4f8",
  muted: "#a3acbf",
  grid: "#161c30",
};

/* A brand with both sets. A test overrides one set. */
function brand(sets: Partial<BrandFile> = {}): BrandFile {
  return { light: LIGHT, dark: DARK, ...sets };
}

/* The value of one custom property in a block of the brand CSS. */
function declared(css: string, block: "@theme static" | ".dark", token: string): string | undefined {
  const start = css.indexOf(`${block} {`);
  if (start < 0) return undefined;
  const body = css.slice(start, css.indexOf("}", start));
  return body.match(new RegExp(`--${token}: ([^;]+);`))?.[1];
}

const css = (file: BrandFile) => brandCss(file, { source: "clients/test/brand.toml" });

describe("the derived roles", () => {
  it("take the formula of the design package when the brand gives no override", () => {
    const text = css(brand());
    expect(declared(text, "@theme static", "color-ink-2")).toBe("color-mix(in srgb, var(--color-ink) 85%, var(--color-page))");
    expect(declared(text, "@theme static", "color-accent-ink")).toBe("var(--color-accent)");
    expect(declared(text, "@theme static", "color-card-band")).toBe("var(--color-band)");
    expect(declared(text, "@theme static", "color-on-dark-2")).toBe("color-mix(in srgb, var(--color-on-dark) 80%, var(--color-band))");
  });

  it("take the light page as the on-dark text in both sets", () => {
    expect(declared(css(brand()), "@theme static", "color-on-dark")).toBe("#ffffff");
    expect(declared(css(brand()), ".dark", "color-on-dark")).toBe("#ffffff");
  });

  it("take the override of the brand, as a hex or as a mix", () => {
    const light: ColorSet = { ...LIGHT, derived: { rule: "#dddddd", divider: { mix: "accent", percent: 15, over: "card" } } };
    const text = css(brand({ light }));
    expect(declared(text, "@theme static", "color-rule")).toBe("#dddddd");
    expect(declared(text, "@theme static", "color-divider")).toBe("color-mix(in srgb, var(--color-accent) 15%, var(--color-card))");
  });

  it("mix in srgb as the browser does", () => {
    const colors = colorsOf(brand(), "light");
    // ink-2 is #111111 85% over #ffffff: 0.85 * 17 + 0.15 * 255 = 52.7 in each channel.
    expect(colors.ink_2.slice(0, 3).map((c) => Math.round(c * 255 * 10) / 10)).toEqual([52.7, 52.7, 52.7]);
  });
});

describe("the sets of a brand", () => {
  it("paints the light set in @theme and the dark set under .dark, so each dark: variant stays (ADR 0007)", () => {
    const file = brand();
    expect(setsOf(file)).toEqual(["light", "dark"]);
    expect(declared(css(file), "@theme static", "color-page")).toBe("#ffffff");
    expect(declared(css(file), ".dark", "color-page")).toBe("#0b1020");
  });

  it("writes the raised surface and the grid lines of the look in each set", () => {
    expect(declared(css(brand()), "@theme static", "color-raised")).toBe("#e2e6ee");
    expect(declared(css(brand()), ".dark", "color-raised")).toBe("#1d2540");
    expect(declared(css(brand()), ".dark", "color-grid")).toBe("#161c30");
  });

  it("writes no font and no radius, because the look owns them", () => {
    expect(css(brand())).not.toMatch(/--(font|radius)-|@font-face/);
  });
});

describe("the contrast", () => {
  it("gives 21 for black on white and 1 for one color on itself", () => {
    expect(contrastRatio([0, 0, 0, 1], [1, 1, 1, 1])).toBeCloseTo(21, 5);
    expect(contrastRatio([0.5, 0.5, 0.5, 1], [0.5, 0.5, 0.5, 1])).toBe(1);
  });

  it("finds a text pair under 4.5 to 1", () => {
    const pale: ColorSet = { ...LIGHT, muted: "#bbbbbb" };
    const failed = textPairsOf(brand({ light: pale }), "light").filter((pair) => pair.ratio < 4.5);
    expect(failed.map((pair) => `${pair.text} on ${pair.surface}`)).toContain("muted on page");
  });
});
