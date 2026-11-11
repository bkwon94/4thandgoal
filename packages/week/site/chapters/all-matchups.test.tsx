/**
 * Tests for Every game, the game cards of the week page. They render the week 8 JSON of CPC and open a recap with a tap.
 * They check what a reader sees and the button state.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { AllMatchups } from "./all-matchups";
import { avatarSrc } from "@cpc/league/images";
import { week8 } from "../fixtures/week-page";

afterEach(() => {
  cleanup();
});

function renderGames(managersHref: string | null = "/2026/managers/") {
  render(<AllMatchups matchups={week8.matchups} avatars={week8.avatars} managersHref={managersHref} />);
  return screen.getByRole("region", { name: "Every game" });
}

/* The head buttons of the game cards. The chevron under each card is a second toggle with its own label. */
function heads(scope: HTMLElement = document.body) {
  return within(scope)
    .getAllByRole("button")
    .filter((button) => !button.hasAttribute("aria-label"));
}

/* The game card button that names this team. */
function gameOf(team: string) {
  return heads().find((button) => button.textContent?.includes(team))!;
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
    const buttons = heads(chapter);
    expect(buttons.map((button) => button.textContent?.split(/\d/)[0])).toEqual([
      "Teehee",
      "Maye d'force B with U",
      "To Infinity and Bijan",
      "All You Need Is Love",
      "Return of T Mac",
      "The Blue Tent",
    ]);
    for (const button of within(chapter).getAllByRole("button")) expect(button.getAttribute("aria-expanded")).toBe("false");
    // Each card has a chevron toggle under it, bound to the same panel as its head.
    expect(within(chapter).getAllByRole("button", { name: "Show the details" })).toHaveLength(buttons.length);
  });

  it("gives each game an id with the roster ids of its two teams, lower first, so a link reaches one game", () => {
    renderGames();
    const ids = week8.matchups.map((matchup) => {
      const [low, high] = matchup.sides.map((side) => side.team.roster_id).sort((a, b) => a - b);
      return `game-${low}-${high}`;
    });
    for (const id of ids) expect(document.getElementById(id)?.tagName).toBe("LI");
    expect(document.getElementById("game-3-9")?.textContent).toContain("Lil Fridge");
  });

  it("shows both teams and both scores on a card, as plain text in one button", () => {
    renderGames();
    const button = gameOf("The Blue Tent");
    expect(button.textContent).toBe("The Blue Tent100.31London Cooking98.88");
    expect(within(button).queryByRole("link")).toBeNull();
  });

  it("keeps each recap closed until a tap, and findable by find-in-page", () => {
    renderGames();
    const panel = panelOf(gameOf("All You Need Is Love"));
    expect(panel.getAttribute("hidden")).toBe("until-found");
    expect(panel.hasAttribute("inert")).toBe(false);
    const game = week8.matchups.find((matchup) => matchup.sides[0].team.name === "All You Need Is Love")!;
    expect(panel.textContent).toContain(game.recap!);
  });

  it("opens the card of All You Need Is Love with exactly three chips: both best players and both records (AT-3)", () => {
    renderGames();
    const button = gameOf("All You Need Is Love");
    fireEvent.click(button);
    const panel = panelOf(button);
    const chips = within(panel).getAllByRole("listitem");
    expect(chips.map((chip) => chip.textContent)).toEqual(["Best J. Burrow 42.48", "Best J. Jacobs 20.2", "Records 11-5 · 6-10"]);
    // Each best-player chip starts with the avatar of its team.
    const [winner, loser] = week8.matchups.find((matchup) => matchup.id === 4)!.sides;
    expect(chips[0].querySelector("img")?.getAttribute("src")).toBe(avatarSrc(week8.avatars, winner.team.roster_id));
    expect(chips[1].querySelector("img")?.getAttribute("src")).toBe(avatarSrc(week8.avatars, loser.team.roster_id));
    expect(chips[2].querySelector("img")).toBeNull();
    // The margin line is gone, because the scores and the share bar show it.
    expect(within(panel).queryByText(/^Won by/)).toBeNull();
  });

  it("keeps the scoreboard on the closed card of All You Need Is Love: both avatars, both scores, and the share bar (AT-2)", () => {
    renderGames();
    const button = gameOf("All You Need Is Love");
    expect(button.textContent).toBe("All You Need Is Love116.83Unsolicited Dak Picks92.55");
    expect(button.querySelectorAll("img")).toHaveLength(2);
    expect(within(button).getByRole("meter", { name: "Share of the points" })).toBeTruthy();
  });

  it("opens the recap of The Blue Tent and London Cooking with a brand edge and one Manager page link (AT-17)", () => {
    renderGames();
    const button = gameOf("The Blue Tent");
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("true");
    const panel = panelOf(button);
    expect(panel.hasAttribute("hidden")).toBe(false);
    const pick = week8.matchups.find((matchup) => matchup.is_pick)!;
    expect(within(panel).getByText(pick.recap!).tagName).toBe("P");
    const links = within(panel).getAllByRole("link");
    expect(links).toHaveLength(1);
    expect(links[0].textContent).toBe("Manager page of The Blue Tent");
    expect(links[0].getAttribute("href")).toBe(`/2026/managers/${pick.sides[0].team.roster_id}/`);
    // The open card takes the brand edge.
    expect(button.closest("[data-open]")?.getAttribute("data-open")).toBe("true");
  });

  it("closes the recap on a second tap", async () => {
    renderGames();
    const button = gameOf("The Blue Tent");
    fireEvent.click(button);
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("false");
    await waitFor(() => expect(panelOf(button).getAttribute("hidden")).toBe("until-found"));
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
