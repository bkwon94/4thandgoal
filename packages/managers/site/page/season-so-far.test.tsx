/**
 * Tests for the Season So Far chapter. They render fixture entries and spread variants of them.
 * They read the dots, the week labels, and the legend of the points line, the bench lines, and the season tiles.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Manager } from "../schema/manager-types";
import { managers as fixture } from "../fixtures/managers";
import { SeasonSoFar } from "./season-so-far";

afterEach(() => {
  cleanup();
});

/* A fixture entry with the joined fields of the loader. The chapter reads none of them. */
function managerOf(index: number, change: Partial<Manager> = {}): Manager {
  const entry = fixture.managers[index] as Manager;
  return { ...entry, standing: 1, rank: null, movement: null, odds: null, odds_change: null, ...change };
}

/* The dots of the points line by the result each one names. */
function dots(result?: string) {
  const line = screen.getByRole("img", { name: "Points per week against the league median" });
  return line.querySelectorAll(result ? `[data-result="${result}"]` : "[data-result]");
}

/* The label, the number, and the note of each season tile, as a reader reads them. */
function stats() {
  const group = screen.getByRole("group", { name: "Season Numbers" });
  return [...group.children].map((tile) => [...tile.children].map((line) => line.textContent));
}

describe("SeasonSoFar", () => {
  it("shows the chapter heading", () => {
    render(<SeasonSoFar manager={managerOf(0)} />);
    expect(screen.getByRole("heading", { level: 2 }).textContent).toBe("Season So Far");
  });

  it("draws one dot per week, filled for each win", () => {
    // Brock 'N' Roll won weeks 1 and 5 and lost the other four.
    render(<SeasonSoFar manager={managerOf(0)} />);
    expect(dots()).toHaveLength(6);
    expect(dots("win")).toHaveLength(2);
    expect(dots("loss")).toHaveLength(4);
  });

  it("marks a week with no result apart from a win and a loss", () => {
    const manager = managerOf(0);
    const weeks = manager.weeks.map((week) => (week.week === 3 ? { ...week, won: null } : week));
    render(<SeasonSoFar manager={{ ...manager, weeks }} />);
    expect(dots("none")).toHaveLength(1);
    expect(dots("loss")).toHaveLength(3);
  });

  it("labels the first and the last week only", () => {
    render(<SeasonSoFar manager={managerOf(0)} />);
    expect(screen.getByText("Week 1")).toBeTruthy();
    expect(screen.getByText("Week 6")).toBeTruthy();
    expect(screen.queryByText("Week 2")).toBeNull();
  });

  it("names each mark of the chart in one legend under it", () => {
    render(<SeasonSoFar manager={managerOf(0)} />);
    const legend = screen.getByRole("list", { name: "Legend" });
    const keys = within(legend).getAllByRole("listitem").map((item) => item.textContent);
    expect(keys).toEqual(["Points", "League Median", "Win", "Loss"]);
    expect(screen.queryByText("Points per week against the league median.")).toBeNull();
  });

  it("gives the points line a short summary for a screen reader", () => {
    render(<SeasonSoFar manager={managerOf(0)} />);
    const line = screen.getByRole("img", { name: "Points per week against the league median" });
    expect(line.textContent).toContain("Weeks 1 to 6: 2 wins, 4 losses.");
  });

  it("shows the bench total and one sentence with the best lineup and the worst week", () => {
    render(<SeasonSoFar manager={managerOf(0)} />);
    expect(screen.getByText("Points Left On The Bench")).toBeTruthy();
    expect(screen.getByText("46.54")).toBeTruthy();
    expect(
      screen.getByText(
        "Your best lineup would have scored 46.54 more points this season. Worst in week 2: 19.4 points, Stefon Diggs sat.",
      ),
    ).toBeTruthy();
  });

  it("reads that the best lineup matched the starters with no worst week", () => {
    render(<SeasonSoFar manager={managerOf(0, { bench: { total: 0, worst: null } })} />);
    expect(screen.getByText("Your best lineup matched your starters every week.")).toBeTruthy();
    expect(screen.queryByText(/Worst in week/)).toBeNull();
  });

  it("reads one quiet line with no bench data", () => {
    render(<SeasonSoFar manager={managerOf(0, { bench: null })} />);
    expect(screen.getByText("No bench data yet.")).toBeTruthy();
    expect(screen.queryByText("46.54")).toBeNull();
  });

  it("shows three tiles: the points for, the record against the median, and the high week", () => {
    // Brock 'N' Roll scored 685.01, peaked in week 5, and beat the median in weeks 1, 2, 3, and 5.
    render(<SeasonSoFar manager={managerOf(0)} />);
    expect(stats()).toEqual([
      ["Points For", "685.01"],
      ["Vs Median", "4-2"],
      ["High Week", "158.91", "week 5"],
    ]);
  });

  it("does not show the awards shelf", () => {
    render(<SeasonSoFar manager={managerOf(10)} />);
    expect(screen.queryByRole("group", { name: "Awards Shelf" })).toBeNull();
    expect(screen.queryByText("Top Scorer")).toBeNull();
  });

  it("draws the median line with the median game", () => {
    render(<SeasonSoFar manager={managerOf(0)} />);
    const line = screen.getByRole("img", { name: "Points per week against the league median" });
    expect(line.querySelectorAll("[data-median]")).toHaveLength(1);
  });

  it("draws no median line, no median key, and no median tile for a league with no median game", () => {
    const manager = managerOf(0);
    render(<SeasonSoFar manager={{ ...manager, weeks: manager.weeks.map((week) => ({ ...week, median: null })) }} />);
    const line = screen.getByRole("img", { name: "Points per week" });
    expect(line.querySelectorAll("[data-median]")).toHaveLength(0);
    expect(line.textContent).toContain("Weeks 1 to 6: 2 wins, 4 losses.");
    expect(line.textContent).not.toContain("median");
    const legend = screen.getByRole("list", { name: "Legend" });
    expect(within(legend).getAllByRole("listitem").map((item) => item.textContent)).toEqual(["Points", "Win", "Loss"]);
    expect(stats().map(([label]) => label)).toEqual(["Points For", "High Week"]);
  });
});
