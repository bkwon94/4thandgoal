/**
 * Tests for the Season So Far chapter. They render fixture entries and spread variants of them.
 * They read the dots, the week labels, and the legend of the points line, the bench lines, and the four season stats.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Manager } from "@/lib/manager-types";
import fixture from "@/fixtures/managers.json";
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

/* The label, the number, and the quiet line of each season stat, as a reader reads them. */
function stats() {
  const group = screen.getByRole("group", { name: "Season Numbers" });
  return [...group.querySelectorAll("dt")].map((term) => [
    term.textContent,
    term.nextElementSibling?.textContent,
    term.nextElementSibling?.nextElementSibling?.textContent ?? null,
  ]);
}

/* A fixture entry with its results swapped for the given ones, week 1 first. */
function withResults(results: (boolean | null)[]): Manager {
  const manager = managerOf(0);
  return { ...manager, weeks: manager.weeks.map((week, i) => ({ ...week, won: results[i] })) };
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

  it("shows the season high, the season low, the streak, and the record against the median", () => {
    // Brock 'N' Roll peaked in week 5, bottomed out in week 4, lost week 6, and beat the median in weeks 1, 2, 3, and 5.
    render(<SeasonSoFar manager={managerOf(0)} />);
    expect(stats()).toEqual([
      ["Season High", "158.91", "week 5"],
      ["Season Low", "88.22", "week 4"],
      ["Streak", "L1", null],
      ["Against The Median", "4-2", "wins above the median"],
    ]);
  });

  it("counts the streak from the last week back to the first change of result", () => {
    render(<SeasonSoFar manager={withResults([false, true, false, true, true, true])} />);
    expect(stats()[2]).toEqual(["Streak", "W3", null]);
  });

  it("ends the streak at a week with no result", () => {
    render(<SeasonSoFar manager={withResults([true, true, null, false, false, false])} />);
    expect(stats()[2]).toEqual(["Streak", "L3", null]);
  });

  it("shows a dash for the streak when the last week has no result", () => {
    render(<SeasonSoFar manager={withResults([true, true, true, true, true, null])} />);
    expect(stats()[2]).toEqual(["Streak", "—", null]);
  });

  it("does not show the awards shelf", () => {
    render(<SeasonSoFar manager={managerOf(10)} />);
    expect(screen.queryByRole("group", { name: "Awards Shelf" })).toBeNull();
    expect(screen.queryByText("Top Scorer")).toBeNull();
  });
});
