/**
 * Tests for Position leaders. They render the week 8 JSON of CPC, tap a position chip, and read the top three.
 * They check what a reader sees and the chip state, not the class names.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { PositionLeaders } from "./position-leaders";

afterEach(() => {
  cleanup();
});

function renderLeaders(leaders = week8.leaders) {
  render(<PositionLeaders leaders={leaders} headshots={week8.headshots} blurb={week8.blurbs.position_leaders} />);
  return screen.getByRole("region", { name: "Position leaders" });
}

/* The names of the rows that show now. */
function names(chapter: HTMLElement) {
  return within(within(chapter).getByRole("list", { name: /leaders$/ }))
    .getAllByRole("listitem")
    .map((row) => row.querySelector("[data-player]")?.textContent);
}

/* The chip of a position. */
const chip = (chapter: HTMLElement, position: string) => within(chapter).getByRole("button", { name: position });

describe("PositionLeaders", () => {
  it("shows a chip for each position, with QB chosen first", () => {
    const chapter = renderLeaders();
    expect(chapter.id).toBe("leaders");
    const chips = within(chapter).getAllByRole("button");
    expect(chips.map((button) => button.textContent)).toEqual(["QB", "RB", "WR", "TE", "DEF"]);
    expect(chips.map((button) => button.getAttribute("aria-pressed"))).toEqual(["true", "false", "false", "false", "false"]);
    expect(names(chapter)).toEqual(["Joe Burrow", "Kirk Cousins", "Josh Allen"]);
  });

  it("shows the top three WR of week 8 after a tap on the chip WR (AT-18)", () => {
    const chapter = renderLeaders();
    fireEvent.click(chip(chapter, "WR"));
    expect(chip(chapter, "WR").getAttribute("aria-pressed")).toBe("true");
    expect(chip(chapter, "QB").getAttribute("aria-pressed")).toBe("false");
    expect(names(chapter)).toEqual(["Tee Higgins", "Ja'Marr Chase", "Michael Wilson"]);
  });

  it("shows the rank, the fantasy team, and the points of each row", () => {
    const chapter = renderLeaders();
    fireEvent.click(chip(chapter, "WR"));
    const first = within(within(chapter).getByRole("list", { name: "WR leaders" })).getAllByRole("listitem")[0];
    expect(first.textContent).toBe("1Tee HigginsTeehee32.5");
  });

  it("shows each player in a round photo frame, and the initials of a player with no headshot (AT-33)", () => {
    const chapter = renderLeaders();
    fireEvent.click(chip(chapter, "DEF"));
    expect(within(chapter).getByRole("img", { name: "Jacksonville Jaguars" }).getAttribute("src")).toBe("headshots/JAX.png");
    cleanup();
    render(<PositionLeaders leaders={week8.leaders} headshots={{}} />);
    expect(screen.getByRole("img", { name: "Joe Burrow" }).textContent).toBe("JB");
  });

  it("shows only the positions it gets, so a league with no DEF slot shows no DEF chip", () => {
    const chapter = renderLeaders(week8.leaders.filter((board) => board.position !== "DEF"));
    expect(within(chapter).queryByRole("button", { name: "DEF" })).toBeNull();
  });

  it("shows a note for a position with no starters", () => {
    render(<PositionLeaders leaders={[{ position: "TE", rows: [] }]} headshots={{}} />);
    expect(screen.getByText("No starters this week")).toBeTruthy();
  });

  it("shows the blurb as prose", () => {
    const chapter = renderLeaders();
    expect(within(chapter).getByText(week8.blurbs.position_leaders!).tagName).toBe("P");
  });
});
