/**
 * Tests for The Race on the real CPC week 11 sim file, with Bo Girds as Your team: the title, the Goal switch, the seed picker,
 * the odds of the Your team card, and the League board in odds order with the accent bar of Your team.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, spyOn } from "bun:test";
import { weekElevenSim } from "../fixtures/sim";
import { SimPage } from "./sim-page";

beforeEach(() => {
  spyOn(window, "matchMedia").mockImplementation(
    (query: string) =>
      ({
        matches: false,
        media: query,
        addEventListener: () => {},
        removeEventListener: () => {},
      }) as unknown as MediaQueryList,
  );
});

afterEach(() => {
  cleanup();
});

// Bo Girds is roster 6 in CPC.
const YOU = 6;
const sim = weekElevenSim;

/* The roster ids of the board rows from the top, and the odds order of the file for one Goal. */
const boardIds = () =>
  within(screen.getByRole("group", { name: /^League board/ }))
    .getAllByRole("button")
    .map((bar) => Number(bar.getAttribute("data-roster")));
const oddsOf = (id: number, goal: string) =>
  sim.board.find((row) => row.roster_id === id)!.goals[goal].odds;
const expectOddsOrder = (goal: string) => {
  const ids = boardIds();
  expect(ids).toHaveLength(12);
  const odds = ids.map((id) => oddsOf(id, goal));
  expect(odds).toEqual([...odds].sort((a, b) => b - a));
};
const cardOdds = () =>
  screen
    .getByRole("region", { name: "Your team" })
    .querySelector("[data-goal-odds]")!
    .getAttribute("data-goal-odds");

describe("The Race", () => {
  it("is titled The Race, with the week and the weeks left", () => {
    render(<SimPage sim={sim} you={YOU} />);
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("The Race");
    expect(screen.getByText("After week 11 · 3 weeks left")).toBeTruthy();
  });

  it("opens on the open Goal of Your team, with its odds on the card", () => {
    render(<SimPage sim={sim} you={YOU} />);
    const open = sim.pages[YOU].open_goal;
    expect(open).toBe("spot");
    expect(screen.getByRole("radio", { name: "Spot" }).getAttribute("aria-checked")).toBe("true");
    expect(cardOdds()).toBe(`${sim.pages[YOU].goals.spot.odds}%`);
  });

  it("shows 12 teams in odds order for a spot, Bo Girds with the accent bar and the You tag", () => {
    render(<SimPage sim={sim} you={YOU} />);
    expectOddsOrder("spot");
    const board = screen.getByRole("group", { name: /^League board/ });
    const bars = within(board).getAllByRole("button");
    for (const bar of bars) {
      const mine = Number(bar.getAttribute("data-roster")) === YOU;
      expect(bar.querySelector("[data-tone]")!.getAttribute("data-tone")).toBe(
        mine ? "accent" : "ink",
      );
      expect(within(bar).queryByText("You") !== null).toBe(mine);
    }
  });

  it("moves the card odds and the board to the odds of a bye on a tap of Bye", () => {
    render(<SimPage sim={sim} you={YOU} />);
    fireEvent.click(screen.getByRole("radio", { name: "Bye" }));
    expect(cardOdds()).toBe(`${sim.pages[YOU].goals.bye.odds}%`);
    expectOddsOrder("bye");
    expect(screen.getByRole("group", { name: "League board: odds of a bye" })).toBeTruthy();
  });

  it("shows the odds of the 3 seed after a tap of Seed, then 3", () => {
    render(<SimPage sim={sim} you={YOU} />);
    fireEvent.click(screen.getByRole("radio", { name: "Seed" }));
    fireEvent.click(screen.getByRole("button", { name: "Seed 3" }));
    expect(cardOdds()).toBe(`${sim.pages[YOU].goals["seed-3"].odds}%`);
    expectOddsOrder("seed-3");
    expect(screen.getByRole("group", { name: "League board: odds of the 3 seed" })).toBeTruthy();
  });
});
