/**
 * Tests for Every game, the game cards of the week page. They render the week 8 JSON of CPC and open a recap with a tap.
 * They check what a reader sees and the button state.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { AllMatchups } from "./all-matchups";
import { week8 } from "../fixtures/week-page";

afterEach(() => {
  cleanup();
});

function renderGames(managersHref: string | null = "/2026/managers/") {
  render(<AllMatchups matchups={week8.matchups} avatars={week8.avatars} managersHref={managersHref} />);
  return screen.getByRole("region", { name: "Every game" });
}

/* The game card button that names this team. */
function gameOf(team: string) {
  return screen.getAllByRole("button").find((button) => button.textContent?.includes(team))!;
}

/* The recap panel that a game card button opens. */
function panelOf(button: HTMLElement) {
  return document.getElementById(button.getAttribute("aria-controls") ?? "")!;
}

describe("AllMatchups", () => {
  it("is the chapter Every game, with one closed card button per game, by top score", () => {
    const chapter = renderGames();
    expect(chapter.id).toBe("matchups");
    expect(within(chapter).getByRole("heading", { level: 2 }).textContent).toBe("Every game");
    const buttons = within(chapter).getAllByRole("button");
    expect(buttons.map((button) => button.textContent?.split(/\d/)[0])).toEqual([
      "Teehee",
      "Maye d'force B with U",
      "To Infinity and Bijan",
      "All You Need Is Love",
      "Return of T Mac",
      "The Blue Tent",
    ]);
    for (const button of buttons) expect(button.getAttribute("aria-expanded")).toBe("false");
  });

  it("shows both teams and both scores on a card, as plain text in one button", () => {
    renderGames();
    const button = gameOf("The Blue Tent");
    expect(button.textContent).toBe("The Blue Tent100.31London Cooking98.88");
    expect(within(button).queryByRole("link")).toBeNull();
  });

  it("keeps each recap closed until a tap", () => {
    renderGames();
    expect(panelOf(gameOf("The Blue Tent")).hidden).toBe(true);
  });

  it("opens the recap of The Blue Tent and London Cooking with a brand edge and one Manager page link (AT-17)", () => {
    renderGames();
    const button = gameOf("The Blue Tent");
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("true");
    const panel = panelOf(button);
    expect(panel.hidden).toBe(false);
    expect(within(panel).getByText("Won by 1.43")).toBeTruthy();
    const pick = week8.matchups.find((matchup) => matchup.is_pick)!;
    expect(within(panel).getByText(pick.recap!).tagName).toBe("P");
    const links = within(panel).getAllByRole("link");
    expect(links).toHaveLength(1);
    expect(links[0].textContent).toBe("Manager page of The Blue Tent");
    expect(links[0].getAttribute("href")).toBe(`/2026/managers/${pick.sides[0].team.roster_id}/`);
    // The open card takes the brand edge.
    expect(button.closest("[data-open]")?.getAttribute("data-open")).toBe("true");
  });

  it("closes the recap on a second tap", () => {
    renderGames();
    const button = gameOf("The Blue Tent");
    fireEvent.click(button);
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(panelOf(button).hidden).toBe(true);
    expect(button.closest("[data-open]")?.getAttribute("data-open")).toBe("false");
  });

  it("shows no Manager page link when the season has no managers file", () => {
    renderGames(null);
    const button = gameOf("The Blue Tent");
    fireEvent.click(button);
    expect(within(panelOf(button)).queryByRole("link")).toBeNull();
  });

  it("names each recap panel by its game, so a link or a check can open one game", () => {
    renderGames();
    const pick = week8.matchups.find((matchup) => matchup.is_pick)!;
    expect(gameOf("The Blue Tent").getAttribute("aria-controls")).toBe(`recap-${pick.id}`);
  });
});
