/**
 * Tests for the standings. They render the week 8 JSON of CPC and read each team row, the playoff ticks, and the cut.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { Standings } from "./standings";

afterEach(() => {
  cleanup();
});

function renderStandings(managersHref: string | null = "/2026/managers/", hasMedianGame = true) {
  render(<Standings table={week8.table} avatars={week8.avatars} managersHref={managersHref} hasMedianGame={hasMedianGame} />);
  return screen.getByRole("region", { name: "Standings" });
}

const rows = (chapter: HTMLElement) =>
  within(within(chapter).getByRole("list", { name: "Standings" })).getAllByRole("listitem");

describe("Standings", () => {
  it("shows a row for every team with its rank, avatar, name, record, and points (AT-16)", () => {
    const chapter = renderStandings();
    expect(chapter.id).toBe("standings");
    expect(rows(chapter)).toHaveLength(12);
    expect(rows(chapter)[0].textContent).toBe("01All You Need Is Love, playoff spot11-5850.17");
    expect(rows(chapter)[11].textContent).toBe("12NFC Least3-13700.97");
    expect(rows(chapter)[0].querySelector("img")?.getAttribute("src")).toMatch(/^avatars\//);
  });

  it("ticks the six playoff spots and draws the brand line under the sixth", () => {
    const chapter = renderStandings();
    const ticked = rows(chapter).map((row) => row.textContent?.includes("playoff spot"));
    expect(ticked).toEqual([true, true, true, true, true, true, false, false, false, false, false, false]);
    expect(rows(chapter).map((row) => row.hasAttribute("data-cut"))).toEqual(
      [false, false, false, false, false, true, false, false, false, false, false, false],
    );
    expect(within(chapter).getByText("Playoff line after 6th")).toBeTruthy();
  });

  it("makes each whole row the link to the manager page of its team", () => {
    const chapter = renderStandings();
    const link = within(rows(chapter)[0]).getByRole("link");
    expect(link.getAttribute("href")).toBe(`/2026/managers/${week8.table[0].team.roster_id}/`);
    expect(link.textContent).toBe(rows(chapter)[0].textContent);
  });

  it("shows the rows as plain text when the season has no managers file", () => {
    const chapter = renderStandings(null);
    expect(within(chapter).queryByRole("link")).toBeNull();
  });

  it("shows the note about the median game only for a league that plays one", () => {
    const chapter = renderStandings();
    expect(within(chapter).getByText(/Records include the weekly median game/)).toBeTruthy();
    cleanup();
    const other = renderStandings("/2026/managers/", false);
    expect(within(other).queryByText(/Records include the weekly median game/)).toBeNull();
  });
});
