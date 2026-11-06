/**
 * Tests for the Awards chapter. They render the week 8 JSON of CPC and read each award tile.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Awards } from "./awards";
import { week8 } from "../fixtures/week-page";

afterEach(() => {
  cleanup();
});

function renderAwards(headshots = week8.headshots) {
  render(<Awards awards={week8.awards} headshots={headshots} blurb={week8.blurbs.awards} />);
  return screen.getByRole("region", { name: "Awards" });
}

/* The tile of each award, in the order of the JSON. */
const tiles = (chapter: HTMLElement) => within(chapter).getAllByRole("listitem");

describe("Awards", () => {
  it("shows a tile for each award with its name, the points, the player, and the team", () => {
    const chapter = renderAwards();
    expect(chapter.id).toBe("awards");
    expect(tiles(chapter).map((tile) => tile.textContent)).toEqual([
      "Top Scorer42.48Joe BurrowAll You Need Is Love",
      "MVB · Most Valuable Benchwarmer26.2Tony PollardTeehee",
      "Underperformer0Lamar JacksonBo Girds · proj 20.52",
      "Overachiever32.5Tee HigginsTeehee · proj 13.67",
    ]);
  });

  it("shows each player in a round photo frame (AT-33)", () => {
    const chapter = renderAwards();
    expect(within(tiles(chapter)[0]).getByRole("img", { name: "Joe Burrow" }).getAttribute("src")).toBe(
      "headshots/6770.png",
    );
  });

  it("shows the initials of a player with no headshot (AT-33)", () => {
    const chapter = renderAwards({});
    expect(within(tiles(chapter)[1]).getByRole("img", { name: "Tony Pollard" }).textContent).toBe("TP");
  });

  it("shows a note in place of the player when the award is missing", () => {
    render(<Awards awards={[{ title: "Overachiever", missing: true }]} headshots={{}} blurb="" />);
    expect(screen.getByText("Projections unavailable this week")).toBeTruthy();
  });

  it("shows the blurb as prose", () => {
    const chapter = renderAwards();
    expect(within(chapter).getByText(week8.blurbs.awards).tagName).toBe("P");
  });
});
