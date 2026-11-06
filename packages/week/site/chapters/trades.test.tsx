/**
 * Tests for the Trades chapter. They render the week 8 JSON of CPC and read each side and the players it gets.
 * A copy of the JSON with no trades checks that the chapter is left out.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week8 } from "../fixtures/week-page";
import { Trades } from "./trades";

afterEach(() => {
  cleanup();
});

function renderTrades(trades = week8.trades, managersHref: string | null = "/2026/managers/") {
  render(<Trades trades={trades} avatars={week8.avatars} managersHref={managersHref} />);
  return screen.getByRole("region", { name: "Trades" });
}

/* The players that a side gets, by the name of the side. */
function gets(chapter: HTMLElement, team: string) {
  return within(within(chapter).getByRole("list", { name: `${team} gets` }))
    .getAllByRole("listitem")
    .map((item) => item.textContent);
}

describe("Trades", () => {
  it("shows a card for the trade of week 8 with the count of the week", () => {
    const chapter = renderTrades();
    expect(chapter.id).toBe("trades");
    expect(within(chapter).getByText("1 this week")).toBeTruthy();
    expect(within(chapter).getAllByRole("article")).toHaveLength(1);
  });

  it("shows each side and the players it gets, each in a round photo frame", () => {
    const chapter = renderTrades();
    expect(gets(chapter, "NFC Least")).toEqual(["Saquon Barkley", "CeeDee Lamb"]);
    expect(gets(chapter, "behold the lamb")).toEqual(["Omar Cooper Jr.", "Puka Nacua"]);
    // The name sits beside the frame, so the photo is decorative and a screen reader hears the name once.
    const saquon = within(within(chapter).getByRole("list", { name: "NFC Least gets" })).getAllByRole("listitem")[0];
    expect(saquon.querySelector("img")?.getAttribute("src")).toBe("headshots/4866.png");
  });

  it("makes the whole team row of a side the link to its manager page", () => {
    const chapter = renderTrades();
    const link = within(chapter).getByRole("link", { name: "NFC Least" });
    expect(link.getAttribute("href")).toMatch(/^\/2026\/managers\/\d+\/$/);
    expect(link.querySelector("img")).not.toBeNull();
  });

  it("shows the team names as plain text when the season has no managers file", () => {
    const chapter = renderTrades(week8.trades, null);
    expect(within(chapter).queryByRole("link")).toBeNull();
    expect(within(chapter).getByText("NFC Least")).toBeTruthy();
  });

  it("shows picks as plain lines and all sides of a trade of three", () => {
    const [a, b] = week8.trades[0].sides;
    const third = { ...a, team: { ...a.team, roster_id: 901, name: "Third Team" }, players: [], picks: ["2027 1st round"] };
    const chapter = renderTrades([{ sides: [a, b, third] }]);
    expect(gets(chapter, "Third Team")).toEqual(["2027 1st round"]);
    expect(within(chapter).getByText("1 this week")).toBeTruthy();
  });

  it("counts two trades as 2 this week", () => {
    const chapter = renderTrades([week8.trades[0], week8.trades[0]]);
    expect(within(chapter).getByText("2 this week")).toBeTruthy();
  });

  it("leaves the chapter out when the week has no trades", () => {
    const { container } = render(<Trades trades={[]} avatars={week8.avatars} />);
    expect(container.innerHTML).toBe("");
  });
});
