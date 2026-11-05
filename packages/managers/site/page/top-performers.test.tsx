/**
 * Tests for the Top Performers chapter. They render the fixture entry and spread variants of it.
 * They read the rows a reader sees: the order, the quiet lines, the numbers, and the empty line.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Manager } from "../schema/manager-types";
import { managers as fixture } from "../fixtures/managers";
import { TopPerformers } from "./top-performers";

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

describe("TopPerformers", () => {
  it("shows the heading and the five performers in order", () => {
    render(<TopPerformers manager={manager} />);
    expect(screen.getByRole("heading", { level: 2 }).textContent).toBe("Top Performers");
    expect(rowLines()).toEqual([
      ["Brock Purdy", "QB · 6 starts", "127.92", "21.3 a game"],
      ["Christian Watson", "WR · 7 starts", "112.5", "16.1 a game"],
      ["Brock Bowers", "TE · 5 starts", "78.5", "15.7 a game"],
      ["Mike Evans", "WR · 6 starts", "75.5", "12.6 a game"],
      ["Derrick Henry", "RB · 3 starts", "72.4", "24.1 a game"],
    ]);
  });

  it("shows a headshot from the Sleeper CDN for each performer", () => {
    render(<TopPerformers manager={manager} />);
    const images = within(screen.getByRole("list")).getAllByRole("presentation");
    expect(images[0].getAttribute("src")).toBe("https://sleepercdn.com/content/nfl/players/8183.jpg");
    expect(images).toHaveLength(5);
  });

  it("reads one start in the singular and leaves out a null position", () => {
    const performer = { ...manager.top_performers[0], position: null, games: 1, points: 21.3, per_game: 21.3 };
    render(<TopPerformers manager={{ ...manager, top_performers: [performer] }} />);
    expect(rowLines()).toEqual([["Brock Purdy", "1 start", "21.3", "21.3 a game"]]);
  });

  it("reads one quiet line with no performers", () => {
    render(<TopPerformers manager={{ ...manager, top_performers: [] }} />);
    expect(screen.getByText("No starts yet.")).toBeTruthy();
    expect(screen.queryByRole("list")).toBeNull();
  });
});
