/**
 * Tests for the home parts of the midseason package on the real build of CPC 2026 week 8 in the package fixture.
 * They read what a manager sees on the home page: the takeover through the end week, then the report tile.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { midseason } from "../fixtures/midseason";
import { ReportTile } from "./report-tile";
import { Takeover, takeoverOn } from "./takeover";

afterEach(cleanup);

describe("takeoverOn", () => {
  it("holds the takeover through the week after the report, then gives way to the tile", () => {
    // The report counts week 8, so the takeover ends after week 9.
    expect(midseason.takeover_end_week).toBe(9);
    expect([8, 9, 10, 11].map((week) => takeoverOn(midseason, week))).toEqual([true, true, false, false]);
  });
});

describe("Takeover", () => {
  it("shows the opener, the title race, with the leaders, the record leader, and a link to the report", () => {
    render(<Takeover report={midseason} href="/midseason/2026/" />);
    const takeover = within(screen.getByRole("region", { name: "2026 Midseason Report" }));
    expect(takeover.getByText("2026 midseason report // Week 8")).toBeTruthy();
    // The intro of the home page holds the h1, so the title of the opener is a level 2 heading.
    expect(takeover.getByRole("heading", { level: 2, name: "The title race" })).toBeTruthy();
    expect(takeover.getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      "Title odds16.8%London Cooking",
      "Title odds16.3%Bo Girds",
      "Title odds14.5%Maye d'force B with U",
    ]);
    expect(takeover.getByText("All You Need Is Love, 11-5, 6th in title odds")).toBeTruthy();
    const link = takeover.getByRole("link", { name: "Read the Midseason Report" });
    expect(link.getAttribute("href")).toBe("/midseason/2026/");
  });
});

describe("ReportTile", () => {
  it("shows one big fact, the title odds of the favorite, as one link to the report", () => {
    render(<ReportTile report={midseason} href="/midseason/2026/" />);
    const link = screen.getByRole("link", { name: /Midseason Report/ });
    expect(link.getAttribute("href")).toBe("/midseason/2026/");
    expect(within(link).getByText("2026 Midseason Report")).toBeTruthy();
    expect(within(link).getByText("Title favorite")).toBeTruthy();
    expect(within(link).getByText("16.8%")).toBeTruthy();
    expect(within(link).getByText("London Cooking")).toBeTruthy();
  });
});
