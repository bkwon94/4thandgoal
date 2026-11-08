/**
 * Tests for the Trend tile: a tile with a small chart of its number from week 1 to the page week.
 * They read the chart by its role and its text, and each bar by the week it holds.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Tile } from "./tile";

afterEach(() => cleanup());

const TOP = [156.92, 156.52, 140.6, 145.63, 158.96, 126.79, 148.13, 134.1].map((value, index) => ({
  week: index + 1,
  value,
}));

describe("Tile with a trend", () => {
  it("draws one bar per week and lights the bar of the page week", () => {
    render(<Tile label="Top Score" value="134.1" trend={{ points: TOP, week: 8, kind: "bars", text: "Down from week 7." }} />);
    const chart = screen.getByRole("img", { name: "Down from week 7." });
    const bars = [...chart.querySelectorAll("[data-week]")];
    expect(bars.map((bar) => bar.getAttribute("data-week"))).toEqual(["1", "2", "3", "4", "5", "6", "7", "8"]);
    expect(bars.filter((bar) => bar.hasAttribute("data-lit")).map((bar) => bar.getAttribute("data-week"))).toEqual(["8"]);
  });

  it("draws a stepped area for a step trend", () => {
    render(<Tile label="Median" value="99.6" trend={{ points: TOP, week: 8, kind: "step", text: "Lowest of the season." }} />);
    const chart = screen.getByRole("img", { name: "Lowest of the season." });
    expect(chart.querySelector("[data-step]")).toBeTruthy();
  });

  it("draws a dot only at each week with a count above zero for a dots trend", () => {
    const trades = [1, 0, 0, 1, 0, 0, 0, 0].map((value, index) => ({ week: index + 1, value }));
    render(<Tile label="Trades" value={2} trend={{ points: trades, week: 8, kind: "dots", text: "Trades in week 1 and week 4." }} />);
    const chart = screen.getByRole("img", { name: "Trades in week 1 and week 4." });
    expect([...chart.querySelectorAll("[data-week]")].map((dot) => dot.getAttribute("data-week"))).toEqual(["1", "4"]);
  });

  it("reads its label, its number, and the text of its trend", () => {
    render(<Tile label="Top Score" value="134.1" note="Teehee" trend={{ points: TOP, week: 8, kind: "bars", text: "Down from week 7." }} />);
    expect(screen.getByText("134.1")).toBeTruthy();
    expect(screen.getByRole("img").getAttribute("aria-label")).toBe("Down from week 7.");
  });

  it("shows no chart with no trend", () => {
    render(<Tile label="Closest" value="1.43" note="The Blue Tent over London Cooking" />);
    expect(screen.queryByRole("img")).toBeNull();
  });
});
