/**
 * Tests for the manager page route. Each test builds a temp public/ folder with a week page, the managers file, and the rankings file.
 * They read the static params and what a reader sees: the hero, the three numbers with their context lines, the season so far, and the chapters.
 * The Roster chapter reads the slot ranks of the grade, one line each.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import { managers as fixture } from "@cpc/managers/fixtures/managers";
import { rankings as rankingsFixture } from "@/fixtures/rankings";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

/* The last week of the rankings fixture, and a week 5 before it where each playoff percent is shifted by the given points.
   The fixture's own week before week 6 is week 1, which has no odds. */
function rankingsWithWeek5(shift: (rosterId: number) => number) {
  const last = rankingsFixture.weeks.at(-1)!;
  const rows = last.rows.map((row) => ({ ...row, odds: { ...row.odds!, playoff: row.odds!.playoff - shift(row.roster_id) } }));
  return { ...rankingsFixture, weeks: [rankingsFixture.weeks[0], { ...last, week: 5, rows }, last] };
}

/* A temp public/ folder with the week 6 page, the managers file unless managers is false, and the rankings file when given.
   Managers is the fixture when true, or the given file when it is an object. */
async function routeOver({ managers = true, rankings }: { managers?: boolean | object; rankings?: unknown } = {}) {
  const root = mkdtempSync(join(tmpdir(), "manager-page-"));
  mkdirSync(join(root, "public", "2026", "week-06"), { recursive: true });
  writeFileSync(
    join(root, "public", "2026", "week-06", "page.json"),
    weekPageJson({ avatars: { "9": "avatars/9.jpg" } }),
  );
  if (managers) writeFileSync(join(root, "public", "2026", "managers.json"), JSON.stringify(managers === true ? fixture : managers));
  if (rankings !== undefined) writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankings));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them.
  vi.resetModules();
  return import("./manager-page");
}

/* Renders the page of one roster and returns the group of the three numbers. */
async function renderManager(roster: string, options: Parameters<typeof routeOver>[0] = {}) {
  const { default: ManagerPage } = await routeOver(options);
  render(await ManagerPage({ params: Promise.resolve({ season: "2026", roster }) }));
  return screen.getByRole("group", { name: "Hero Numbers" });
}

/* The label, the number, and the context line of each number, as a reader reads them. */
function numbersIn(group: HTMLElement) {
  return [...group.querySelectorAll("dt")].map((term) => {
    const lines = [term.textContent];
    let next = term.nextElementSibling;
    while (next && next.tagName === "DD") {
      lines.push(next.textContent);
      next = next.nextElementSibling;
    }
    return lines;
  });
}

describe("generateStaticParams", () => {
  it("lists one page per roster in the managers file", async () => {
    const { generateStaticParams } = await routeOver({ rankings: rankingsFixture });
    const params = generateStaticParams();
    expect(params).toHaveLength(12);
    expect(params).toContainEqual({ season: "2026", roster: "9" });
  });

  it("lists no page when the managers file is missing", async () => {
    const { generateStaticParams } = await routeOver({ managers: false });
    expect(generateStaticParams()).toEqual([]);
  });
});

describe("generateMetadata", () => {
  it("titles the page with the team name", async () => {
    const { generateMetadata } = await routeOver({ rankings: rankingsFixture });
    const metadata = await generateMetadata({ params: Promise.resolve({ season: "2026", roster: "9" }) });
    expect(metadata.title).toBe("Maye d'force B with U · Cornerstone Fantasy Football League");
  });
});

describe("ManagerPage", () => {
  it("shows the team name as the page heading, the owner, the record, and the standing", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Maye d'force B with U");
    const hero = screen.getByRole("heading", { level: 1 }).closest("section")!;
    expect(hero.textContent).toContain(fixture.managers[8].team.owner);
    expect(hero.textContent).toContain("7-5 · 4th of 12");
    // The team name sits next to the avatar, so the image is decorative and has no role to query.
    expect(hero.querySelector("img")?.getAttribute("src")).toBe("/2026/week-06/avatars/9.jpg");
  });

  it("shows the three numbers, each with one context line", async () => {
    // Week 5 sits 9 points under week 6 for this team, so the odds went up 9.
    const group = await renderManager("9", { rankings: rankingsWithWeek5(() => 9) });
    expect(numbersIn(group)).toEqual([
      ["Grade", "B", "QB fine · RB thin · WR fine · TE fine"],
      ["Playoff Odds", "71%", "up 9"],
      ["Power Rank", "4th of 12", "down 2"],
    ]);
  });

  it("reads a drop in the odds and a rise in the rank", async () => {
    // London Cooking rose 4 places to 1st. Week 5 sits 4 points over week 6 for it.
    const group = await renderManager("5", { rankings: rankingsWithWeek5(() => -4) });
    expect(numbersIn(group).slice(1)).toEqual([
      ["Playoff Odds", "97%", "down 4"],
      ["Power Rank", "1st of 12", "up 4"],
    ]);
  });

  it("reads no change for a flat week", async () => {
    // Bo Girds kept 3rd, and week 5 has the same odds.
    const group = await renderManager("6", { rankings: rankingsWithWeek5(() => 0) });
    expect(numbersIn(group).slice(1)).toEqual([
      ["Playoff Odds", "89%", "no change"],
      ["Power Rank", "3rd of 12", "no change"],
    ]);
  });

  it("shows no odds line when the week before has no odds", async () => {
    const group = await renderManager("9", { rankings: rankingsFixture });
    expect(numbersIn(group)[1]).toEqual(["Playoff Odds", "71%"]);
  });

  it("shows a dash with no line when no week has odds", async () => {
    const noOdds = {
      ...rankingsFixture,
      weeks: rankingsFixture.weeks.map((week) => ({ ...week, rows: week.rows.map(({ odds: _odds, ...row }) => row) })),
    };
    const group = await renderManager("9", { rankings: noOdds });
    expect(numbersIn(group)[1]).toEqual(["Playoff Odds", "—"]);
  });

  it("shows the five chapters, each with its heading", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const main = screen.getByRole("main");
    expect(within(main).getAllByRole("heading", { level: 2 }).map((heading) => heading.textContent)).toEqual([
      "Season So Far",
      "Roster",
      "Best Adds",
      "Top Performers",
      "Moves",
    ]);
  });

  it("lists the four slot ranks in the Roster chapter, one line each, in the file's order", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const roster = screen.getByRole("heading", { level: 2, name: "Roster" }).closest("section")!;
    expect(within(roster).getAllByRole("listitem").map((line) => line.textContent)).toEqual([
      "QB · 1st of 12 · fine",
      "RB · 2nd of 12 · thin",
      "WR · 12th of 12 · fine",
      "TE · 3rd of 12 · fine",
    ]);
  });

  it("shows a dash with no line in the hero and one quiet line in the Roster chapter with no grade", async () => {
    const managers = fixture.managers.map((entry) => (entry.roster_id === 9 ? { ...entry, grade: null } : entry));
    const group = await renderManager("9", { managers: { ...fixture, managers }, rankings: rankingsFixture });
    expect(numbersIn(group)[0]).toEqual(["Grade", "—"]);
    const roster = screen.getByRole("heading", { level: 2, name: "Roster" }).closest("section")!;
    expect(within(roster).queryAllByRole("listitem")).toHaveLength(0);
    expect(within(roster).getByText("No grade yet.")).toBeTruthy();
  });

  it("shows the moves totals and the weeks newest first, with one line for an empty week", async () => {
    // London Cooking made two adds, one drop, and one trade, and no move in weeks 6, 5, 3, and 1.
    await renderManager("5", { rankings: rankingsFixture });
    const moves = screen.getByRole("heading", { name: "Moves" }).closest("section")!;
    const totals = within(moves).getByRole("group", { name: "Move Totals" });
    expect([...totals.querySelectorAll("dd")].map((count) => count.textContent)).toEqual(["2", "1", "1"]);
    const weeks = within(moves).getAllByRole("group", { name: /^Week / });
    expect(weeks.map((group) => group.getAttribute("aria-label"))).toEqual([
      "Week 6",
      "Week 5",
      "Week 4",
      "Week 3",
      "Week 2",
      "Week 1",
    ]);
    expect(within(weeks[0]).getByText("No moves.")).toBeTruthy();
    expect(within(moves).getAllByText("No moves.")).toHaveLength(4);
  });

  it("shows the season so far: the dots, the bench line, and the four season stats", async () => {
    // Maye d'force B with U won weeks 1, 2, 5, and 6, and beat the median in weeks 1, 5, and 6.
    await renderManager("9", { rankings: rankingsFixture });
    const line = screen.getByRole("img", { name: "Points per week against the league median" });
    expect(line.querySelectorAll("[data-result]")).toHaveLength(6);
    expect(line.querySelectorAll('[data-result="win"]')).toHaveLength(4);
    expect(screen.getByText(/Worst in week 4: 13\.68 points, Drake Maye sat\.$/)).toBeTruthy();
    const stats = screen.getByRole("group", { name: "Season Numbers" });
    const numbers = [...stats.querySelectorAll("dt")].map((term) => term.nextElementSibling?.textContent);
    expect(numbers).toEqual(["158.96", "87.93", "W2", "3-3"]);
  });

  it("lists the best adds and the top performers in order", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const names = (id: string) =>
      [...document.getElementById(id)!.querySelectorAll("li b")].map((name) => name.textContent);
    expect(names("best-adds")).toEqual(fixture.managers[8].best_adds.map((add) => add.name));
    expect(names("top-performers")).toEqual(fixture.managers[8].top_performers.map((performer) => performer.name));
    expect(names("best-adds")).toEqual(["Alvin Kamara", "Kyler Murray", "Emmett Johnson"]);
  });

  it("lists the five chapters in the chapter rail", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const rail = screen.getByRole("navigation", { name: "Chapters" });
    expect(within(rail).getAllByRole("link").map((link) => [link.textContent, link.getAttribute("href")])).toEqual([
      ["Season So Far", "#season"],
      ["Roster", "#roster"],
      ["Best Adds", "#best-adds"],
      ["Top Performers", "#top-performers"],
      ["Moves", "#moves"],
    ]);
  });
});
