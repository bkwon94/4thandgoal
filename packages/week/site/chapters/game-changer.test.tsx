/**
 * Tests for the game changer hero. They render the week 6 JSON and read the name, the team line, and the points.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { firstSentence, week6 } from "../fixtures/week-page";
import { GameChanger } from "./game-changer";

afterEach(() => {
  cleanup();
});

const gameChanger = week6.game_changer!;

describe("GameChanger", () => {
  it("shows the label, the player name, and the team line", () => {
    render(<GameChanger gameChanger={gameChanger} headshots={week6.headshots} blurb={week6.blurbs.game_changer} />);
    expect(screen.getByText("Game Changer")).toBeTruthy();
    expect(screen.getByText("Germie Bernard")).toBeTruthy();
    expect(screen.getByText("WR · PIT · behold the lamb")).toBeTruthy();
  });

  it("shows the points and the projection as formatted text", () => {
    render(<GameChanger gameChanger={gameChanger} headshots={week6.headshots} />);
    expect(screen.getByText("20.2")).toBeTruthy();
    expect(screen.getByText("projected 8.13")).toBeTruthy();
  });

  it("leaves out the projection line when the player has no projection", () => {
    const line = { ...gameChanger.award.line, projection: null };
    render(<GameChanger gameChanger={{ ...gameChanger, award: { ...gameChanger.award, line } }} headshots={week6.headshots} />);
    expect(screen.queryByText(/projected/)).toBeNull();
  });

  it("shows the headshot cutout and the blurb", () => {
    const { container } = render(
      <GameChanger gameChanger={gameChanger} headshots={week6.headshots} blurb={week6.blurbs.game_changer} />,
    );
    expect(container.querySelector("img")?.getAttribute("src")).toBe("headshots/13274.png");
    expect(screen.getByText(firstSentence(week6.blurbs.game_changer), { exact: false })).toBeTruthy();
  });
});
