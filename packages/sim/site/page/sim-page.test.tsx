/**
 * Tests for the sim page on the real week 10 sim files of CPC and NorCal, with Bo Girds as Your team.
 * They check the header, the ladder, the week switch, the week card, the root-for card, and the "about" numbers.
 */
import "@cpc/design/ui/sheet-jsdom";
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { norcalWeekSim, weekSim } from "../fixtures/sim";
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

const tiles = () => within(weekCard()).getAllByRole("group");

describe("the week card", () => {
  it("shows four tiles in CPC, each with the odds after, the chance, and the wins it adds", () => {
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    expect(within(weekCard()).getByRole("heading").textContent).toBe("Week 11 vs Maye d'force B with U");
    const week = cpcPage.weeks[0];
    expect(tiles().map((tile) => tile.getAttribute("aria-label"))).toEqual([
      "Win, beat median",
      "Win, miss median",
      "Lose, beat median",
      "Lose, miss median",
    ]);
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
    expect(tiles().map((tile) => tile.getAttribute("aria-label"))).toEqual(["Win", "Lose"]);
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
      expect(screen.getAllByRole("group")).toHaveLength(week.results.length);
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
    render(<SimPage sim={weekSim} you={CPC_YOU} />);
    for (const label of ["Wk 12", "Wk 13", "Wk 14", "Playoffs", "Wk 11"]) {
      fireEvent.click(within(weekSwitch()).getByRole("button", { name: label }));
    }
    expect(fetch).not.toHaveBeenCalled();
  });
});
