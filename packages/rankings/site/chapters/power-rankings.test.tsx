/**
 * Tests for the Ladder of the power rankings: the hero for rank 1, the week chips, the cards, and the note on the parts.
 * They render the fixture and read what a reader sees and taps, not the class names.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { rankings } from "../fixtures/rankings";
import { Movement, PowerRankings } from "./power-rankings";

const lastWeek = rankings.weeks.at(-1)!;
const firstWeek = rankings.weeks[0];

/* One avatar per team of the fixture, in the shape of the avatars of a week page. */
const avatars = Object.fromEntries(rankings.weeks[0].rows.map((row) => [String(row.roster_id), `avatars/${row.roster_id}.jpg`]));

afterEach(() => {
  cleanup();
  // A test that sets the hash must not leak it into the next test.
  window.history.replaceState(null, "", "/");
});

function hero() {
  return within(screen.getByRole("region", { name: "Rank 1" }));
}

function chip(week: number) {
  return within(screen.getByRole("group", { name: "Week" })).getByRole("button", { name: `Week ${week}` });
}

/* The cards of the ladder, in their order on the page. */
function cards() {
  return within(screen.getByRole("list")).getAllByRole("listitem");
}

/* The head of a card is its button, and its name holds the team name. */
function cardButton(name: string) {
  return screen.getByRole("button", { name: new RegExp(name) });
}

function panelOf(button: HTMLElement) {
  return document.getElementById(button.getAttribute("aria-controls") ?? "")!;
}

/* The text of each hero slot, in the order of the markup. */
function slots() {
  const region = screen.getByRole("region", { name: "Rank 1" });
  return [...region.querySelectorAll("[data-hero-slot]")].map((slot) => [slot.getAttribute("data-hero-slot"), slot.textContent]);
}

describe("The hero", () => {
  it("fills the slots: the week, the team at rank 1, its record and movement, then the three tiles", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    // London Cooking is first in week 6 at 9-3, up 4, with odds of 97, 64, and the 2 seed.
    expect(slots()).toEqual([
      ["eyebrow", "WEEK 6 // POWER RANKINGS"],
      ["title", "London Cooking"],
      ["meta", "9-3 · Up4"],
      ["stats", "Playoff97%Bye64%Seed2"],
    ]);
    expect(hero().getByText("Up").parentElement?.querySelector("svg")?.dataset.arrow).toBe("up");
    expect(hero().getByText("Playoff").nextElementSibling?.textContent).toBe("97%");
    expect(hero().getByText("Bye").nextElementSibling?.textContent).toBe("64%");
    expect(hero().getByText("Seed").nextElementSibling?.textContent).toBe("2");
  });

  it("names the team at rank 1 in the level one heading", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    expect(hero().getByRole("heading", { level: 1 }).textContent).toBe("London Cooking");
  });

  it("shows the blurb of rank 1 as a paragraph directly under the hero, outside its frame", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    const text = lastWeek.rows[0].blurb.map((sentence) => sentence.text).join(" ");
    expect(hero().queryByText(text)).toBeNull();
    const top = screen.getByRole("region", { name: "Rank 1" });
    expect(top.nextElementSibling?.tagName).toBe("P");
    expect(top.nextElementSibling?.textContent).toBe(text);
  });

  it("follows the chosen week, with a dash in each tile for a week with no odds", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    fireEvent.click(chip(firstWeek.week));
    // Lil Fridge is first in week 1, before the odds engine ran.
    expect(hero().getByRole("heading", { level: 1 }).textContent).toBe("Lil Fridge");
    expect(slots()[0]).toEqual(["eyebrow", "WEEK 1 // POWER RANKINGS"]);
    expect(hero().getByText("No last week")).toBeTruthy();
    for (const label of ["Playoff", "Bye", "Seed"]) {
      expect(hero().getByText(label).nextElementSibling?.textContent).toMatch(/^–No (odds|seed)$/);
    }
  });

  it("keeps the static grid, the glow, and the brackets in the hero, and draws no scene on the page (AT-35, AT-44)", () => {
    const { container } = render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    const hero = screen.getByRole("region", { name: "Rank 1" });
    expect(container.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(0);
    // The static hero: the texture layer holds the grid and the glow, and the four brackets sit in the corners.
    expect(hero.querySelectorAll("[data-hero-art='texture']")).toHaveLength(1);
    expect(hero.querySelectorAll("[data-hero-art='bracket']")).toHaveLength(4);
  });
});

describe("The ladder", () => {
  it("shows one card for each team after rank 1, in rank order", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    expect(cards()).toHaveLength(11);
    expect(cards().map((card) => card.textContent)).toEqual(
      lastWeek.rows.slice(1).map((row) => expect.stringContaining(row.name)),
    );
  });

  it("shows the rank, the avatar, the name, the record with the movement, and the playoff odds with a bar", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    // Bo Girds is third at 8-4, with no change, and playoff odds of 89.
    const card = cards()[1];
    const head = within(card.querySelector("button")!);
    expect(head.getByText("03")).toBeTruthy();
    expect(card.querySelector("img")?.getAttribute("src")).toBe(`avatars/${lastWeek.rows[2].roster_id}.jpg`);
    expect(head.getByText("Bo Girds")).toBeTruthy();
    expect(head.getByText("8-4")).toBeTruthy();
    expect(head.getByText("No change")).toBeTruthy();
    expect(head.getByText("89%")).toBeTruthy();
    expect((card.querySelector("[data-odds-bar]") as HTMLElement).style.width).toBe("89%");
  });

  it("shows In and a full bar for a clinched team, and Out and an empty bar for a team that is out", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    const fridge = cards()[0];
    const pukancun = cards()[10];
    expect(within(fridge).getByText("In")).toBeTruthy();
    expect((fridge.querySelector("[data-odds-bar]") as HTMLElement).style.width).toBe("100%");
    expect(within(pukancun).getByText("Out")).toBeTruthy();
    expect((pukancun.querySelector("[data-odds-bar]") as HTMLElement).style.width).toBe("0%");
  });

  it("shows a dash and no bar for a team with no odds", () => {
    render(<PowerRankings weeks={[firstWeek]} avatars={avatars} />);
    for (const card of cards()) {
      expect(within(card).getByText("No odds")).toBeTruthy();
      expect(card.querySelector("[data-odds-bar]")).toBeNull();
    }
  });

  it("puts the note on the four parts after the last card", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    const note = screen.getByText(/rank from 1 to 12 in four parts/);
    expect(cards()[10].compareDocumentPosition(note) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getByText("Playoff odds from 5,000 simulated seasons.")).toBeTruthy();
  });

  it("never shows a sum, a ratio, or a decimal on a card", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    for (const card of cards()) {
      expect(card.textContent).not.toMatch(/\d\.\d|\//);
    }
  });
});

describe("An open card", () => {
  it("opens the four part ranks, the blurb, and the manager link on a tap, then closes on a second tap", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} managersHref="/2026/managers/" />);
    // Lil Fridge is second, and ranks 1, 3, 6, and 2 on standing, form, schedule played, and scoring.
    const button = cardButton("Lil Fridge");
    const panel = panelOf(button);
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(panel.getAttribute("aria-hidden")).toBe("true");
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(panel.getAttribute("aria-hidden")).toBe("false");
    const open = within(panel);
    expect(open.getByText("Stand").nextElementSibling?.textContent).toBe("1");
    expect(open.getByText("Form").nextElementSibling?.textContent).toBe("3");
    expect(open.getByText("Sched").nextElementSibling?.textContent).toBe("6");
    expect(open.getByText("Pts").nextElementSibling?.textContent).toBe("2");
    expect(open.getByText(lastWeek.rows[1].blurb.map((sentence) => sentence.text).join(" "))).toBeTruthy();
    expect(panel.textContent).not.toMatch(/PR\./);
    expect(open.getByRole("link", { name: /Manager page/ }).getAttribute("href")).toBe(
      `/2026/managers/${lastWeek.rows[1].roster_id}/`,
    );
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(panel.getAttribute("aria-hidden")).toBe("true");
  });

  it("shows no manager link when the season has no managers file", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    fireEvent.click(cardButton("Lil Fridge"));
    expect(screen.queryByRole("link", { name: /Manager page/ })).toBeNull();
  });

  it("opens a card with no blurb to the four part ranks only", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    const button = cardButton("Bo Girds");
    fireEvent.click(button);
    expect(panelOf(button).textContent).toMatch(/^Stand\d+Form\d+Sched\d+Pts\d+$/);
  });

  it("closes every card when the week changes", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    fireEvent.click(cardButton("Lil Fridge"));
    fireEvent.click(chip(firstWeek.week));
    fireEvent.click(chip(lastWeek.week));
    expect(cardButton("Lil Fridge").getAttribute("aria-expanded")).toBe("false");
  });
});

describe("The week chips", () => {
  it("shows one chip per week in the file, with the last week chosen on load", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    const chips = within(screen.getByRole("group", { name: "Week" })).getAllByRole("button");
    expect(chips.map((button) => button.textContent)).toEqual(rankings.weeks.map((week) => String(week.week)));
    expect(chip(lastWeek.week).getAttribute("aria-pressed")).toBe("true");
    expect(chip(firstWeek.week).getAttribute("aria-pressed")).toBe("false");
  });

  it("puts the chips after the hero and before the first card", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    const group = screen.getByRole("group", { name: "Week" });
    const top = screen.getByRole("region", { name: "Rank 1" });
    expect(top.compareDocumentPosition(group) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(group.compareDocumentPosition(cards()[0]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows the cards of a week on a chip click, marks the chip, and sets the hash", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    fireEvent.click(chip(firstWeek.week));
    expect(chip(firstWeek.week).getAttribute("aria-pressed")).toBe("true");
    expect(chip(lastWeek.week).getAttribute("aria-pressed")).toBe("false");
    expect(cards().map((card) => card.textContent)).toEqual(
      firstWeek.rows.slice(1).map((row) => expect.stringContaining(row.name)),
    );
    expect(window.location.hash).toBe(`#week-${firstWeek.week}`);
  });

  it("picks the week that the hash names on load", () => {
    window.history.replaceState(null, "", `#week-${firstWeek.week}`);
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    expect(chip(firstWeek.week).getAttribute("aria-pressed")).toBe("true");
    expect(hero().getByRole("heading", { name: firstWeek.rows[0].name })).toBeTruthy();
  });

  it("picks the last week when the hash names no week in the file", () => {
    window.history.replaceState(null, "", "#week-99");
    render(<PowerRankings weeks={rankings.weeks} avatars={avatars} />);
    expect(chip(lastWeek.week).getAttribute("aria-pressed")).toBe("true");
  });
});

describe("Movement", () => {
  it("shows a dash for no change", () => {
    render(<Movement movement={0} />);
    expect(screen.getByText("–")).toBeTruthy();
    expect(screen.getByText("No change")).toBeTruthy();
  });

  it("shows a drawn down arrow with the count, and no arrow glyph", () => {
    render(<Movement movement={-3} />);
    expect(screen.getByText("Down").parentElement?.textContent).toBe("Down3");
    expect(document.querySelector("svg")?.dataset.arrow).toBe("down");
  });
});
