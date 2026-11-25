/**
 * Tests for the Sim tile of the week page on the real sim files: the odds and the line of more wins of Your team, the
 * league fact with no team, the title odds or the favorite in a playoff week, and the champion after the final.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "bun:test";
import { finalWeekSim, playoffsWeekSim, roundTwoWeekSim, weekSim } from "../fixtures/sim";
import { SimTile } from "./sim-tile";
import { simTileOf } from "./tile";

afterEach(cleanup);

const HREF = "/sim/2026/";

/* The one link of the tile, which is the whole card. */
const tileLink = () => screen.getByRole("link");

describe("the Sim tile in the regular season", () => {
  it("shows the playoff odds of Bo Girds and the line of more wins of the file, and links to the sim page (AT-45)", () => {
    const data = simTileOf(weekSim);
    render(<SimTile tile={data.teams[6]} fact={data.fact} href={HREF} />);
    const link = tileLink();
    expect(link.getAttribute("href")).toBe(HREF);
    expect(link.textContent).toContain("Open The Race");
    expect(link.textContent).toContain("Playoff odds");
    expect(link.textContent).toContain("58%");
    expect(link.textContent).toContain("Win 5 of the 8 left and you're in.");
  });

  it("shows the league fact of the file with no team set (AT-46)", () => {
    const data = simTileOf(weekSim);
    render(<SimTile tile={null} fact={data.fact} href={HREF} />);
    expect(tileLink().textContent).toContain("6 managers fight for the last 4 spots");
    expect(tileLink().textContent).not.toContain("%");
  });

  it("asks for a team when the file has no league fact", () => {
    render(<SimTile tile={null} fact={null} href={HREF} />);
    expect(tileLink().textContent).toContain("Pick your team to see your odds.");
  });
});

describe("the Sim tile in a playoff week (AT-47)", () => {
  it("shows the title odds of the top seed, with its bye", () => {
    const data = simTileOf(playoffsWeekSim);
    render(<SimTile tile={data.teams[2]} fact={data.fact} href={HREF} />);
    expect(tileLink().textContent).toContain("Title odds");
    expect(tileLink().textContent).toContain("17%");
    expect(tileLink().textContent).toContain("Seed 1, a bye in week 15.");
  });

  it("shows the game of the round for a team that plays", () => {
    const data = simTileOf(playoffsWeekSim);
    render(<SimTile tile={data.teams[1]} fact={data.fact} href={HREF} />);
    expect(tileLink().textContent).toContain("14%");
    expect(tileLink().textContent).toContain(
      "Week 15 vs Maye d'force B with U. Win and you reach the semifinals.",
    );
  });

  it("shows the favorite fact for the 12th team, which is out", () => {
    const data = simTileOf(playoffsWeekSim);
    expect(data.teams[4]).toBeNull();
    render(<SimTile tile={data.teams[4]} fact={data.fact} href={HREF} />);
    expect(tileLink().textContent).toContain("6 teams left, Lil Fridge is the favorite at 23%");
    expect(tileLink().textContent).not.toContain("Title odds");
  });

  it("shows the favorite fact for a team that lost its bracket game", () => {
    const data = simTileOf(roundTwoWeekSim);
    const lost = Object.values(roundTwoWeekSim.pages).find(
      (page) => page.playoffs!.seed !== null && !page.playoffs!.alive,
    )!;
    expect(data.teams[lost.you]).toBeNull();
    expect(data.fact).toBe("4 teams left, The Blue Tent is the favorite at 28%");
  });
});

describe("the Sim tile after the final (AT-48)", () => {
  it("names the champion for each team and links to the sim page", () => {
    const data = simTileOf(finalWeekSim);
    for (const id of [3, 6]) {
      cleanup();
      render(<SimTile tile={data.teams[id]} fact={data.fact} href={HREF} />);
      expect(tileLink().textContent).toContain("Lil Fridge is the 2026 champion");
      expect(tileLink().getAttribute("href")).toBe(HREF);
    }
  });
});
