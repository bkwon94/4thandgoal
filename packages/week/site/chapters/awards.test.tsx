/**
 * Tests for the Awards chapter. They render the week 8 JSON of CPC, read each award tile, and open a tile with a tap.
 * They check what a reader sees and the button state, not the class names.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Awards } from "./awards";
import { week8 } from "../fixtures/week-page";

afterEach(() => {
  cleanup();
});

function renderAwards(headshots = week8.headshots) {
  render(<Awards awards={week8.awards} headshots={headshots} blurb={week8.blurbs.awards} />);
  return screen.getByRole("region", { name: "Awards" });
}

/* The tile of each award, in the order of the JSON. A chip of a panel is a listitem too, so only the items of the grid count. */
const tiles = (chapter: HTMLElement) => Array.from(within(chapter).getAllByRole("list")[0].children) as HTMLElement[];

/* The head button of a tile. The chevron under each tile is a second toggle with its own label. */
const headOf = (tile: HTMLElement) => within(tile).getAllByRole("button").find((button) => !button.hasAttribute("aria-label"))!;

/* The panel that a toggle opens. */
const panelOf = (button: HTMLElement) => document.getElementById(button.getAttribute("aria-controls") ?? "")!;

describe("Awards", () => {
  it("shows a closed tile for each award with its name, the points, and the player in one button", () => {
    const chapter = renderAwards();
    expect(chapter.id).toBe("awards");
    expect(tiles(chapter).map((tile) => headOf(tile).textContent)).toEqual([
      "Top Scorer42.48Joe Burrow",
      "MVB · Most Valuable Benchwarmer26.2Tony Pollard",
      "Underperformer0Lamar Jackson",
      "Overachiever32.5Tee Higgins",
    ]);
    for (const button of within(chapter).getAllByRole("button")) expect(button.getAttribute("aria-expanded")).toBe("false");
    // Each tile has a chevron toggle under it, bound to the same panel as its head.
    expect(within(chapter).getAllByRole("button", { name: "Show the details" })).toHaveLength(4);
  });

  it("keeps the team and the projection closed until a tap, and findable by find-in-page (AT-7)", () => {
    const chapter = renderAwards();
    const panel = panelOf(headOf(tiles(chapter)[2]));
    expect(panel.getAttribute("hidden")).toBe("until-found");
    expect(panel.hasAttribute("inert")).toBe(false);
    expect(panel.textContent).toContain("Bo Girds");
  });

  it("opens the Underperformer tile to two chips: the team and the projection (AT-7)", () => {
    const chapter = renderAwards();
    const tile = tiles(chapter)[2];
    const button = headOf(tile);
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(tile.getAttribute("data-open")).toBe("true");
    const panel = panelOf(button);
    expect(panel.hasAttribute("hidden")).toBe(false);
    expect(within(panel).getAllByRole("listitem").map((chip) => chip.textContent)).toEqual(["Bo Girds", "Proj 20.52"]);
  });

  it("opens the Top Scorer tile to the team chip alone, because the award has no projection (AT-7)", () => {
    const chapter = renderAwards();
    const button = headOf(tiles(chapter)[0]);
    fireEvent.click(button);
    expect(within(panelOf(button)).getAllByRole("listitem").map((chip) => chip.textContent)).toEqual(["All You Need Is Love"]);
  });

  it("opens a tile from its chevron and closes it on a second tap (AT-7)", async () => {
    const chapter = renderAwards();
    const tile = tiles(chapter)[3];
    const chevron = within(tile).getByRole("button", { name: "Show the details" });
    fireEvent.click(chevron);
    expect(headOf(tile).getAttribute("aria-expanded")).toBe("true");
    expect(chevron.getAttribute("aria-label")).toBe("Hide the details");
    fireEvent.click(headOf(tile));
    expect(headOf(tile).getAttribute("aria-expanded")).toBe("false");
    await waitFor(() => expect(panelOf(headOf(tile)).getAttribute("hidden")).toBe("until-found"));
    expect(tile.getAttribute("data-open")).toBe("false");
  });

  it("shows each player in a round photo frame (AT-33)", () => {
    const chapter = renderAwards();
    expect(within(tiles(chapter)[0]).getByRole("img", { name: "Joe Burrow" }).getAttribute("src")).toBe(
      "headshots/6770.png",
    );
  });

  it("shows the initials of a player with no headshot (AT-33)", () => {
    const chapter = renderAwards({});
    expect(within(tiles(chapter)[1]).getByRole("img", { name: "Tony Pollard" }).textContent).toBe("TP");
  });

  it("shows a note in place of the player when the award is missing", () => {
    render(<Awards awards={[{ title: "Overachiever", missing: true }]} headshots={{}} blurb="" />);
    expect(screen.getByText("Projections unavailable this week")).toBeTruthy();
    // A missing award has no detail to open, so its tile has no toggle.
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("shows the blurb as prose", () => {
    const chapter = renderAwards();
    expect(within(chapter).getByText(week8.blurbs.awards).tagName).toBe("P");
  });
});
