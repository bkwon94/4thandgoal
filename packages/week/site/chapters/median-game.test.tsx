/**
 * Tests for the median game. They render the week 8 JSON of CPC and read a bar for each team against the median line.
 * A copy with no median game checks that the chapter is left out.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { MedianGame } from "./median-game";

afterEach(() => {
  cleanup();
});

function renderMedian() {
  render(<MedianGame median={week8.median} avatars={week8.avatars} blurb={week8.blurbs.median} />);
  return screen.getByRole("region", { name: "The median game" });
}

describe("MedianGame", () => {
  it("names the median line beside the heading", () => {
    const chapter = renderMedian();
    expect(chapter.id).toBe("median");
    expect(within(chapter).getByText("Line 99.6")).toBeTruthy();
  });

  it("shows a bar for each team with its avatar, its name, and its score, and marks the teams above the line", () => {
    const chapter = renderMedian();
    const bars = within(within(chapter).getByRole("list", { name: "Scores against the median" })).getAllByRole("listitem");
    expect(bars).toHaveLength(12);
    expect(bars[0].textContent).toBe("Teehee134.1Above");
    expect(bars[11].textContent).toBe("Lil Fridge80.11Below");
    expect(bars[0].querySelector("img")?.getAttribute("src")).toMatch(/^avatars\//);
  });

  it("shows the blurb as prose", () => {
    const chapter = renderMedian();
    expect(within(chapter).getByText(week8.blurbs.median!).tagName).toBe("P");
  });

  it("leaves the chapter out when the week has no median game", () => {
    const { container } = render(<MedianGame median={null} avatars={week8.avatars} />);
    expect(container.innerHTML).toBe("");
  });
});
