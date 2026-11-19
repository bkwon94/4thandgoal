/**
 * Tests for the sim page in the playoff weeks and after the final, on the playoff fixtures of CPC (ACCEPTANCE.md).
 * They check Your team first: the title odds, the game of the round with its two tiles, the bye, the out line, and the bracket.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { finalWeekSim, playoffsWeekSim, roundTwoWeekSim } from "../fixtures/sim";
import type { WeekSim } from "../schema/sim-types";
import { SimPage } from "./sim-page";

afterEach(cleanup);

/* The playoff part of a page. Each team of a fixture has one, and each holds the same bracket. */
const playoffsOf = (sim: WeekSim, you: number) => sim.pages[you].playoffs!;
const seed = (sim: WeekSim, n: number) => playoffsOf(sim, sim.sample[0].table[0]).teams[n - 1].roster_id;
// The 12th team of the table of stored run 1, the last place of the regular season.
const last = (sim: WeekSim) => sim.sample[0].table[11];
const header = () => screen.getByRole("region", { name: "Your team" });
const gameCard = () => screen.getByRole("article", { name: /^Week \d+ vs / });
const bracket = () => screen.getByRole("region", { name: "Bracket" });

describe("a team still in the playoffs", () => {
  it("sees its title odds, its game of the round, and two tiles with the odds after a win and a loss (AT-42)", () => {
    const you = seed(roundTwoWeekSim, 1);
    const playoffs = playoffsOf(roundTwoWeekSim, you);
    const game = playoffs.game!;
    render(<SimPage sim={roundTwoWeekSim} you={you} />);
    expect(header().textContent).toContain(`${playoffs.title}%`);
    expect(header().textContent).toContain("Title odds");
    expect(within(gameCard()).getByRole("heading").textContent).toBe(`Week ${game.week} vs ${roundTwoWeekSim.names[game.opponent]}`);
    const tiles = within(gameCard()).getAllByRole("group");
    expect(tiles.map((tile) => tile.getAttribute("aria-label"))).toEqual(["Win", "Lose"]);
    const [win, loss] = game.results;
    expect(tiles[0].textContent).toContain(`${win.title}%`);
    expect(tiles[0].textContent).toContain(`${Math.round(win.chance)}% likely`);
    expect(tiles[1].textContent).toContain(`${loss.title}%`);
    expect(gameCard().textContent).toContain(`Win and you reach the final. ${win.title}% to win it all.`);
  });

  it("has no week switch and no sentence of more wins in the playoffs", () => {
    render(<SimPage sim={roundTwoWeekSim} you={seed(roundTwoWeekSim, 1)} />);
    expect(screen.queryByRole("navigation", { name: "Weeks" })).toBeNull();
    expect(screen.queryByText(/more wins|Win \d+ of/)).toBeNull();
  });

  it("sees a bye with no tile while its next opponent is not set", () => {
    const you = seed(playoffsWeekSim, 1);
    render(<SimPage sim={playoffsWeekSim} you={you} />);
    expect(screen.getByRole("article", { name: "Bye in week 15" }).textContent).toContain("week 16");
    expect(screen.queryAllByRole("group")).toHaveLength(0);
    expect(header().textContent).toContain(`${playoffsOf(playoffsWeekSim, you).title}%`);
  });

  it("offers tiles only for the game of the current round, never a later round (AT-66)", () => {
    for (const [sim, n] of [[playoffsWeekSim, 3], [roundTwoWeekSim, 1]] as const) {
      render(<SimPage sim={sim} you={seed(sim, n)} />);
      expect(screen.getAllByRole("group")).toHaveLength(2);
      expect(within(bracket()).queryAllByRole("group")).toHaveLength(0);
      expect(within(bracket()).queryAllByRole("button")).toHaveLength(0);
      cleanup();
    }
  });
});

describe("a team out of the playoffs", () => {
  it("sees Out of the playoffs and the bracket with the title odds of each team left (AT-43)", () => {
    const you = last(playoffsWeekSim);
    const playoffs = playoffsOf(playoffsWeekSim, you);
    render(<SimPage sim={playoffsWeekSim} you={you} />);
    expect(screen.getByRole("heading", { name: "Out of the playoffs" })).toBeTruthy();
    expect(screen.queryAllByRole("group")).toHaveLength(0);
    const rows = within(bracket()).getAllByRole("listitem");
    for (const team of playoffs.teams.filter((entry) => entry.alive)) {
      const row = rows.find((item) => item.textContent?.includes(playoffsWeekSim.names[team.roster_id]));
      expect(row?.textContent).toContain(`${team.title}%`);
    }
  });

  it("lists the teams left by title odds, best first", () => {
    const you = last(roundTwoWeekSim);
    render(<SimPage sim={roundTwoWeekSim} you={you} />);
    const odds = screen.getByRole("region", { name: "Title odds" });
    const left = playoffsOf(roundTwoWeekSim, you).teams.filter((team) => team.alive).sort((a, b) => b.title - a.title);
    expect(within(odds).getAllByRole("listitem").map((row) => row.textContent)).toEqual(
      left.map((team) => expect.stringContaining(roundTwoWeekSim.names[team.roster_id])),
    );
    expect(left).toHaveLength(4);
  });
});

describe("after the final", () => {
  it("shows the final bracket and the champion, with no result tile and no sim button (AT-44)", () => {
    const champion = playoffsOf(finalWeekSim, last(finalWeekSim)).champion!;
    render(<SimPage sim={finalWeekSim} you={last(finalWeekSim)} />);
    const card = screen.getByRole("article", { name: "2026 champion" });
    expect(card.textContent).toContain(finalWeekSim.names[champion]);
    expect(screen.queryAllByRole("group")).toHaveLength(0);
    expect(screen.queryByRole("button", { name: /sim/i })).toBeNull();
    // Each game of each round shows its real score and its winner.
    const playoffs = playoffsOf(finalWeekSim, champion);
    for (const round of playoffs.rounds) {
      for (const game of round.games) {
        const [a, b] = game.scores!;
        expect(bracket().textContent).toContain(a.toFixed(1));
        expect(bracket().textContent).toContain(b.toFixed(1));
      }
    }
  });

  it("names how the season of Your team ended", () => {
    const champion = playoffsOf(finalWeekSim, last(finalWeekSim)).champion!;
    render(<SimPage sim={finalWeekSim} you={champion} />);
    expect(header().textContent).toContain("Champion");
    cleanup();
    render(<SimPage sim={finalWeekSim} you={last(finalWeekSim)} />);
    expect(header().textContent).toContain("Out of the playoffs");
  });

  it("has no chart of the odds of each team by week (AT-69)", () => {
    const { container } = render(<SimPage sim={finalWeekSim} you={last(finalWeekSim)} />);
    expect(screen.queryByRole("img")).toBeNull();
    expect(container.querySelector("canvas, svg:not([aria-hidden='true'])")).toBeNull();
    expect(screen.queryByText(/by week/i)).toBeNull();
  });
});
