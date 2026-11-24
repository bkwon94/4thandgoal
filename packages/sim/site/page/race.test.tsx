/**
 * Tests for The Race on the real CPC week 11 sim file, with Bo Girds as Your team: the title, the Goal switch, the seed picker,
 * the odds of the Your team card, and the League board in odds order with the accent bar of Your team.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, mock, spyOn } from "bun:test";
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

/* The Finish list of the open card, and its bar of one Finish by its name, such as "4-2". */
const finishList = () => screen.getByRole("group", { name: "Finish list for a playoff spot" });
const finishBar = (name: string) =>
  within(finishList())
    .getAllByRole("button")
    .find((bar) => bar.getAttribute("data-finish") === name)!;

describe("the Finish list of the Your team card", () => {
  it("opens in place with one bar per Finish from 6-0 to 0-6, before the week card", () => {
    render(<SimPage sim={sim} you={YOU} />);
    expect(screen.queryByRole("dialog")).toBeNull();
    const bars = within(finishList()).getAllByRole("button");
    expect(bars.map((bar) => bar.getAttribute("data-finish"))).toEqual([
      "6-0",
      "5-1",
      "4-2",
      "3-3",
      "2-4",
      "1-5",
      "0-6",
    ]);
    expect(finishBar("4-2").textContent).toContain("ends 15-13");
    const card = screen.getByRole("region", { name: "Your team" });
    const week = within(card).getByRole("navigation", { name: "Weeks" });
    // The Finish list comes before the week card in the order of the page.
    expect(
      finishList().compareDocumentPosition(week) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it("shows the Paths of 4-2 with their copy on a tap", async () => {
    render(<SimPage sim={sim} you={YOU} />);
    const four = sim.pages[YOU].finishes.spot.find((f) => f.more_wins === 4)!;
    fireEvent.click(finishBar("4-2"));
    expect(finishBar("4-2").getAttribute("aria-expanded")).toBe("true");
    const panel = screen.getByRole("region", { name: "Paths at 4-2" });
    expect(panel.textContent).toContain(`4-2 · ends 15-13 · ${Math.round(four.chance)}% likely`);
    const paths = within(panel).getAllByRole("listitem");
    expect(paths).toHaveLength(four.paths.length);
    four.paths.forEach((path, i) => {
      expect(paths[i].textContent).toMatch(/^If .+ ends \d+-\d+ or worse/);
      expect(paths[i].textContent).toContain(
        `Happens ${Math.round(path.chance)}% · you're in ${path.odds}%.`,
      );
    });
    fireEvent.click(finishBar("4-2"));
    expect(finishBar("4-2").getAttribute("aria-expanded")).toBe("false");
    await waitFor(() => expect(screen.queryByRole("region", { name: "Paths at 4-2" })).toBeNull());
  });

  it("shows the copy of a sure Finish, a Finish with no way in, and a best chance", () => {
    render(<SimPage sim={sim} you={YOU} />);
    fireEvent.click(finishBar("6-0"));
    expect(screen.getByRole("region", { name: "Paths at 6-0" }).textContent).toContain(
      "You're in whatever the others do.",
    );
    fireEvent.click(finishBar("1-5"));
    expect(screen.getByRole("region", { name: "Paths at 1-5" }).textContent).toContain(
      "No way in at this record.",
    );
    fireEvent.click(finishBar("3-3"));
    const best = screen.getByRole("region", { name: "Paths at 3-3" });
    expect(within(best).getByText("Best chance")).toBeTruthy();
    expect(within(best).getAllByRole("listitem")).toHaveLength(1);
  });
});

describe("another team on the League board", () => {
  it("opens a sheet with its Finish list and Make this Your team", () => {
    const onYou = mock((_: number) => {});
    render(<SimPage sim={sim} you={YOU} onYou={onYou} />);
    const fridge = Number(Object.entries(sim.names).find(([, name]) => name === "Lil Fridge")![0]);
    const board = screen.getByRole("group", { name: /^League board/ });
    fireEvent.click(
      within(board)
        .getAllByRole("button")
        .find((bar) => Number(bar.getAttribute("data-roster")) === fridge)!,
    );
    const sheet = screen.getByRole("dialog", { name: "Lil Fridge" });
    const bars = within(
      within(sheet).getByRole("group", { name: "Finish list for a playoff spot" }),
    ).getAllByRole("button");
    expect(bars).toHaveLength(sim.pages[fridge].finishes.spot.length);
    fireEvent.click(within(sheet).getByRole("button", { name: "Make this Your team" }));
    expect(onYou).toHaveBeenCalledWith(fridge);
  });
});
