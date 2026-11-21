/**
 * Tests for the sim page in the playoff weeks and after the final, on the playoff fixtures of CPC (ACCEPTANCE.md): the title odds, the
 * game of the round with its two tiles and their What-if, the bye, the out line, and the bracket of Your team.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, spyOn } from "bun:test";
import { finalWeekSim, playoffsWeekSim, roundTwoWeekSim } from "../fixtures/sim";
import { fakeWhatIfApi } from "../fixtures/what-if-api";
import { whatIfApi } from "../lib/what-if-api";
import type { WeekSim } from "../schema/sim-types";
import { SimPage } from "./sim-page";

afterEach(cleanup);

/* The playoff part of a page. Each team of a fixture has one, and each holds the same bracket. */
const playoffsOf = (sim: WeekSim, you: number) => sim.pages[you].playoffs!;
const seed = (sim: WeekSim, n: number) =>
  playoffsOf(sim, sim.sample[0].table[0]).teams[n - 1].roster_id;
// The 12th team of the table of stored run 1, the last place of the regular season.
const last = (sim: WeekSim) => sim.sample[0].table[11];
const header = () => screen.getByRole("region", { name: "Your team" });
const gameCard = () => screen.getByRole("article", { name: /^Week \d+ vs / });
const bracket = () => screen.getByRole("region", { name: "Bracket" });
// The result tiles of the game card, each a toggle button in the group "Results", as in the regular weeks.
const tiles = () =>
  within(within(gameCard()).getByRole("group", { name: "Results" })).getAllByRole("button");
const tile = (name: string) =>
  tiles().find((entry) => entry.querySelector("[data-result-name]")?.textContent === name)!;
const noTiles = () => expect(screen.queryAllByRole("group", { name: "Results" })).toHaveLength(0);
const setLine = () => screen.queryByRole("region", { name: "What-if" });

describe("a team still in the playoffs", () => {
  it("sees its title odds, its game of the round, and two tiles with the odds after a win and a loss (AT-42)", () => {
    const you = seed(roundTwoWeekSim, 1);
    const playoffs = playoffsOf(roundTwoWeekSim, you);
    const game = playoffs.game!;
    render(<SimPage sim={roundTwoWeekSim} you={you} />);
    expect(header().textContent).toContain(`${playoffs.title}%`);
    expect(header().textContent).toContain("Title odds");
    expect(within(gameCard()).getByRole("heading").textContent).toBe(
      `Week ${game.week} vs ${roundTwoWeekSim.names[game.opponent]}`,
    );
    expect(tiles().map((entry) => entry.querySelector("[data-result-name]")?.textContent)).toEqual([
      "Win",
      "Lose",
    ]);
    const [win, loss] = game.results;
    expect(tiles()[0].textContent).toContain(`${win.title}%`);
    expect(tiles()[0].textContent).toContain(`${Math.round(win.chance)}% likely`);
    expect(tiles()[1].textContent).toContain(`${loss.title}%`);
    expect(gameCard().textContent).toContain(
      `Win and you reach the final. ${win.title}% to win it all.`,
    );
  });

  it("has no week switch and no sentence of more wins in the playoffs", () => {
    render(<SimPage sim={roundTwoWeekSim} you={seed(roundTwoWeekSim, 1)} />);
    expect(screen.queryByRole("navigation", { name: "Weeks" })).toBeNull();
    expect(screen.queryByText(/more wins|Win \d+ of/)).toBeNull();
  });

  it("sees a bye with no tile while its next opponent is not set", () => {
    const you = seed(playoffsWeekSim, 1);
    render(<SimPage sim={playoffsWeekSim} you={you} />);
    expect(screen.getByRole("article", { name: "Bye in week 15" }).textContent).toContain(
      "week 16",
    );
    noTiles();
    expect(screen.queryAllByRole("button", { pressed: false })).toHaveLength(0);
    expect(header().textContent).toContain(`${playoffsOf(playoffsWeekSim, you).title}%`);
  });

  it("offers tiles only for the game of the current round, never a later round (AT-66)", () => {
    for (const [sim, n] of [
      [playoffsWeekSim, 3],
      [roundTwoWeekSim, 1],
    ] as const) {
      render(<SimPage sim={sim} you={seed(sim, n)} whatIf={fakeWhatIfApi()} />);
      expect(tiles()).toHaveLength(2);
      expect(screen.getAllByRole("button", { pressed: false })).toHaveLength(2);
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
    noTiles();
    const rows = within(bracket()).getAllByRole("listitem");
    for (const team of playoffs.teams.filter((entry) => entry.alive)) {
      const row = rows.find((item) =>
        item.textContent?.includes(playoffsWeekSim.names[team.roster_id]),
      );
      expect(row?.textContent).toContain(`${team.title}%`);
    }
  });

  it("lists the teams left by title odds, best first", () => {
    const you = last(roundTwoWeekSim);
    render(<SimPage sim={roundTwoWeekSim} you={you} />);
    const odds = screen.getByRole("region", { name: "Title odds" });
    const left = playoffsOf(roundTwoWeekSim, you)
      .teams.filter((team) => team.alive)
      .sort((a, b) => b.title - a.title);
    expect(
      within(odds)
        .getAllByRole("listitem")
        .map((row) => row.textContent),
    ).toEqual(left.map((team) => expect.stringContaining(roundTwoWeekSim.names[team.roster_id])));
    expect(left).toHaveLength(4);
  });
});

describe("after the final", () => {
  it("shows the final bracket and the champion, with no result tile and no sim button (AT-44)", () => {
    const champion = playoffsOf(finalWeekSim, last(finalWeekSim)).champion!;
    render(<SimPage sim={finalWeekSim} you={last(finalWeekSim)} />);
    const card = screen.getByRole("article", { name: "2026 champion" });
    expect(card.textContent).toContain(finalWeekSim.names[champion]);
    noTiles();
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

/* In the week 14 fixture, the 3rd seed plays the 6th seed in week 15, and both teams of the game are set. The one fake
   of the port holds no answer of a playoff week, so it answers 422, as the route does for a set it cannot hold. */
describe("the What-if of a bracket game", () => {
  /* The API is down in each test of this block, as a refused connection makes it, so no test opens a socket. A test
     that needs an answer passes the one fake of the port. */
  beforeEach(() => {
    spyOn(globalThis, "fetch").mockImplementation((() =>
      Promise.reject(new TypeError("fetch failed"))) as unknown as typeof fetch);
  });

  const you = () => seed(playoffsWeekSim, 3);
  const game = () => playoffsOf(playoffsWeekSim, you()).game!;

  it("sets the result of the game on a tap of a tile, with only the week and the game", () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={playoffsWeekSim} you={you()} whatIf={api} />);
    fireEvent.click(tile("Win"));
    expect(api.calls.map((call) => call.ask)).toEqual([
      { you: you(), set: [{ week: game().week, game: "win", median: null }] },
    ]);
    expect(tile("Win").getAttribute("aria-pressed")).toBe("true");
    expect(setLine()!.textContent).toContain(`What-if: Wk ${game().week} win`);
    expect(header().getAttribute("aria-busy")).toBe("true");
  });

  it("cancels the call before a new tap", () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={playoffsWeekSim} you={you()} whatIf={api} />);
    fireEvent.click(tile("Win"));
    fireEvent.click(tile("Lose"));
    expect(api.calls.map((call) => call.ask.set)).toEqual([
      [{ week: game().week, game: "win", median: null }],
      [{ week: game().week, game: "loss", median: null }],
    ]);
    expect(api.calls[0].signal.aborted).toBe(true);
    expect(api.calls[1].signal.aborted).toBe(false);
    expect(tile("Lose").getAttribute("aria-pressed")).toBe("true");
    expect(tile("Win").getAttribute("aria-pressed")).toBe("false");
  });

  it("clears the result on a second tap of its tile, with no new call", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={playoffsWeekSim} you={you()} whatIf={api} />);
    fireEvent.click(tile("Win"));
    fireEvent.click(tile("Win"));
    expect(api.calls).toHaveLength(1);
    expect(api.calls[0].signal.aborted).toBe(true);
    await waitFor(() => expect(setLine()).toBeNull());
    expect(tile("Win").getAttribute("aria-pressed")).toBe("false");
  });

  it("keeps the numbers of the file and shows one line when the call fails", async () => {
    const playoffs = playoffsOf(playoffsWeekSim, you());
    render(<SimPage sim={playoffsWeekSim} you={you()} whatIf={fakeWhatIfApi()} />);
    fireEvent.click(tile("Win"));
    await screen.findByText("The What-if is not available now.");
    await waitFor(() => expect(setLine()).toBeNull());
    expect(tile("Win").getAttribute("aria-pressed")).toBe("false");
    expect(header().textContent).toContain(`${playoffs.title}%`);
  });

  it("shows the line when the API is down", async () => {
    // The real client of the port, with the refused call of the beforeEach, as when the API is down.
    render(
      <SimPage
        sim={playoffsWeekSim}
        you={you()}
        whatIf={whatIfApi({ url: "http://127.0.0.1:9", client: "cpc" })}
      />,
    );
    fireEvent.click(tile("Lose"));
    await screen.findByText("The What-if is not available now.");
    expect(tile("Lose").getAttribute("aria-pressed")).toBe("false");
  });
});

/* With no regular week left, "Sim the season" replays only the playoffs, so the stage opens on Playoffs. */
describe("Sim the season in the playoffs", () => {
  it("shows only Sim the season before the final, for a team in and a team out", () => {
    for (const you of [seed(playoffsWeekSim, 3), seed(playoffsWeekSim, 1), last(playoffsWeekSim)]) {
      render(<SimPage sim={playoffsWeekSim} you={you} />);
      expect(
        screen.getAllByRole("button", { name: /^Sim / }).map((button) => button.textContent),
      ).toEqual(["Sim the season"]);
      cleanup();
    }
  });

  it("plays Playoffs, then Champion, with no Season screen", () => {
    render(<SimPage sim={roundTwoWeekSim} you={seed(roundTwoWeekSim, 1)} random={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    const stage = screen.getByRole("region", { name: "Sim replay" });
    const screens = within(stage).getByRole("list", { name: "Screens" });
    expect(
      within(screens)
        .getAllByRole("button")
        .map((button) => button.textContent),
    ).toEqual(["Playoffs", "Champion"]);
    expect(
      within(screens).getByRole("button", { name: "Playoffs" }).getAttribute("aria-current"),
    ).toBe("step");
  });
});
