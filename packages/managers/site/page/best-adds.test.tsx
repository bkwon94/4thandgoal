/**
 * Tests for the Best Adds chapter. They render the fixture entry and spread variants of it.
 * They read the rows a reader sees: the order, the quiet lines, the numbers, and the empty line.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Manager } from "../schema/manager-types";
import { BestAdds } from "./best-adds";
import { managers as fixture } from "../fixtures/managers";

afterEach(() => {
  cleanup();
});

/* The first fixture entry as a joined manager. The join fields do not show in this chapter. */
const manager = {
  ...fixture.managers[0],
  standing: 1,
  rank: null,
  movement: null,
  odds: null,
  odds_change: null,
} as Manager;

/* The text of each row in order, one string per line of the row. */
function rowLines() {
  const list = screen.getByRole("list");
  return within(list)
    .getAllByRole("listitem")
    .map((row) => [...row.querySelectorAll("[data-line]")].map((line) => line.textContent));
}

describe("BestAdds", () => {
  it("shows the heading and the three adds in order", () => {
    render(<BestAdds manager={manager} />);
    expect(screen.getByRole("heading", { level: 2 }).textContent).toBe("Best Adds");
    expect(rowLines()).toEqual([
      ["Dallas Goedert", "TE · Added week 5 · 3 games", "23.2", "26.3 proj"],
      ["Cleveland Browns", "DEF · Added week 4 · 2 games", "23.15", "15.9 proj"],
      ["Jacksonville Jaguars", "DEF · Added week 1 · 1 game", "13.5", "9.1 proj"],
    ]);
  });

  it("shows a headshot from the Sleeper CDN for each add", () => {
    render(<BestAdds manager={manager} />);
    const images = within(screen.getByRole("list")).getAllByRole("presentation");
    expect(images.map((img) => img.getAttribute("src"))).toEqual([
      "https://sleepercdn.com/content/nfl/players/5022.jpg",
      "https://sleepercdn.com/content/nfl/players/CLE.jpg",
      "https://sleepercdn.com/content/nfl/players/JAX.jpg",
    ]);
  });

  it("leaves the position out of the line when the position is null", () => {
    const add = { ...manager.best_adds[0], position: null };
    render(<BestAdds manager={{ ...manager, best_adds: [add] }} />);
    expect(rowLines()).toEqual([["Dallas Goedert", "Added week 5 · 3 games", "23.2", "26.3 proj"]]);
  });

  it("reads one quiet line with no adds", () => {
    render(<BestAdds manager={{ ...manager, best_adds: [] }} />);
    expect(screen.getByText("No adds yet.")).toBeTruthy();
    expect(screen.queryByRole("list")).toBeNull();
  });
});
