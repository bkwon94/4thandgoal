/**
 * Tests for the four numbers under the hero of the week page. They render the week 8 JSON of CPC.
 * They read each tile by its label, as a reader does, not by the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { WeekNumbers } from "./week-numbers";

afterEach(() => {
  cleanup();
});

/* The text of each tile, label first, in the order of the page. */
function tiles() {
  const region = screen.getByRole("region", { name: "The week in numbers" });
  return within(region)
    .getAllByRole("listitem")
    .map((tile) => tile.textContent);
}

describe("WeekNumbers", () => {
  it("shows the top score, the median, the closest margin, and the Game Changer gap (AT-16)", () => {
    render(<WeekNumbers matchups={week8.matchups} median={week8.median} gameChanger={week8.game_changer} />);
    expect(tiles()).toEqual([
      "Top Score134.1Teehee",
      "Median99.66 above, 6 below",
      "Closest1.43The Blue Tent over London Cooking",
      "Game Changer+20.44Burrow over projection",
    ]);
  });

  it("takes the median of the scores for a league with no median game", () => {
    render(<WeekNumbers matchups={week8.matchups} median={null} gameChanger={week8.game_changer} />);
    // The two middle scores of the twelve are 100.31 and 98.88.
    expect(tiles()[1]).toBe("Median99.66 above, 6 below");
  });

  it("shows three numbers for a week with no Game Changer or no projection", () => {
    render(<WeekNumbers matchups={week8.matchups} median={week8.median} gameChanger={null} />);
    expect(tiles().map((tile) => tile?.split(/\d/)[0])).toEqual(["Top Score", "Median", "Closest"]);
  });
});
