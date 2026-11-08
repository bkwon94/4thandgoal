/**
 * Tests for the power rankings page. Each test builds a temp public/ folder, with or without the rankings file.
 * They read what a reader sees: the empty state, or the Ladder of the last week of the file with the week page avatars.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import fixture from "@cpc/rankings/fixtures/rankings.json";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  // A chip click sets the hash, so a test must not leak its week into the next test.
  window.history.replaceState(null, "", "/");
});

/* A temp public/ folder with the week 6 page, and the rankings file when one is given. */
async function pageOver(rankings?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "rankings-page-"));
  mkdirSync(join(root, "public", "2026", "week-06"), { recursive: true });
  writeFileSync(
    join(root, "public", "2026", "week-06", "page.json"),
    // Lil Fridge (roster 3) is rank 2 of week 6, so it heads the first card of the ladder.
    weekPageJson({ avatars: { "3": "avatars/3.jpg" } }),
  );
  if (rankings !== undefined) {
    writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankings));
  }
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return (await import("./page")).default;
}

describe("RankingsPage", () => {
  it("shows the empty state when the file is missing", async () => {
    const RankingsPage = await pageOver();
    render(<RankingsPage />);
    expect(screen.getByRole("heading", { level: 2, name: "Power Rankings" })).toBeTruthy();
    expect(screen.getByText("No power rankings are published yet.")).toBeTruthy();
    expect(within(screen.getByRole("main")).queryAllByRole("listitem")).toHaveLength(0);
  });

  it("shows the Ladder of the last week of the file with the avatars of the latest week page", async () => {
    const RankingsPage = await pageOver(fixture);
    render(<RankingsPage />);
    const main = screen.getByRole("main");
    expect(within(main).getByRole("heading", { level: 1 }).textContent).toBe("London Cooking");
    // London Cooking sits in the hero, so the first card is the team at rank 2.
    const cards = within(main).getAllByRole("listitem");
    expect(cards).toHaveLength(11);
    expect(cards[0].querySelector("img")?.getAttribute("src")).toBe("/2026/week-06/avatars/3.jpg");
  });

  it("drops the week line under the top band, because the hero names the week", async () => {
    const RankingsPage = await pageOver(fixture);
    render(<RankingsPage />);
    expect(document.body.textContent?.match(/WEEK 6/g)).toHaveLength(1);
  });

  it("moves the hero week with the chosen chip", async () => {
    const RankingsPage = await pageOver(fixture);
    render(<RankingsPage />);
    const page = document.body;
    const chip = (week: number) =>
      within(screen.getByRole("group", { name: "Week" })).getByRole("button", { name: `Week ${week}` });
    expect(page.textContent).toContain("WEEK 6");
    fireEvent.click(chip(1));
    expect(page.textContent).toContain("WEEK 1");
    expect(page.textContent).not.toContain("WEEK 6");
  });

  it("shows All You Need Is Love at 11-5, up 4, in the hero of CPC week 8", async () => {
    // The published rankings file of CPC, as the build copies it into public/.
    const cpc = JSON.parse(readFileSync(join(__dirname, "../../../../../../clients/cpc/published/2026/rankings.json"), "utf8"));
    const RankingsPage = await pageOver(cpc);
    render(<RankingsPage />);
    const hero = within(screen.getByRole("region", { name: "Rank 1" }));
    expect(hero.getByText("WEEK 8 // POWER RANKINGS")).toBeTruthy();
    expect(hero.getByRole("heading", { level: 1 }).textContent).toBe("All You Need Is Love");
    expect(hero.getByText("11-5")).toBeTruthy();
    expect(hero.getByText("Up").parentElement?.textContent).toBe("Up4");
    for (const label of ["Playoff", "Bye", "Seed"]) expect(hero.getByText(label)).toBeTruthy();
  });

  it("shows The Blue Tent of CPC week 8 closed at 05 large, with 9-7, up 3, the odds bar, and Playoff 75%", async () => {
    const RankingsPage = await pageOver(cpcRankings());
    render(<RankingsPage />);
    const head = blueTent();
    const card = head.closest("li")!;
    // The rank sits large in the plain raised panel at the top of the card, before the team.
    const rank = within(head).getByText("05");
    expect(rank.closest("[data-rank-panel]")).toBeTruthy();
    expect(rank.compareDocumentPosition(within(head).getByText("The Blue Tent")) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(within(head).getByText("9-7")).toBeTruthy();
    expect(within(head).getByText("Up").parentElement?.textContent).toBe("Up3");
    expect((card.querySelector("[data-odds-bar]") as HTMLElement).style.width).toBe("75%");
    expect(within(head).getByText(/^Playoff/).textContent).toBe("Playoff 75%");
    // The details stay closed until a tap.
    expect(head.getAttribute("aria-expanded")).toBe("false");
    expect(document.getElementById(head.getAttribute("aria-controls")!)!.getAttribute("hidden")).toBe("until-found");
  });

  it("opens The Blue Tent of CPC week 8 to the overview, the seven chips, and then the blurb", async () => {
    const cpc = cpcRankings();
    const RankingsPage = await pageOver(cpc);
    render(<RankingsPage />);
    const head = blueTent();
    fireEvent.click(head);
    expect(head.getAttribute("aria-expanded")).toBe("true");
    const panel = document.getElementById(head.getAttribute("aria-controls")!)!;
    expect(panel.hasAttribute("hidden")).toBe(false);
    const chips = within(panel).getAllByRole("listitem");
    expect(chips.map((chip) => chip.textContent)).toEqual([
      "Stand 6",
      "Form 6",
      "Sched 8",
      "Pts 7",
      "Move Up3",
      "Bye 22%",
      "Seed 5",
    ]);
    expect(chips[4].querySelector("svg")?.dataset.arrow).toBe("up");
    // The overview line is the rank, the record, and the move, and the blurb follows the chips.
    expect(panel.querySelector("p")?.textContent).toBe("Rank 5 · 9-7 · Up3");
    const row = cpc.weeks.at(-1).rows.find((each: { name: string }) => each.name === "The Blue Tent");
    const blurb = within(panel).getByText(row.blurb.map((sentence: { text: string }) => sentence.text).join(" "));
    expect(chips[6].compareDocumentPosition(blurb) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
});

/* The published rankings file of CPC, as the build copies it into public/. */
function cpcRankings() {
  return JSON.parse(readFileSync(join(__dirname, "../../../../../../clients/cpc/published/2026/rankings.json"), "utf8"));
}

/* The head of the card of The Blue Tent: the toggle whose name holds the team name. */
function blueTent() {
  return within(screen.getByRole("main")).getByRole("button", { name: /The Blue Tent/ });
}
