/**
 * Tests for the slot row of the egg art: one grid column per letter of the egg word, each of the same width.
 * The browser lays out the grid, so these tests read the columns and the classes that set the widths.
 */
import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { SlotRow } from "./egg-art";
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
