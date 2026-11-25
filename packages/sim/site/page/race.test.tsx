/**
 * Tests for The Race on the real CPC week 11 sim file, with Bo Girds as Your team: the title, the Goal switch, the seed picker,
 * the odds of the Your team card, and the League board in odds order with the accent bar of Your team.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, mock, spyOn } from "bun:test";
import { weekElevenSim } from "../fixtures/sim";
import { fakeWhatIfApi, tryIt } from "../fixtures/what-if-api";
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
    const week = within(card).getByRole("article", { name: /^Week 12 vs / });
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

describe("the Week plan of a Path", () => {
  const four = () => sim.pages[YOU].finishes.spot.find((f) => f.more_wins === 4)!;
  const openPlan = () => {
    fireEvent.click(finishBar("4-2"));
    const panel = screen.getByRole("region", { name: "Paths at 4-2" });
    fireEvent.click(within(panel).getAllByRole("button", { name: /^Week plan:/ })[0]);
    return screen.getByRole("dialog", { name: /^Your plan to 15-13/ });
  };

  it("opens in a sheet from the first Path of 4-2, with its header, its order line, and one row per week", () => {
    render(<SimPage sim={sim} you={YOU} />);
    const plan = four().paths[0].plan!;
    const sheet = openPlan();
    expect(
      within(sheet).getByRole("heading", { name: `Your plan to 15-13 · you're in ${plan.odds}%` }),
    ).toBeTruthy();
    expect(plan.any_order).toBe(true);
    expect(sheet.textContent).toContain(
      "Any 4 wins of your 6 work. This is the most common order.",
    );
    const rows = within(
      within(sheet).getByRole("list", { name: "Weeks of the plan" }),
    ).getAllByRole("listitem");
    expect(rows).toHaveLength(3);
    plan.weeks.forEach((week, i) => {
      const text = rows[i].textContent!;
      expect(text).toContain(`Week ${week.week} · vs ${sim.names[week.opponent]}`);
      // Each row reads the Score to beat of its own result. A loss row holds none against the opponent.
      if (week.game === "win") {
        expect(week.win).not.toBeNull();
        expect(text).toContain(`Score ${week.win} to win, ${week.win_sure} to be sure.`);
      } else {
        expect(week.win).toBeNull();
        expect(text).not.toContain("to win,");
      }
      if (week.median === "above")
        expect(text).toContain(
          `Score ${week.median_score} to beat the median, ${week.median_sure} to be sure.`,
        );
      for (const game of week.root_for)
        expect(text).toContain(`${sim.names[game.winner]} over ${sim.names[game.loser]}`);
    });
    // Week 12 is Bo Girds against roster 5.
    expect(plan.weeks[0].opponent).toBe(5);
    expect(rows[0].textContent).toContain("Win and beat the median.");
  });

  it("sets the 3 results of the plan as a What-if on Try it, and the card takes the odds of the header", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={sim} you={YOU} whatIf={api} />);
    const plan = four().paths[0].plan!;
    const sheet = openPlan();
    fireEvent.click(within(sheet).getByRole("button", { name: `Try it: you're in ${plan.odds}%` }));
    expect(api.calls).toHaveLength(1);
    expect(api.calls[0].ask).toEqual({
      you: YOU,
      set: plan.weeks.map((week) => ({ week: week.week, game: week.game, median: week.median })),
    });
    await waitFor(() => expect(cardOdds()).toBe(`${tryIt.page.playoff}%`));
    expect(Math.abs(tryIt.page.playoff - plan.odds)).toBeLessThanOrEqual(1);
    const line = screen.getByRole("region", { name: "What-if" });
    expect(line.textContent).toContain(
      "Wk 12 win, beat median · Wk 13 win, beat median · Wk 14 lose, miss median",
    );
    await waitFor(() => expect(screen.queryByRole("dialog", { name: /^Your plan/ })).toBeNull());
    fireEvent.click(within(line).getByRole("button", { name: "Reset" }));
    expect(cardOdds()).toBe(`${sim.pages[YOU].goals.spot.odds}%`);
  });

  it("opens the plan of another team on its sheet, with no Try it", () => {
    render(<SimPage sim={sim} you={YOU} />);
    // The first other team with a Path for a spot.
    const fridge = sim.board
      .map((row) => row.roster_id)
      .find((id) => id !== YOU && sim.pages[id].finishes.spot.some((f) => f.paths.length > 0))!;
    const finish = sim.pages[fridge].finishes.spot.find((f) => f.paths.length > 0);
    expect(finish).toBeTruthy();
    const board = screen.getByRole("group", { name: /^League board/ });
    fireEvent.click(
      within(board)
        .getAllByRole("button")
        .find((bar) => Number(bar.getAttribute("data-roster")) === fridge)!,
    );
    const team = screen.getByRole("dialog", { name: sim.names[fridge] });
    const name = `${finish!.more_wins}-${sim.pages[fridge].wins_left - finish!.more_wins}`;
    fireEvent.click(within(team).getByRole("button", { name: new RegExp(`^${name},`) }));
    const panel = within(team).getByRole("region", { name: `Paths at ${name}` });
    fireEvent.click(within(panel).getAllByRole("button", { name: /^Week plan:/ })[0]);
    const plan = screen.getByRole("dialog", { name: /^Their plan to/ });
    expect(within(plan).queryByRole("button", { name: /^Try it/ })).toBeNull();
  });
});

describe("the status pill of the Your team card", () => {
  const cardPill = () =>
    within(screen.getByRole("region", { name: "Your team" }))
      .getAllByRole("button")[0]
      .querySelector("[data-status-pill]");

  it("shows no pill for Bo Girds in the hunt for a spot after week 11", () => {
    expect(sim.board.find((row) => row.roster_id === YOU)!.goals.spot.status).toBe("open");
    render(<SimPage sim={sim} you={YOU} />);
    expect(cardPill()).toBeNull();
  });

  it("shows a red Out pill when Your team is out of the Goal", () => {
    const out = structuredClone(sim);
    out.board.find((row) => row.roster_id === YOU)!.goals.spot.status = "out";
    render(<SimPage sim={out} you={YOU} />);
    expect(cardPill()?.textContent).toBe("Out");
    expect(cardPill()?.getAttribute("data-status-pill")).toBe("out");
  });

  it("names the best Goal locked on the green pill when Your team clinched", () => {
    const clinched = structuredClone(sim);
    const mine = clinched.board.find((row) => row.roster_id === YOU)!;
    mine.goals.spot.status = "in";
    mine.goals.bye.status = "in";
    render(<SimPage sim={clinched} you={YOU} />);
    expect(cardPill()?.textContent).toBe("Clinched bye");
    expect(cardPill()?.getAttribute("data-status-pill")).toBe("clinched");
  });
});

describe("the pills and the Clinch lines of the League board", () => {
  const rowOf = (id: number) =>
    within(screen.getByRole("group", { name: /^League board/ }))
      .getAllByRole("button")
      .find((bar) => Number(bar.getAttribute("data-roster")) === id)!;
  const pillOf = (id: number) => rowOf(id).querySelector("[data-status-pill]");

  it("shows a red Out pill for a team out of a spot and no pill for a team in the hunt", () => {
    render(<SimPage sim={sim} you={YOU} />);
    for (const team of sim.board) {
      const pill = pillOf(team.roster_id);
      const status = team.goals.spot.status;
      if (status === "open") expect(pill).toBeNull();
      else expect(pill?.textContent).toBe(status === "out" ? "Out" : "Clinched spot");
    }
    // The name of the bar reads the pill too, so a screen reader hears it.
    expect(rowOf(4).getAttribute("aria-label")).toContain("Out.");
    // NFC Least and Unsolicited Dak Picks are out of a spot after week 11.
    expect(pillOf(4)?.getAttribute("data-status-pill")).toBe("out");
    expect(pillOf(11)?.getAttribute("data-status-pill")).toBe("out");
  });

  it("names the best Goal locked on the green pill of a team that clinched", () => {
    const clinched = structuredClone(sim);
    const fridge = clinched.board.find((row) => row.roster_id === 3)!;
    fridge.goals.spot.status = "in";
    fridge.goals.bye.status = "in";
    render(<SimPage sim={clinched} you={YOU} />);
    expect(pillOf(3)?.textContent).toBe("Clinched bye");
    expect(pillOf(3)?.getAttribute("data-status-pill")).toBe("clinched");
  });

  it("shows each Clinch line of a spot under its team, with the Goal named", () => {
    render(<SimPage sim={sim} you={YOU} />);
    expect(
      within(rowOf(3)).getByText(
        "Clinches a spot with a win, a median win, and a Bo Girds loss to Puka Deez...",
      ),
    ).toBeTruthy();
    expect(
      within(rowOf(7)).getByText(
        "Out with a loss, a median miss, a median win by The Blue Tent, a 💿 🐑 median win, and 1 more result.",
      ),
    ).toBeTruthy();
    // The line of a team names at most 2 results beyond its own, then the count of the rest.
    expect(
      within(rowOf(9)).getByText(
        "Clinches a spot with a win, a median win, a Bo Girds loss to Puka Deez..., a Nico Collinsizer median miss, and 2 more results.",
      ),
    ).toBeTruthy();
    expect(rowOf(3).getAttribute("aria-label")).toContain("Clinches a spot with a win");
    // A team with no line for a spot shows none.
    expect(rowOf(10).querySelector("[data-clinch-line]")).toBeNull();
  });

  it("shows the Clinch lines of a bye on a tap of Bye, and none on a Seed Goal", () => {
    render(<SimPage sim={sim} you={YOU} />);
    fireEvent.click(screen.getByRole("radio", { name: "Bye" }));
    expect(within(rowOf(7)).getByText("Out of the bye race with any loss.")).toBeTruthy();
    // A name that starts with a vowel takes "an".
    expect(
      within(rowOf(6)).getByText(
        "Out of the bye race with a loss, a median miss, an Unsolicited Dak Picks loss to Maye d'force B with U, a NFC Least loss to Lil Fridge, and 1 more result.",
      ),
    ).toBeTruthy();
    expect(rowOf(3).querySelector("[data-clinch-line]")).toBeNull();
    fireEvent.click(screen.getByRole("radio", { name: "Seed" }));
    expect(document.querySelector("[data-clinch-line]")).toBeNull();
  });
});
