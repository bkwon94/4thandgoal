/**
 * Tests for the Trades chapter. They render the week 8 JSON of CPC, read each side and the players it gets, and open a card with a tap.
 * A copy of the JSON with no trades checks that the chapter is left out.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { avatarSrc } from "@cpc/league/images";
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

/* The head button of the first trade card. The chevron under the card is a second toggle with its own label. */
function headOf(chapter: HTMLElement) {
  return within(within(chapter).getAllByRole("article")[0])
    .getAllByRole("button")
    .find((button) => !button.hasAttribute("aria-label"))!;
}

/* The panel that a toggle opens. */
const panelOf = (button: HTMLElement) => document.getElementById(button.getAttribute("aria-controls") ?? "")!;

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

  it("shows the closed trade as one button: both sides, the players each gets, and no link (AT-7)", () => {
    const chapter = renderTrades();
    const button = headOf(chapter);
    expect(button.textContent).toBe("NFC LeastGetsSaquon BarkleyCeeDee Lambbehold the lambGetsOmar Cooper Jr.Puka Nacua");
    expect(within(button).queryByRole("link")).toBeNull();
    for (const toggle of within(chapter).getAllByRole("button")) expect(toggle.getAttribute("aria-expanded")).toBe("false");
    expect(within(chapter).getAllByRole("button", { name: "Show the details" })).toHaveLength(1);
  });

  it("keeps the records closed until a tap, and findable by find-in-page (AT-7)", () => {
    const chapter = renderTrades();
    const panel = panelOf(headOf(chapter));
    expect(panel.getAttribute("hidden")).toBe("until-found");
    expect(panel.hasAttribute("inert")).toBe(false);
    expect(panel.textContent).toContain("NFC Least 3-13");
  });

  it("opens the trade of week 8 to a record chip for each side, each with the avatar of its team (AT-7)", () => {
    const chapter = renderTrades();
    const button = headOf(chapter);
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(button.closest("[data-open]")?.getAttribute("data-open")).toBe("true");
    const panel = panelOf(button);
    expect(panel.hasAttribute("hidden")).toBe(false);
    const chips = within(panel).getAllByRole("listitem");
    expect(chips.map((chip) => chip.textContent)).toEqual(["NFC Least 3-13", "behold the lamb 6-10"]);
    const [first, second] = week8.trades[0].sides;
    expect(chips[0].querySelector("img")?.getAttribute("src")).toBe(avatarSrc(week8.avatars, first.team.roster_id));
    expect(chips[1].querySelector("img")?.getAttribute("src")).toBe(avatarSrc(week8.avatars, second.team.roster_id));
  });

  it("opens the trade to one manager page link for each side (AT-7)", () => {
    const chapter = renderTrades();
    const button = headOf(chapter);
    fireEvent.click(button);
    const links = within(panelOf(button)).getAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual(["NFC Least, manager page", "behold the lamb, manager page"]);
    const [first, second] = week8.trades[0].sides;
    expect(links.map((link) => link.getAttribute("href"))).toEqual([
      `/2026/managers/${first.team.roster_id}/`,
      `/2026/managers/${second.team.roster_id}/`,
    ]);
  });

  it("closes the trade on a tap of the chevron (AT-7)", async () => {
    const chapter = renderTrades();
    const button = headOf(chapter);
    fireEvent.click(button);
    fireEvent.click(within(chapter).getByRole("button", { name: "Hide the details" }));
    expect(button.getAttribute("aria-expanded")).toBe("false");
    await waitFor(() => expect(panelOf(button).getAttribute("hidden")).toBe("until-found"));
  });

  it("shows no link when the season has no managers file", () => {
    const chapter = renderTrades(week8.trades, null);
    fireEvent.click(headOf(chapter));
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
