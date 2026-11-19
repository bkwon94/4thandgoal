/**
 * Tests for the sim page on the real week 10 sim files of CPC and NorCal, with Bo Girds as Your team: the header, the ladder, the week
 * switch, the week card, the root-for card, the "about" numbers, and the What-if, over two local API answers and an API that is down.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { norcalWeekSim, weekSim } from "../fixtures/sim";
import { fakeWhatIfApi } from "../fixtures/what-if-api";
import { whatIfApi } from "../lib/what-if-api";
import { SimPage } from "./sim-page";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

// Bo Girds is roster 6 in CPC and roster 7 in NorCal.
const CPC_YOU = 6;
const NORCAL_YOU = 7;
const AVATARS = { [String(CPC_YOU)]: "/2026/week-10/avatars/6.png" };

const cpcPage = weekSim.pages[CPC_YOU];

describe("the sim page header", () => {
  it("shows the avatar, the name, the record, the weeks left, and the playoff odds of Your team", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} avatars={AVATARS} />);
    const header = screen.getByRole("region", { name: "Your team" });
    expect(within(header).getByRole("heading", { level: 1 }).textContent).toBe("Bo Girds");
    expect(header.querySelector("img")?.getAttribute("src")).toBe(AVATARS[String(CPC_YOU)]);
    expect(header.textContent).toContain("11-9");
    expect(header.textContent).toContain("4 weeks left");
    expect(header.textContent).toContain(`${cpcPage.playoff}%`);
  });
});

/* The text of an odds number as the page writes it: "about 1%" when the file flags it, else "58%". */
const odds = (value: number | null, about: boolean) => (value === null ? "–" : about ? `about ${value}%` : `${value}%`);

describe("the sentence of more wins", () => {
  it("shows the sentence of the file and opens the ladder with each count, its odds, and its chance", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} avatars={AVATARS} />);
    fireEvent.click(screen.getByRole("button", { name: new RegExp(cpcPage.sentence) }));
    const ladder = screen.getByRole("dialog", { name: "Wins left and your odds" });
    const rows = within(ladder).getAllByRole("listitem");
    expect(rows).toHaveLength(cpcPage.ladder.length);
    // The ladder reads from the most wins down, so the top row is the best case.
    const top = [...cpcPage.ladder].reverse();
    rows.forEach((row, index) => {
      const step = top[index];
      expect(row.textContent).toContain(`${step.more_wins} of ${cpcPage.wins_left}`);
      expect(row.textContent).toContain(odds(step.playoff, step.about));
      expect(row.textContent).toContain(`${step.chance}%`);
    });
  });
});

const weekSwitch = () => screen.getByRole("navigation", { name: "Weeks" });
const yourTeam = () => screen.getByRole("region", { name: "Your team" });
const weekCard = () => screen.getByRole("article", { name: /^Week \d+ vs / });

describe("the week switch", () => {
  it("has Wk 11 to Wk 14, then Playoffs, and opens on Wk 11", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    const items = within(weekSwitch()).getAllByRole("button");
    expect(items.map((item) => item.textContent)).toEqual(["Wk 11", "Wk 12", "Wk 13", "Wk 14", "Playoffs"]);
    expect(items[0].getAttribute("aria-current")).toBe("page");
    expect(weekCard().getAttribute("aria-label") ?? weekCard().textContent).toContain("Week 11");
  });

  it("opens the week page of each item", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    for (const week of cpcPage.weeks) {
      fireEvent.click(within(weekSwitch()).getByRole("button", { name: `Wk ${week.week}` }));
      expect(within(weekCard()).getByRole("heading").textContent).toBe(`Week ${week.week} vs ${weekSim.names[week.opponent]}`);
    }
    fireEvent.click(within(weekSwitch()).getByRole("button", { name: "Playoffs" }));
    expect(screen.queryByRole("article", { name: /^Week \d+ vs / })).toBeNull();
    expect(screen.getByRole("heading", { name: "Your playoff odds" })).toBeTruthy();
  });
});

const tiles = () => within(within(weekCard()).getByRole("group", { name: "Results" })).getAllByRole("button");
const tileNames = () => tiles().map((tile) => tile.querySelector("[data-result-name]")?.textContent);

describe("the week card", () => {
  it("shows four tiles in CPC, each with the odds after, the chance, and the wins it adds", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    expect(within(weekCard()).getByRole("heading").textContent).toBe("Week 11 vs Maye d'force B with U");
    const week = cpcPage.weeks[0];
    expect(tileNames()).toEqual(["Win, beat median", "Win, miss median", "Lose, beat median", "Lose, miss median"]);
    tiles().forEach((tile, index) => {
      const result = week.results[index];
      expect(tile.textContent).toContain(odds(result.playoff, result.about));
      expect(tile.textContent).toContain(`${Math.round(result.chance)}% likely`);
      expect(tile.textContent).toContain(["No wins", "+1 win", "+2 wins"][result.wins_added]);
    });
  });

  it("shows two tiles in NorCal, a win and a loss", () => {
    render(<SimPage sim={norcalWeekSim} you={NORCAL_YOU} />);
    expect(within(weekCard()).getByRole("heading").textContent).toBe("Week 11 vs The Mean Machine");
    expect(tileNames()).toEqual(["Win", "Lose"]);
    const [win, loss] = norcalWeekSim.pages[NORCAL_YOU].weeks[0].results;
    expect(tiles()[0].textContent).toContain(`${win.playoff}%`);
    expect(tiles()[1].textContent).toContain(`${loss.playoff}%`);
  });

  it("reads a flagged number as about X%", () => {
    // The real file flags no result of week 11, so this copy sets the flag on the first tile.
    const week = cpcPage.weeks[0];
    const flagged = { ...week, results: week.results.map((result, index) => ({ ...result, about: index === 0 })) };
    const sim = { ...weekSim, pages: { ...weekSim.pages, [CPC_YOU]: { ...cpcPage, weeks: [flagged, ...cpcPage.weeks.slice(1)] } } };
    render(<SimPage sim={sim} you={CPC_YOU} />);
    expect(tiles()[0].textContent).toContain(`about ${week.results[0].playoff}%`);
    expect(tiles()[1].textContent).not.toContain("about");
  });

  it("holds only the tiles of Your team, and no list of every game", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    for (const week of cpcPage.weeks) {
      fireEvent.click(within(weekSwitch()).getByRole("button", { name: `Wk ${week.week}` }));
      expect(tiles()).toHaveLength(week.results.length);
      expect(screen.queryByRole("table")).toBeNull();
    }
  });
});

describe("the root-for card", () => {
  it("says what a loss costs, then each result with its reason and the odds after it", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    const week = cpcPage.weeks[0];
    const card = screen.getByRole("article", { name: `If you lose, you drop to ${week.loss_playoff}%` });
    fireEvent.click(within(card).getByRole("button", { expanded: false }));
    const rows = within(card).getAllByRole("listitem");
    expect(rows).toHaveLength(week.root_for.length);
    rows.forEach((row, index) => {
      const root = week.root_for[index];
      expect(row.textContent).toContain(`${weekSim.names[root.winner]} beats ${weekSim.names[root.loser]}`);
      expect(row.textContent).toContain(root.reason);
      expect(row.textContent).toContain(`→ ${root.playoff}%`);
    });
  });

  it("opens from one row on a phone", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    const card = screen.getByRole("article", { name: /^If you lose/ });
    const toggle = within(card).getByRole("button");
    expect(toggle.getAttribute("aria-expanded")).toBe("false");
    fireEvent.click(toggle);
    expect(toggle.getAttribute("aria-expanded")).toBe("true");
  });

  it("shows in full from the tablet tier, with no toggle", () => {
    // The tablet tier matches, as at 1080x740.
    vi.spyOn(window, "matchMedia").mockImplementation(
      (query: string) => ({ matches: true, media: query, addEventListener: () => {}, removeEventListener: () => {} }) as unknown as MediaQueryList,
    );
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    const card = screen.getByRole("article", { name: /^If you lose/ });
    expect(within(card).queryByRole("button")).toBeNull();
    expect(within(card).getAllByRole("listitem")).toHaveLength(cpcPage.weeks[0].root_for.length);
  });

  it("writes a long team name in full, with no cut", () => {
    // The Blue Tent roots for Maye d'force B with U in week 11.
    render(<SimPage sim={weekSim} you={1} />);
    const card = screen.getByRole("article", { name: /^If you lose/ });
    const row = within(card).getAllByRole("listitem").find((item) => item.textContent?.includes("Maye"))!;
    expect(row.textContent).toContain("Maye d'force B with U beats Bo Girds");
    expect(row.querySelector(".truncate")).toBeNull();
  });
});

describe("the calls of the page", () => {
  it("makes no call on load or on a switch of weeks", () => {
    const fetch = vi.spyOn(globalThis, "fetch");
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    for (const label of ["Wk 12", "Wk 13", "Wk 14", "Playoffs", "Wk 11"]) {
      fireEvent.click(within(weekSwitch()).getByRole("button", { name: label }));
    }
    expect(fetch).not.toHaveBeenCalled();
    expect(api.calls).toHaveLength(0);
  });
});

/* The numbers of the answers of the local API on week-sim.json, from what-if-win-above.json and what-if-loss-below.json.
   With week 11 set to a win over Maye d'force B with U and the median, Bo Girds goes from 58% to 86%. */
const FILE_SENTENCE = "Win 5 of the 8 left and you're in.";
const WIN_ABOVE = { week: 11, game: "win", median: "above" } as const;
const LOSS_BELOW = { week: 11, game: "loss", median: "below" } as const;

const tile = (name: string) => tiles().find((entry) => entry.querySelector("[data-result-name]")?.textContent === name)!;
const setLine = () => screen.queryByRole("region", { name: "What-if" });
const weekItem = (label: string) => within(weekSwitch()).getByRole("button", { name: new RegExp(`^${label}`) });

describe("the What-if", () => {
  it("sets a result on a tap, shows the numbers of the API answer, and stays on its week", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    expect(yourTeam().textContent).toContain("58%");
    fireEvent.click(tile("Win, beat median"));
    // The call starts on the tap, with no wait.
    expect(api.calls.map((call) => call.ask)).toEqual([{ you: CPC_YOU, set: [WIN_ABOVE] }]);
    await waitFor(() => expect(yourTeam().textContent).toContain("86%"));
    expect(yourTeam().textContent).toContain("Win 3 of the 6 left and you're in.");
    expect(within(setLine()!).getByText(/Wk 11/).textContent).toContain("Wk 11 win, beat median");
    // Well past the old beat of 400 ms, the tapped week is still open.
    await new Promise((done) => setTimeout(done, 700));
    expect(weekItem("Wk 11").getAttribute("aria-current")).toBe("page");
    expect(weekItem("Wk 12").getAttribute("aria-current")).toBeNull();
    fireEvent.click(weekItem("Wk 12"));
    expect(within(weekCard()).getByRole("heading").textContent).toBe(`Week 12 vs ${weekSim.names[5]}`);
    // The root-for card of week 12 takes the numbers of the answer: 71% after a loss, and 75% if roster 10 wins.
    const card = screen.getByRole("article", { name: "If you lose, you drop to 71%" });
    fireEvent.click(within(card).getByRole("button", { expanded: false }));
    expect(within(card).getAllByRole("listitem")[0].textContent).toContain(
      `${weekSim.names[10]} beats ${weekSim.names[12]}`,
    );
    expect(within(card).getAllByRole("listitem")[0].textContent).toContain("→ 75%");
    // Back on week 11, the set tile shows as pressed.
    fireEvent.click(weekItem("Wk 11"));
    expect(tile("Win, beat median").getAttribute("aria-pressed")).toBe("true");
    expect(tile("Lose, miss median").getAttribute("aria-pressed")).toBe("false");
  });

  it("shows the odds of the answer on the Playoffs page after a set result, and the file after a Reset", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    const stats = () => screen.getByRole("article", { name: "Your playoff odds" });
    const stat = (label: string) => within(stats()).getByText(label).parentElement!.textContent;
    fireEvent.click(weekItem("Playoffs"));
    // The file: 58% to make the playoffs, 10% to get a bye, and 9.7% to win the title, which shows as 10%.
    expect(stat("Make the playoffs")).toContain("58%");
    expect(stat("Get a bye")).toContain("10%");
    expect(stat("Win the title")).toContain("10%");
    fireEvent.click(weekItem("Wk 11"));
    fireEvent.click(tile("Win, beat median"));
    await waitFor(() => expect(yourTeam().textContent).toContain("86%"));
    fireEvent.click(weekItem("Playoffs"));
    // The answer: 86%, 27%, and 17.0%, so the page agrees with the header.
    expect(stat("Make the playoffs")).toContain("86%");
    expect(stat("Get a bye")).toContain("27%");
    expect(stat("Win the title")).toContain("17%");
    fireEvent.click(within(setLine()!).getByRole("button", { name: "Reset" }));
    await waitFor(() => expect(stat("Make the playoffs")).toContain("58%"));
    expect(stat("Get a bye")).toContain("10%");
  });

  it("clears the set line on Reset and shows the numbers of the file again, with no call", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(tile("Win, beat median"));
    await waitFor(() => expect(yourTeam().textContent).toContain("86%"));
    fireEvent.click(within(setLine()!).getByRole("button", { name: "Reset" }));
    // The set line closes with a short exit, then leaves the page.
    await waitFor(() => expect(setLine()).toBeNull());
    await waitFor(() => expect(yourTeam().textContent).toContain(FILE_SENTENCE));
    expect(yourTeam().textContent).toContain("58%");
    expect(api.calls).toHaveLength(1);
    fireEvent.click(weekItem("Wk 11"));
    expect(tile("Win, beat median").getAttribute("aria-pressed")).toBe("false");
  });

  it("cancels the call before a new tap and shows the answer of the last tap", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(tile("Win, beat median"));
    fireEvent.click(tile("Lose, miss median"));
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
    fireEvent.click(weekItem("Wk 11"));
    expect(cpcPage.weeks[0].results[3].playoff).toBe(41);
    expect(tile("Lose, miss median").textContent).toContain("42%");
    expect(tile("Win, beat median").textContent).toContain(`${cpcPage.weeks[0].results[0].playoff}%`);
  });

  it("clears the result of a week on a second tap of its tile, with no call", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={api} />);
    fireEvent.click(tile("Win, beat median"));
    fireEvent.click(tile("Win, beat median"));
    expect(api.calls).toHaveLength(1);
    expect(api.calls[0].signal.aborted).toBe(true);
    await waitFor(() => expect(setLine()).toBeNull());
    expect(tile("Win, beat median").getAttribute("aria-pressed")).toBe("false");
    expect(yourTeam().textContent).toContain(FILE_SENTENCE);
  });

  it("keeps the numbers of the file and shows one line when the API is down", async () => {
    // A real call to port 9, which nothing serves, so the connection is refused as when the API is down.
    render(<SimPage sim={weekSim} you={CPC_YOU} whatIf={whatIfApi({ url: "http://127.0.0.1:9", client: "cpc" })} />);
    fireEvent.click(tile("Win, beat median"));
    await screen.findByText("The What-if is not available now.");
    fireEvent.click(weekItem("Wk 11"));
    fireEvent.click(tile("Lose, miss median"));
    await waitFor(() => expect(tile("Lose, miss median").getAttribute("aria-pressed")).toBe("false"));
    expect(screen.getAllByText("The What-if is not available now.")).toHaveLength(1);
    await waitFor(() => expect(setLine()).toBeNull());
    expect(yourTeam().textContent).toContain("58%");
    expect(yourTeam().textContent).toContain(FILE_SENTENCE);
    expect(tile("Win, beat median").getAttribute("aria-pressed")).toBe("false");
  });
});
