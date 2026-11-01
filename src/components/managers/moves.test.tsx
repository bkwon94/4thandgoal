/**
 * Tests for the Moves chapter. They render fixture entries and spread variants of them.
 * They read the three totals, the week order, the empty line, the add and drop lines, and both sides of a trade, and the teams it names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { sleeperHeadshot } from "@/lib/headshot";
import type { Manager, ManagerEntry } from "@/lib/manager-types";
import fixture from "@/fixtures/managers.json";
import { Moves } from "./moves";

afterEach(() => {
  cleanup();
});

const managers = fixture.managers as unknown as ManagerEntry[];
const MANAGERS_HREF = "/2026/managers/";

/* The fixture entry of one roster as a joined manager. The page fields the chapter does not read get plain values. */
function managerOf(rosterId: number, moves?: Partial<Manager["moves"]>): Manager {
  const entry = managers.find((manager) => manager.roster_id === rosterId)!;
  return { ...entry, moves: { ...entry.moves, ...moves }, standing: 1, rank: null, movement: null, odds: null, odds_change: null };
}

/* The label and the count of each total, as a reader reads them. */
function totalsIn() {
  const group = screen.getByRole("group", { name: "Move Totals" });
  return [...group.querySelectorAll("dt")].map((term) => [term.textContent, term.nextElementSibling?.textContent]);
}

function week(label: string) {
  return screen.getByRole("group", { name: label });
}

describe("Moves", () => {
  it("shows the heading and the three season totals", () => {
    render(<Moves manager={managerOf(1)} managers={managers} managersHref={MANAGERS_HREF} />);
    expect(screen.getByRole("heading", { level: 2 }).textContent).toBe("Moves");
    expect(totalsIn()).toEqual([
      ["Adds", "18"],
      ["Drops", "17"],
      ["Trades", "2"],
    ]);
  });

  it("shows a zero total as a count", () => {
    render(<Moves manager={managerOf(1, { trades: 0 })} managers={managers} managersHref={MANAGERS_HREF} />);
    expect(totalsIn()[2]).toEqual(["Trades", "0"]);
  });

  it("lists the weeks newest first, in the order of the file", () => {
    render(<Moves manager={managerOf(1)} managers={managers} managersHref={MANAGERS_HREF} />);
    const labels = screen.getAllByRole("group", { name: /^Week / }).map((group) => group.getAttribute("aria-label"));
    expect(labels).toEqual(["Week 6", "Week 5", "Week 4", "Week 3", "Week 2", "Week 1"]);
  });

  it("shows one quiet line for a week with no moves", () => {
    // London Cooking made no move in weeks 6, 5, 3, and 1.
    render(<Moves manager={managerOf(5)} managers={managers} managersHref={MANAGERS_HREF} />);
    expect(within(week("Week 6")).getByText("No moves.")).toBeTruthy();
    expect(screen.getAllByText("No moves.")).toHaveLength(4);
    expect(within(week("Week 4")).queryByText("No moves.")).toBeNull();
  });

  it("shows a free agent add before a drop, each with its position line and headshot", () => {
    render(<Moves manager={managerOf(1)} managers={managers} managersHref={MANAGERS_HREF} />);
    const rows = within(week("Week 6")).getAllByRole("listitem");
    expect(rows.map((row) => row.textContent)).toEqual([
      "Tampa Bay BuccaneersDEF · Free agent",
      "Cleveland BrownsDEF · Dropped",
    ]);
    expect(rows[0].querySelector("img")?.getAttribute("src")).toBe(sleeperHeadshot("TB"));
  });

  it("shows the bid of a waiver add", () => {
    render(<Moves manager={managerOf(1)} managers={managers} managersHref={MANAGERS_HREF} />);
    const row = within(week("Week 3")).getByText("Kalif Raymond").closest("li")!;
    expect(row.textContent).toBe("Kalif RaymondWR · $5 bid");
  });

  it("shows both sides of a trade with headshots", () => {
    render(<Moves manager={managerOf(1)} managers={managers} managersHref={MANAGERS_HREF} />);
    const trade = within(week("Week 4")).getByRole("group", { name: "Trade With Lil Fridge" });
    const gave = within(trade).getByRole("list", { name: "Gave" });
    const got = within(trade).getByRole("list", { name: "Got" });
    expect(within(gave).getByText("Stefon Diggs")).toBeTruthy();
    expect(within(gave).getByText("Derrick Henry")).toBeTruthy();
    expect(within(got).getByText("Rashee Rice")).toBeTruthy();
    expect(within(got).getByText("Bucky Irving")).toBeTruthy();
    expect(gave.querySelector("img")?.getAttribute("src")).toBe(sleeperHeadshot("2449"));
    // A traded player's quiet line is his position alone, never the position twice.
    expect(within(gave).getAllByText("WR")).toHaveLength(1);
  });

  it("names the other team of a trade and links the name to its manager page", () => {
    render(<Moves manager={managerOf(1)} managers={managers} managersHref={MANAGERS_HREF} />);
    const trade = within(week("Week 4")).getByRole("group", { name: "Trade With Lil Fridge" });
    expect(within(trade).getByRole("link", { name: "Lil Fridge" }).getAttribute("href")).toBe("/2026/managers/3/");
  });

  it("names a trade with two other rosters by both team names", () => {
    const [first] = managerOf(1).moves.weeks[2].trades;
    const weeks = [{ week: 7, adds: [], drops: [], trades: [{ ...first, with: [3, 4] }] }];
    render(<Moves manager={managerOf(1, { weeks })} managers={managers} managersHref={MANAGERS_HREF} />);
    expect(within(week("Week 7")).getByRole("group", { name: "Trade With Lil Fridge And Pukancun on 3" })).toBeTruthy();
  });
});
