/**
 * Tests for the manager page route. Each test builds a temp public/ folder with a week page, the managers file, and the rankings file.
 * They read the static params and what a reader sees: the back link, the hero with the grade, the tiles, and the chips, then the chapters.
 * The Roster chapter reads a tile for each slot rank of the grade, then the ranks of the grade parts.
 * The Grade dial test reads the published managers file and rankings file of CPC, week 8.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import { managers as fixture } from "@cpc/managers/fixtures/managers";
import { rankings as rankingsFixture } from "@cpc/rankings/fixtures/rankings";

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

/* Renders the page of one roster and returns the group of the three hero tiles. */
async function renderManager(roster: string, options: Parameters<typeof routeOver>[0] = {}) {
  const { default: ManagerPage } = await routeOver(options);
  render(await ManagerPage({ params: Promise.resolve({ season: "2026", roster }) }));
  return screen.getByRole("group", { name: "Hero Numbers" });
}

/* The label, the number, and the note of each tile, as a reader reads them. */
function numbersIn(group: HTMLElement) {
  return [...group.children].map((tile) => [...tile.children].map((line) => line.textContent));
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
  it("opens with a back link to all managers", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const main = screen.getByRole("main");
    const back = within(main).getAllByRole("link")[0];
    expect(back.textContent).toBe("← All Managers");
    expect(back.getAttribute("href")).toBe("/2026/managers/");
  });

  it("shows the team name as the page heading, the owner, the record, and the standing in the hero", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const hero = screen.getByRole("region", { name: "Maye d'force B with U" });
    expect(within(hero).getByRole("heading", { level: 1 }).textContent).toBe("Maye d'force B with U");
    expect(hero.textContent).toContain(fixture.managers[8].team.owner);
    expect(hero.textContent).toContain("7-5 · 4th of 12");
    // The team name sits next to the avatar, so the image is decorative and has no role to query.
    expect(hero.querySelector("img")?.getAttribute("src")).toBe("/2026/week-06/avatars/9.jpg");
  });

  it("shows the grade letter as the big number of the hero, with the grade text beside it", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const hero = screen.getByRole("region", { name: "Maye d'force B with U" });
    expect(within(hero).getByRole("button", { name: "Grade B, how the grade reads" }).textContent).toBe("B");
    expect(within(hero).getByText("Strong at QB and TE. Soft at WR. Thin at RB.")).toBeTruthy();
  });

  it("shows the three hero tiles, Playoff, Bye, and Seed", async () => {
    // Week 5 sits 9 points under week 6 for this team, so the odds went up 9.
    const group = await renderManager("9", { rankings: rankingsWithWeek5(() => 9) });
    expect(numbersIn(group)).toEqual([
      ["Playoff", "71%", "up 9"],
      ["Bye", "9%"],
      ["Seed", "4th"],
    ]);
  });

  it("reads a drop in the odds", async () => {
    // Week 5 sits 4 points over week 6 for London Cooking.
    const group = await renderManager("5", { rankings: rankingsWithWeek5(() => -4) });
    expect(numbersIn(group)[0]).toEqual(["Playoff", "97%", "down 4"]);
  });

  it("reads no change for a flat week", async () => {
    const group = await renderManager("6", { rankings: rankingsWithWeek5(() => 0) });
    expect(numbersIn(group)[0]).toEqual(["Playoff", "89%", "no change"]);
  });

  it("shows no odds note when the week before has no odds", async () => {
    const group = await renderManager("9", { rankings: rankingsFixture });
    expect(numbersIn(group)[0]).toEqual(["Playoff", "71%"]);
  });

  it("shows a dash in each tile when no week has odds", async () => {
    const noOdds = {
      ...rankingsFixture,
      weeks: rankingsFixture.weeks.map((week) => ({ ...week, rows: week.rows.map(({ odds: _odds, ...row }) => row) })),
    };
    const group = await renderManager("9", { rankings: noOdds });
    expect(numbersIn(group)).toEqual([
      ["Playoff", "—"],
      ["Bye", "—"],
      ["Seed", "—"],
    ]);
  });

  it("shows a W or L chip for each week in the hero", async () => {
    // Maye d'force B with U won weeks 1, 2, 5, and 6, and lost weeks 3 and 4.
    await renderManager("9", { rankings: rankingsFixture });
    const results = screen.getByRole("list", { name: "Results By Week" });
    expect(within(results).getAllByRole("listitem").map((item) => [...item.children].map((part) => part.textContent))).toEqual([
      ["W", "1"],
      ["W", "2"],
      ["L", "3"],
      ["L", "4"],
      ["W", "5"],
      ["W", "6"],
    ]);
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

  it("shows a tile for each position slot in the Roster chapter, with its rank and its depth, in the file's order", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const slots = screen.getByRole("list", { name: "Slot Ranks" });
    // The lines of a tile are the boxes with no box inside: the label, the number, and the note.
    const linesOf = (item: HTMLElement) =>
      [...item.querySelectorAll("div")].filter((box) => box.children.length === 0).map((line) => line.textContent);
    expect(within(slots).getAllByRole("listitem").map(linesOf)).toEqual([
      ["QB", "1st", "of 12 · fine"],
      ["RB", "2nd", "of 12 · thin"],
      ["WR", "12th", "of 12 · fine"],
      ["TE", "3rd", "of 12 · fine"],
    ]);
  });

  it("lists the four grade parts with their ranks under the slot tiles", async () => {
    await renderManager("9", { rankings: rankingsFixture });
    const parts = screen.getByRole("list", { name: "Grade Parts" });
    expect(within(parts).getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      "Projection Ahead9th of 12",
      "Season Production12th of 12",
      "Trade Value3rd of 12",
      "Depth And Holes6th of 12",
    ]);
  });

  it("shows a dash in the grade box of the hero and one quiet line in the Roster chapter with no grade", async () => {
    const managers = fixture.managers.map((entry) => (entry.roster_id === 9 ? { ...entry, grade: null } : entry));
    await renderManager("9", { managers: { ...fixture, managers }, rankings: rankingsFixture });
    const hero = screen.getByRole("region", { name: "Maye d'force B with U" });
    expect(within(hero).queryByRole("button")).toBeNull();
    expect(within(hero).getByLabelText("No grade").textContent).toBe("—");
    const roster = screen.getByRole("heading", { level: 2, name: "Roster" }).closest("section")!;
    expect(within(roster).queryAllByRole("list")).toHaveLength(0);
    expect(within(roster).getByText("No grade yet.")).toBeTruthy();
  });

  it("shows the moves totals and the weeks newest first, with one line for an empty week", async () => {
    // London Cooking made two adds, one drop, and one trade, and no move in weeks 6, 5, 3, and 1.
    await renderManager("5", { rankings: rankingsFixture });
    const moves = screen.getByRole("heading", { name: "Moves" }).closest("section")!;
    const totals = within(moves).getByRole("group", { name: "Move Totals" });
    expect([...totals.children].map((tile) => tile.children[1].textContent)).toEqual(["2", "1", "1"]);
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

  it("shows the season so far: the dots, the bench line, and the three season tiles", async () => {
    // Maye d'force B with U won weeks 1, 2, 5, and 6, and beat the median in weeks 1, 5, and 6.
    await renderManager("9", { rankings: rankingsFixture });
    const line = screen.getByRole("img", { name: "Points per week against the league median" });
    expect(line.querySelectorAll("[data-result]")).toHaveLength(6);
    expect(line.querySelectorAll('[data-result="win"]')).toHaveLength(4);
    expect(screen.getByText(/Worst in week 4: 13\.68 points, Drake Maye sat\.$/)).toBeTruthy();
    const stats = screen.getByRole("group", { name: "Season Numbers" });
    const numbers = [...stats.children].map((tile) => tile.children[1].textContent);
    expect(numbers).toEqual(["698.3", "3-3", "158.96"]);
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

describe("The Grade dial in Season So Far", () => {
  /* A published file of CPC, as the build copies it into public/. */
  const published = (name: string) =>
    JSON.parse(readFileSync(join(__dirname, "../../../../../../clients/cpc/published/2026", name), "utf8"));

  it("shows A, the grade read, and arcs 4th, 6th, 7th, and 7th for The Blue Tent of CPC week 8", async () => {
    await renderManager("1", { managers: published("managers.json"), rankings: published("rankings.json") });
    const season = within(document.getElementById("season")!);
    const grade = within(season.getByRole("group", { name: "Roster Grade" }));
    expect(grade.getByText("A")).toBeTruthy();
    expect(grade.getByText("Strong at QB and TE. Soft at RB.")).toBeTruthy();
    const arcs = within(grade.getByRole("list", { name: "Grade Dial" })).getAllByRole("img");
    expect(arcs.map((arc) => arc.getAttribute("aria-label"))).toEqual([
      "Projection Ahead: 4th of 12, 45% of the grade",
      "Season Production: 6th of 12, 30% of the grade",
      "Trade Value: 7th of 12, 10% of the grade",
      "Depth And Holes: 7th of 12, 15% of the grade",
    ]);
    expect(arcs.map((arc) => arc.querySelectorAll("[data-blade]").length)).toEqual([12, 12, 12, 12]);
    expect(arcs.map((arc) => arc.querySelectorAll('[data-blade][data-on="true"]').length)).toEqual([9, 7, 6, 6]);
  });
});
