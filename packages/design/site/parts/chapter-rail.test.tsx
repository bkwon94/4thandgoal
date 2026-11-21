/**
 * Tests for the chapter rail of the week page.
 * They check that the rail links each chapter and sticks under the top band by the band height token.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "bun:test";
import { ChapterRail } from "./chapter-rail";

afterEach(() => cleanup());

const CHAPTERS = [
  { id: "awards", label: "Awards" },
  { id: "leaders", label: "Position leaders" },
];

describe("ChapterRail", () => {
  it("links each chapter, and sticks under the band by the band height token", () => {
    render(<ChapterRail chapters={CHAPTERS} />);
    const rail = screen.getByRole("navigation", { name: "Chapters", hidden: true });
    expect(
      within(rail)
        .getAllByRole("link", { hidden: true })
        .map((link) => link.getAttribute("href")),
    ).toEqual(["#awards", "#leaders"]);
    // The token grows by the Deadline banner, so the rail follows the band when the banner shows.
    expect(rail.className).toContain("sticky");
    expect(rail.className).toContain("top-band-height");
  });
});
