/**
 * Tests of the brand: the formula of each derived role, an override, the set count, the font faces, and the contrast.
 * Each test reads the brand CSS or the colors that a real brand gives.
 */
import { describe, expect, it } from "vitest";
import { brandCss, colorsOf, contrastRatio, setsOf, textPairsOf, type BrandFile, type ColorSet } from "./brand";

const LIGHT: ColorSet = {
  accent: "#1d4ed8",
  band: "#0b1020",
  page: "#ffffff",
  card: "#eef1f6",
  text: "#111111",
  muted: "#555555",
};

const DARK: ColorSet = {
  accent: "#2f6fe4",
  band: "#0b1020",
  page: "#0b1020",
  card: "#151b2e",
  text: "#f2f4f8",
  muted: "#a3acbf",
};

function brand(sets: Partial<Pick<BrandFile, "light" | "dark">>): BrandFile {
  return { radius_card: "6px", radius_small: "2px", fonts: { body: "Inter, sans-serif", heading: "Inter, sans-serif" }, ...sets };
}

/* The value of one custom property in a block of the brand CSS. */
function declared(css: string, block: "@theme static" | ".dark", token: string): string | undefined {
  const start = css.indexOf(`${block} {`);
  if (start < 0) return undefined;
  const body = css.slice(start, css.indexOf("}", start));
  return body.match(new RegExp(`--${token}: ([^;]+);`))?.[1];
}

const css = (file: BrandFile) => brandCss(file, { source: "clients/test/brand.toml", faces: [] });

describe("the derived roles", () => {
  it("take the formula of the design package when the brand gives no override", () => {
    const text = css(brand({ light: LIGHT }));
    expect(declared(text, "@theme static", "color-pick")).toBe("color-mix(in srgb, var(--color-accent) 10%, var(--color-page))");
    expect(declared(text, "@theme static", "color-ink-2")).toBe("color-mix(in srgb, var(--color-ink) 85%, var(--color-page))");
    expect(declared(text, "@theme static", "color-accent-ink")).toBe("var(--color-accent)");
    expect(declared(text, "@theme static", "color-card-band")).toBe("var(--color-band)");
    expect(declared(text, "@theme static", "color-on-dark-2")).toBe("color-mix(in srgb, var(--color-on-dark) 80%, var(--color-band))");
  });

  it("take the light page as the on-dark text, and the text of a dark set with no light set", () => {
    expect(declared(css(brand({ light: LIGHT, dark: DARK })), ".dark", "color-on-dark")).toBe("#ffffff");
    expect(declared(css(brand({ dark: DARK })), "@theme static", "color-on-dark")).toBe("var(--color-ink)");
  });

  it("take the override of the brand, as a hex or as a mix", () => {
    const light: ColorSet = { ...LIGHT, derived: { rule: "#dddddd", pick: { mix: "accent", percent: 15, over: "card" } } };
    const text = css(brand({ light }));
    expect(declared(text, "@theme static", "color-rule")).toBe("#dddddd");
    expect(declared(text, "@theme static", "color-pick")).toBe("color-mix(in srgb, var(--color-accent) 15%, var(--color-card))");
  });

  it("mix in srgb as the browser does", () => {
    const colors = colorsOf(brand({ light: LIGHT }), "light");
    // ink-2 is #111111 85% over #ffffff: 0.85 * 17 + 0.15 * 255 = 52.7 in each channel.
    expect(colors.ink_2.slice(0, 3).map((c) => Math.round(c * 255 * 10) / 10)).toEqual([52.7, 52.7, 52.7]);
  });
});

describe("the sets of a brand", () => {
  it("paints a two-set brand light first, with the dark set under .dark (ADR 0007)", () => {
    const file = brand({ light: LIGHT, dark: DARK });
    expect(setsOf(file)).toEqual(["light", "dark"]);
    expect(declared(css(file), "@theme static", "color-page")).toBe("#ffffff");
    expect(declared(css(file), ".dark", "color-page")).toBe("#0b1020");
  });

  it("paints a brand with one dark set dark, with no .dark block", () => {
    const file = brand({ dark: DARK });
    expect(setsOf(file)).toEqual(["dark"]);
    expect(declared(css(file), "@theme static", "color-page")).toBe("#0b1020");
    expect(css(file)).not.toContain(".dark {");
  });
});

describe("the fonts of a brand", () => {
  it("writes one @font-face per file, from the site and from no outside host", () => {
    const text = brandCss(brand({ light: LIGHT }), {
      source: "clients/test/brand.toml",
      faces: [{ family: "Inter", file: "Inter-Bold.woff2", weight: "700" }],
    });
    expect(text).toContain('font-family: "Inter";');
    expect(text).toContain('src: url("/brand/fonts/Inter-Bold.woff2") format("woff2");');
    expect(text).toContain("font-weight: 700;");
    expect(text).not.toMatch(/url\("?https?:/);
    expect(declared(text, "@theme static", "font-sans")).toBe("Inter, sans-serif");
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
