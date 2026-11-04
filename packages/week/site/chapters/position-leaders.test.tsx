/**
 * Tests for the position leaders. They render the week 6 JSON and read each board and its rows.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { firstSentence, week6 } from "../fixtures/week-page";
import { PositionLeaders } from "./position-leaders";

afterEach(() => {
  cleanup();
});

function renderLeaders() {
  return render(
    <PositionLeaders leaders={week6.leaders} headshots={week6.headshots} blurb={week6.blurbs.position_leaders} />,
  );
}

describe("PositionLeaders", () => {
  it("shows the label and one list per position", () => {
    renderLeaders();
    expect(screen.getByText("Position Leaders")).toBeTruthy();
    for (const position of ["QB", "RB", "WR", "TE", "DEF"]) {
      expect(screen.getByText(position)).toBeTruthy();
    }
    expect(screen.getAllByRole("list")).toHaveLength(5);
  });

  it("shows each leader's name, NFL team, fantasy team, and points", () => {
    renderLeaders();
    const qb = screen.getAllByRole("list")[0];
    const first = within(qb).getAllByRole("listitem")[0];
    expect(first.textContent).toContain("Trevor Lawrence");
    expect(first.textContent).toContain("JAX");
    expect(first.textContent).toContain("Amon-Ra Dawg Your Team");
    expect(first.textContent).toContain("28.34");
    expect(screen.getByText("Christian McCaffrey")).toBeTruthy();
    expect(screen.getByText("Pittsburgh Steelers")).toBeTruthy();
  });

  it("shows only the positions it gets, so a league with no DEF slot shows no DEF card (AT-13)", () => {
    const leaders = week6.leaders.filter((board) => board.position !== "DEF");
    render(<PositionLeaders leaders={leaders} headshots={week6.headshots} />);
    expect(screen.queryByText("DEF")).toBeNull();
    expect(screen.getAllByRole("list")).toHaveLength(4);
  });

  it("shows a note for a position with no starters", () => {
    render(<PositionLeaders leaders={[{ position: "TE", rows: [] }]} headshots={{}} />);
    expect(screen.getByText("No starters this week")).toBeTruthy();
  });

  it("shows the blurb", () => {
    renderLeaders();
    expect(screen.getByText(firstSentence(week6.blurbs.position_leaders), { exact: false })).toBeTruthy();
  });
});
