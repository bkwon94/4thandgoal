/**
 * Tests for the egg art: the whole egg under its two halves, and the slot row of one grid column per letter.
 * The browser lays out and paints the art, so these tests read the elements and the classes that set the look.
 */
import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { crackOf, EGG_MIDDLE } from "./crack";
import { Egg, SlotRow } from "./egg-art";
import { slotsOf } from "./slots";

afterEach(cleanup);

function row(tone: "page" | "hero") {
  const { container } = render(<SlotRow slots={slotsOf("CORNERSTONE", [], "C")} tone={tone} landing={tone === "hero"} />);
  return container.firstElementChild as HTMLElement;
}

describe("SlotRow", () => {
  for (const tone of ["page", "hero"] as const) {
    it(`lays the ${tone} tiles out as one grid column per letter, each of the same width`, () => {
      const grid = row(tone);
      expect(grid.classList.contains("grid")).toBe(true);
      expect(grid.classList.contains("flex-wrap")).toBe(false);
      // Each column shrinks from the tile size to zero by the same amount, so the row stays inside its card.
      expect(grid.style.gridTemplateColumns).toMatch(/^repeat\(11, minmax\(0(px)?, [\d.]+rem\)\)$/);
      const tiles = [...grid.children] as HTMLElement[];
      expect(tiles).toHaveLength(11);
      // The filled tile and the empty slots each fill their column, so the row is even.
      for (const tile of tiles) expect(tile.classList.contains("w-full")).toBe(true);
    });
  }
});

describe("Egg", () => {
  // The two halves clip the art along one zigzag, and the antialiased edges of two clips leave a thin seam.
  // The whole art shows until the burst, and the halves show only from it, so no crack shows before the lines draw.
  // The visibility of each part lives in globals.css, and jsdom applies no CSS, so these tests read the parts and classes.
  it("draws the whole art, unclipped, under the two halves of an egg at rest", () => {
    const { container } = render(<Egg crack={null} motion={true} />);
    const whole = container.querySelector('[data-egg-part="whole"]') as SVGElement;
    expect(whole).not.toBeNull();
    expect(whole.hasAttribute("clip-path")).toBe(false);
    const half = container.querySelector(".egg-half") as SVGElement;
    expect(whole.compareDocumentPosition(half) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(whole.classList.contains("egg-whole-out")).toBe(false);
  });

  it("hides the whole art at the burst of a crack, so the halves fly apart alone", () => {
    const { container } = render(<Egg crack={crackOf(EGG_MIDDLE, 7)} motion={true} />);
    const whole = container.querySelector('[data-egg-part="whole"]') as SVGElement;
    expect(whole.classList.contains("egg-whole-out")).toBe(true);
    const halves = [...container.querySelectorAll(".egg-half")];
    expect(halves.map((half) => half.classList.contains("egg-split-top") || half.classList.contains("egg-split-bottom"))).toEqual([true, true]);
  });
});
