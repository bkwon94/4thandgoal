/**
 * Tests for the Game Changer chapter. They render the week 8 JSON of CPC and read the photo, the name, and the three tiles.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { GameChanger } from "./game-changer";

afterEach(() => {
  cleanup();
});

const gameChanger = week8.game_changer!;

function renderChapter(changer = gameChanger, headshots = week8.headshots) {
  render(<GameChanger gameChanger={changer} headshots={headshots} blurb={week8.blurbs.game_changer} />);
  return screen.getByRole("region", { name: "Game Changer" });
}

/* The text of each tile, label first. */
function tiles(chapter: HTMLElement) {
  return within(chapter)
    .getAllByRole("listitem")
    .map((tile) => tile.textContent);
}

describe("GameChanger", () => {
  it("shows Joe Burrow in a round photo frame with his team line (AT-16)", () => {
    const chapter = renderChapter();
    expect(chapter.id).toBe("game-changer");
    expect(within(chapter).getByRole("img", { name: "Joe Burrow" }).getAttribute("src")).toBe("headshots/6770.png");
    expect(within(chapter).getByText("Joe Burrow")).toBeTruthy();
    expect(within(chapter).getByText("QB · CIN · All You Need Is Love")).toBeTruthy();
  });

  it("shows three tiles for scored, projected, and over", () => {
    expect(tiles(renderChapter())).toEqual(["Scored42.48", "Projected22.04", "Over+20.44"]);
  });

  it("shows a dash for projected and over when the player has no projection", () => {
    const line = { ...gameChanger.award.line, projection: null };
    expect(tiles(renderChapter({ ...gameChanger, award: { ...gameChanger.award, line } }))).toEqual([
      "Scored42.48",
      "Projected—",
      "Over—",
    ]);
  });

  it("shows the initials when the week has no headshot of the player (AT-33)", () => {
    const chapter = renderChapter(gameChanger, {});
    expect(within(chapter).getByRole("img", { name: "Joe Burrow" }).textContent).toBe("JB");
  });

  it("shows the blurb as prose", () => {
    const chapter = renderChapter();
    expect(within(chapter).getByText(week8.blurbs.game_changer!).tagName).toBe("P");
  });
});
