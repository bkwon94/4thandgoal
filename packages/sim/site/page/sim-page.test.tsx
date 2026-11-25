/**
 * Tests for the sim page on the real week 10 sim files of CPC and NorCal, with Bo Girds as Your team: the header, the Finish list, the week
 * card, the "about" numbers, and the What-if, over two local API answers and an API that is down.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, spyOn } from "bun:test";
import { norcalWeekSim, weekSim } from "../fixtures/sim";
import { fakeWhatIfApi } from "../fixtures/what-if-api";
import { whatIfApi } from "../lib/what-if-api";
import { SimPage } from "./sim-page";

// The happy-dom window is 1024 px wide, so matchMedia would match the tablet tier. The stub matches no query, so a test
// sees the phone tier unless it spies on matchMedia itself.
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

// Bo Girds is roster 6 in CPC and roster 7 in NorCal.
const CPC_YOU = 6;
const NORCAL_YOU = 7;
const AVATARS = { [String(CPC_YOU)]: "/2026/week-10/avatars/6.png" };

const cpcPage = weekSim.pages[CPC_YOU];

describe("the sim page header", () => {
  it("shows the avatar, the name, the record, the weeks left, and the playoff odds of Your team", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} avatars={AVATARS} />);
    // Bo Girds opens on the bye in week 10, so the card shows the playoff odds after a tap of Spot.
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    const header = screen.getByRole("region", { name: "Your team" });
    expect(header.textContent).toContain("Bo Girds");
    expect(header.querySelector("img")?.getAttribute("src")).toBe(AVATARS[String(CPC_YOU)]);
    expect(header.textContent).toContain("11-9");
    expect(screen.getByText("After week 10 · 4 weeks left")).toBeTruthy();
    expect(header.textContent).toContain(`${cpcPage.playoff}%`);
  });
});

/* The text of an odds number as the page writes it: "about 1%" when the file flags it, else "58%". */
const odds = (value: number | null, about: boolean) =>
  value === null ? "–" : about ? `about ${value}%` : `${value}%`;

describe("the sentence of more wins and the Finish list", () => {
  it("shows the sentence of the file and one bar per Finish with its odds of a spot, from the most wins down", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} avatars={AVATARS} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    expect(yourTeam().textContent).toContain(cpcPage.sentence);
    const list = screen.getByRole("group", { name: "Finish list for a playoff spot" });
    const rows = within(list).getAllByRole("button");
    expect(rows).toHaveLength(cpcPage.finishes.spot.length);
    rows.forEach((row, index) => {
      const finish = cpcPage.finishes.spot[index];
      expect(row.getAttribute("data-finish")).toBe(
        `${finish.more_wins}-${cpcPage.wins_left - finish.more_wins}`,
      );
      expect(row.textContent).toContain(odds(finish.odds, finish.about));
      expect(row.textContent).toContain(`${Math.round(finish.chance)}% likely`);
    });
  });
});

const yourTeam = () => screen.getByRole("region", { name: "Your team" });
const weekCard = () => screen.getByRole("article", { name: /^Week \d+ vs / });
const card = cpcPage.week_card!;

const tiles = () =>
  within(within(weekCard()).getByRole("group", { name: "Results" })).getAllByRole("button");
const tileNames = () =>
  tiles().map((tile) => tile.querySelector("[data-result-name]")?.textContent);

describe("the week card", () => {
  it("shows four tiles in CPC, each with the odds after it and the chance", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    expect(within(weekCard()).getByRole("heading").textContent).toBe(
      "Week 11 vs Maye d'force B with U",
    );
    expect(tileNames()).toEqual([
      "Win and beat the median",
      "Win, but miss the median",
      "Lose, but beat the median",
      "Lose and miss the median",
    ]);
    tiles().forEach((tile, index) => {
      expect(tile.textContent).toContain(
        odds(card.goals.spot.odds[index], card.results[index].about),
      );
      expect(tile.textContent).toContain(`${Math.round(card.results[index].chance)}% likely`);
    });
  });

  it("shows two tiles in NorCal, a win and a loss", () => {
    render(<SimPage sim={norcalWeekSim} you={NORCAL_YOU} />);
    expect(within(weekCard()).getByRole("heading").textContent).toBe("Week 11 vs The Mean Machine");
    expect(tileNames()).toEqual(["Win", "Lose"]);
    const page = norcalWeekSim.pages[NORCAL_YOU];
    const goal = page.week_card!.goals[page.open_goal!];
    expect(tiles()[0].textContent).toContain(`${goal.odds[0]}%`);
    expect(tiles()[1].textContent).toContain(`${goal.odds[1]}%`);
  });

  it("reads a flagged number as about X%", () => {
    // The real file flags no result of week 11, so this copy sets the flag on the first tile.
    const flagged = {
      ...card,
      results: card.results.map((result, index) => ({ ...result, about: index === 0 })),
    };
    const sim = {
      ...weekSim,
      pages: { ...weekSim.pages, [CPC_YOU]: { ...cpcPage, week_card: flagged } },
    };
    render(<SimPage sim={sim} you={CPC_YOU} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    expect(tiles()[0].textContent).toContain(`about ${card.goals.spot.odds[0]}%`);
    expect(tiles()[1].textContent).not.toContain("about");
  });

  it("writes a long team name in full in the root-for list, with no cut", async () => {
    render(<SimPage sim={weekSim} you={1} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    const list = await within(weekCard()).findByRole("list", { name: "Games to root for" });
    expect(list.textContent).toContain("Maye d'force B with U");
    expect(list.querySelector(".truncate")).toBeNull();
  });
});

describe("the calls of the page", () => {
  it("makes no call on load or on a switch of Goal", () => {
    const fetch = spyOn(globalThis, "fetch");
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    fireEvent.click(screen.getByRole("radio", { name: "Bye" }));
    expect(fetch).not.toHaveBeenCalled();
    expect(api.calls).toHaveLength(0);
  });
});

/* The numbers of the answers of the local API on week-sim.json, from what-if-win-above.json and what-if-loss-below.json.
   With week 11 set to a win over Maye d'force B with U and the median, Bo Girds goes from 58% to 86%. */
const FILE_SENTENCE = "Win 5 of the 8 left and you're in.";
const WIN_ABOVE = { week: 11, game: "win", median: "above" } as const;
const LOSS_BELOW = { week: 11, game: "loss", median: "below" } as const;

const tile = (name: string) =>
  tiles().find((entry) => entry.querySelector("[data-result-name]")?.textContent === name)!;
const setLine = () => screen.queryByRole("region", { name: "What-if" });

describe("the What-if", () => {
  /* The API is down in each test of this block, as a refused connection makes it, so no test opens a socket. A test
     that needs an answer passes the one fake of the port. */
  beforeEach(() => {
    spyOn(globalThis, "fetch").mockImplementation((() =>
      Promise.reject(new TypeError("fetch failed"))) as unknown as typeof fetch);
  });

  it("sets a result on a tap and shows the numbers of the API answer", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    expect(yourTeam().textContent).toContain("58%");
    fireEvent.click(tile("Win and beat the median"));
    // The call starts on the tap, with no wait.
    expect(api.calls.map((call) => call.ask)).toEqual([{ you: CPC_YOU, set: [WIN_ABOVE] }]);
    await waitFor(() => expect(yourTeam().textContent).toContain("86%"));
    expect(yourTeam().textContent).toContain("Win 3 of the 6 left and you're in.");
    expect(within(setLine()!).getByText(/Wk 11/).textContent).toContain("Wk 11 win, beat median");
    expect(tile("Win and beat the median").getAttribute("aria-pressed")).toBe("true");
    expect(tile("Lose and miss the median").getAttribute("aria-pressed")).toBe("false");
  });

  it("clears the set line on Reset and shows the numbers of the file again, with no call", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    fireEvent.click(tile("Win and beat the median"));
    await waitFor(() => expect(yourTeam().textContent).toContain("86%"));
    fireEvent.click(within(setLine()!).getByRole("button", { name: "Reset" }));
    // The set line closes with a short exit, then leaves the page.
    await waitFor(() => expect(setLine()).toBeNull());
    await waitFor(() => expect(yourTeam().textContent).toContain(FILE_SENTENCE));
    expect(yourTeam().textContent).toContain("58%");
    expect(api.calls).toHaveLength(1);
    expect(tile("Win and beat the median").getAttribute("aria-pressed")).toBe("false");
  });

  it("cancels the call before a new tap and shows the answer of the last tap", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    fireEvent.click(tile("Win and beat the median"));
    fireEvent.click(tile("Lose and miss the median"));
    expect(api.calls.map((call) => call.ask)).toEqual([
      { you: CPC_YOU, set: [WIN_ABOVE] },
      { you: CPC_YOU, set: [LOSS_BELOW] },
    ]);
    expect(api.calls[0].signal.aborted).toBe(true);
    expect(api.calls[1].signal.aborted).toBe(false);
    await waitFor(() => expect(yourTeam().textContent).toContain("42%"));
    expect(yourTeam().textContent).toContain("Win 5 of the 6 left and you're in.");
    expect(within(setLine()!).getByText(/Wk 11/).textContent).toContain("Wk 11 lose, miss median");
    // The pressed tile takes the odds of the answer, so it agrees with the header: 42%, where the file had 41%.
    expect(card.goals.spot.odds[3]).toBe(41);
    expect(tile("Lose and miss the median").textContent).toContain("42%");
    expect(tile("Win and beat the median").textContent).toContain(`${card.goals.spot.odds[0]}%`);
  });

  it("clears the result of a week on a second tap of its tile, with no call", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    fireEvent.click(tile("Win and beat the median"));
    fireEvent.click(tile("Win and beat the median"));
    expect(api.calls).toHaveLength(1);
    expect(api.calls[0].signal.aborted).toBe(true);
    await waitFor(() => expect(setLine()).toBeNull());
    expect(tile("Win and beat the median").getAttribute("aria-pressed")).toBe("false");
    expect(yourTeam().textContent).toContain(FILE_SENTENCE);
  });

  it("keeps the numbers of the file and shows one line when the API is down", async () => {
    // The real client of the port, with the refused call of the beforeEach, as when the API is down.
    render(
      <SimPage
        sim={weekSim}
        you={CPC_YOU}
        whatIf={whatIfApi({ url: "http://127.0.0.1:9", client: "cpc" })}
      />,
    );
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    fireEvent.click(tile("Win and beat the median"));
    await screen.findByText("The What-if is not available now.");
    fireEvent.click(tile("Lose and miss the median"));
    await waitFor(() =>
      expect(tile("Lose and miss the median").getAttribute("aria-pressed")).toBe("false"),
    );
    expect(screen.getAllByText("The What-if is not available now.")).toHaveLength(1);
    await waitFor(() => expect(setLine()).toBeNull());
    expect(yourTeam().textContent).toContain("58%");
    expect(yourTeam().textContent).toContain(FILE_SENTENCE);
    expect(tile("Win and beat the median").getAttribute("aria-pressed")).toBe("false");
  });
});
