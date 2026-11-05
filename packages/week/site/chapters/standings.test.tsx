/**
 * Tests for the standings. They render the week 6 JSON and read the rows, the records, and the points.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week6 } from "../fixtures/week-page";
import { Standings } from "./standings";

afterEach(() => {
  cleanup();
});

function renderStandings() {
  return render(<Standings table={week6.table} avatars={week6.avatars} />);
}

describe("Standings", () => {
  it("shows the header row", () => {
    renderStandings();
    for (const head of ["#", "Team", "W-L", "Pts"]) {
      expect(screen.getByText(head)).toBeTruthy();
    }
  });

  it("shows one row per team with the rank, the name, and the record", () => {
    renderStandings();
    expect(screen.getByText("Lil Fridge")).toBeTruthy();
    expect(screen.getByText("10-2")).toBeTruthy();
    expect(screen.getByText("Pukancun on 3")).toBeTruthy();
    expect(screen.getByText("1-11")).toBeTruthy();
    expect(screen.getByText("12")).toBeTruthy();
  });

  it("is a table with a header row, one row per team, and the cut row", () => {
    renderStandings();
    const table = screen.getByRole("table", { name: "Standings" });
    expect(within(table).getAllByRole("columnheader").map((head) => head.textContent)).toEqual(["#", "Team", "W-L", "Pts"]);
    expect(within(table).getAllByRole("row")).toHaveLength(week6.table.length + 2);
    expect(within(table).getByRole("cell", { name: "Lil Fridge" })).toBeTruthy();
  });

  it("always shows the points with two decimals", () => {
    renderStandings();
    expect(screen.getByText("739.67")).toBeTruthy();
    expect(screen.getByText("698.30")).toBeTruthy();
  });

  it("puts the cut line after the sixth row", () => {
    renderStandings();
    const cut = screen.getByRole("cell", { name: "Playoff cut" });
    const before = week6.table.filter(
      (row) => screen.getByText(row.team.name).compareDocumentPosition(cut) & Node.DOCUMENT_POSITION_FOLLOWING,
    );
    expect(before.map((row) => row.team.name)).toEqual(week6.table.slice(0, 6).map((row) => row.team.name));
  });

  it("shows the note about the median game", () => {
    renderStandings();
    expect(screen.getByText(/Records include the weekly median game/)).toBeTruthy();
  });

  it("leaves out the note when the league has no median game", () => {
    render(<Standings table={week6.table} avatars={week6.avatars} hasMedianGame={false} />);
    expect(screen.queryByText(/Records include the weekly median game/)).toBeNull();
  });

  it("links a team name to its manager page only when the season has the managers file", () => {
    const { rerender } = render(<Standings table={week6.table} avatars={week6.avatars} managersHref="/2026/managers/" />);
    expect(screen.getByRole("link", { name: "Lil Fridge" }).getAttribute("href")).toBe("/2026/managers/3/");
    rerender(<Standings table={week6.table} avatars={week6.avatars} />);
    expect(screen.queryByRole("link", { name: "Lil Fridge" })).toBeNull();
  });
});
