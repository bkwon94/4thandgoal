/**
 * Tests for the Front page, the home page at / while the front door is off. Most render the page with the fixed copy of the public/ data of cpc and read what a reader sees.
 * The NorCal test copies the fixed copy of the published files of norcal, and the registry tests build a temp public/ folder from week 6.
 */
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { cpSync, mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { type FixtureClient, fixturePublished, readFixtureSite } from "@/fixtures/sites";
import { weekPageJson } from "@/fixtures/week-page-json";
import fixture from "@cpc/rankings/fixtures/rankings.json";
import { week8 } from "@cpc/week/fixtures/week-page";
import { season } from "@/lib/config";
import HomePage from "./front-page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

/* The temp public/ folders that homeOver made, so each test removes its own folder. */
const roots: string[] = [];

afterEach(() => {
  cleanup();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
  vi.unstubAllGlobals();
  localStorage.clear();
  sessionStorage.clear();
  vi.restoreAllMocks();
});

describe("HomePage", () => {
  it("opens the hero on the Matchup of the Week of the latest week, with the winner by the margin as the title", async () => {
    const Home = await homeOfCpcWithoutReport();
    render(<Home />);
    const hero = screen.getByRole("region", { name: "Matchup of the Week" });
    // CPC week 8: The Blue Tent over London Cooking, 100.31 to 98.88 (AT-10).
    expect(within(hero).getByText("Week 08 // Matchup of the Week")).toBeTruthy();
    expect(within(hero).getByRole("heading", { level: 2 }).textContent).toBe("The Blue Tent by 1.43");
    expect(within(hero).getByText("Closest Finish")).toBeTruthy();
    expect(within(hero).getByText("The Blue Tent")).toBeTruthy();
    expect(within(hero).getByText("100.31")).toBeTruthy();
    expect(within(hero).getByText("London Cooking")).toBeTruthy();
    expect(within(hero).getByText("98.88")).toBeTruthy();
    // The first sentence of the blurb shows under the hero, outside its frame. The pipeline rewrites blurbs, so the test
    // reads the fixture.
    expect(hero.querySelector("p")).toBeNull();
    const sentence = hero.nextElementSibling!.querySelector("p")!.textContent!;
    expect(week8.blurbs.motw.startsWith(sentence)).toBe(true);
    expect(sentence.length).toBeLessThan(week8.blurbs.motw.length);
    expect(sentence.endsWith(".")).toBe(true);
    const read = within(hero).getByRole("link", { name: "Read Week 8" });
    expect(read.getAttribute("href")).toBe("/2026/week-08/");
  });

  it("has exactly one scene, in the hero of the Matchup, when no report takes over the top (AT-35)", async () => {
    const Home = await homeOfCpcWithoutReport();
    const { container } = render(<Home />);
    const hero = screen.getByRole("region", { name: "Matchup of the Week" });
    expect(container.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(1);
    expect(hero.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(1);
  });

  it("has no scene when the midseason report takes over the top, as the takeover keeps the static grid (AT-35, AT-44)", async () => {
    const Home = await homeOfClient("cpc");
    const { container } = render(<Home />);
    expect(screen.getByRole("region", { name: "2026 Midseason Report" })).toBeTruthy();
    expect(screen.queryByRole("region", { name: "Matchup of the Week" })).toBeNull();
    expect(container.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(0);
  });

  it("names the season and the league in the intro", () => {
    render(<HomePage />);
    expect(screen.getByText(`${season} // League Weekly`)).toBeTruthy();
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Cornerstone Fantasy Football League");
  });

  it("shows the parts in the order of the Front page", async () => {
    const Home = await homeOfCpcWithoutReport();
    render(<Home />);
    const main = screen.getByRole("main");
    const hero = within(main).getByRole("region", { name: "Matchup of the Week" });
    // The title of the hero is an h2 too, so the order of the chapters skips it.
    const order = [
      screen.getByRole("heading", { level: 1 }),
      hero,
      ...within(main)
        .getAllByRole("heading", { level: 2 })
        .filter((heading) => !hero.contains(heading)),
    ];
    expect(order.slice(2).map((heading) => heading.textContent)).toEqual([
      "Week 8 in four numbers",
      "Power Rankings",
      "Tools",
      "Weekly Reports",
    ]);
    for (let index = 1; index < order.length; index++) {
      expect(order[index - 1].compareDocumentPosition(order[index]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }
  });

  it("shows the four numbers of the latest week", async () => {
    const Home = await homeOfCpcWithoutReport();
    render(<Home />);
    const numbers = screen.getByRole("region", { name: "The week in numbers" });
    const labels = within(numbers)
      .getAllByRole("listitem")
      .map((item) => item.textContent);
    expect(labels).toHaveLength(4);
    expect(labels[2]).toContain("Closest1.43");
  });

  it("shows the top three of Power Rankings, led by All You Need Is Love, and a link to all teams", () => {
    render(<HomePage />);
    const top = screen.getByRole("list", { name: "Top three" });
    const rows = within(top).getAllByRole("listitem");
    expect(rows).toHaveLength(3);
    expect(rows[0].textContent).toContain("01");
    expect(rows[0].textContent).toContain("All You Need Is Love");
    expect(rows[0].textContent).toMatch(/11.5/);
    expect(rows[0].textContent).toContain("Up4");
    expect(rows[0].textContent).toContain("Playoff odds 81%");
    // Each row shows the avatar of its team from the latest week folder, since the home page sits outside it.
    expect(rows[0].querySelector("img")!.getAttribute("src")).toMatch(/^\/2026\/week-08\//);
    const all = within(screen.getByRole("main")).getByRole("link", { name: "All 12 teams" });
    expect(all.getAttribute("href")).toBe("/rankings/");
  });

  it("shows a tile for each tool, each with one line", () => {
    render(<HomePage />);
    const tools = screen.getByRole("region", { name: "Tools" });
    const links = within(tools).getAllByRole("link");
    expect(links.map((link) => link.getAttribute("href"))).toEqual(["/analyze/", "/2026/managers/"]);
    expect(links[0].textContent).toBe("Trade AnalyzerGrade a trade offer before you send it.");
    expect(links[0].querySelector("svg")).toBeTruthy();
  });

  it("shows a row for each published week, newest first, with its dates and its Matchup of the Week", () => {
    render(<HomePage />);
    const weeks = screen.getByRole("region", { name: "Weekly Reports" });
    expect(within(weeks).getByText("3 weeks")).toBeTruthy();
    const links = within(weeks).getAllByRole("link");
    expect(links.map((link) => link.getAttribute("href"))).toEqual(["/2026/week-08/", "/2026/week-07/", "/2026/week-06/"]);
    expect(links[2].textContent).toContain("Week 6");
    expect(links[2].textContent).toContain("Oct 15 – Oct 19, 2026");
    expect(links[0].textContent).toContain("The Blue Tent vs London Cooking");
  });

  it("shows no empty-list blurb when weeks exist", () => {
    render(<HomePage />);
    expect(screen.queryByText("No weeks are published yet.")).toBeNull();
  });

  it("fetches the teams in the background and stores them when a passphrase is stored", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    const teams = [{ roster_id: 1, team: "Gridiron Ghosts", manager: "Ana", avatar: null, players: [] }];
    const fetchStub = vi.fn().mockResolvedValue(new Response(JSON.stringify({ teams })));
    vi.stubGlobal("fetch", fetchStub);
    render(<HomePage />);

    // The list renders without a wait on the fetch.
    expect(screen.getByText("Week 6")).toBeTruthy();
    await waitFor(() => expect(sessionStorage.getItem("cpc.teams.2026")).not.toBeNull());
    expect(fetchStub.mock.calls[0][1].headers["X-League-Passphrase"]).toBe("localtest");
    expect(JSON.parse(sessionStorage.getItem("cpc.teams.2026")!).teams[0].team).toBe("Gridiron Ghosts");
  });

  it("skips the fetch with no passphrase", () => {
    const fetchStub = vi.fn();
    vi.stubGlobal("fetch", fetchStub);
    render(<HomePage />);
    expect(fetchStub).not.toHaveBeenCalled();
  });
});

/* A temp public/ folder with the week 5 and week 6 pages, the rankings file when one is given, and the managers file when asked. */
async function homeOver(rankings?: unknown, managers = false) {
  const root = tempRoot();
  for (const week of [5, 6]) {
    const folder = join(root, "public", "2026", `week-0${week}`);
    mkdirSync(folder, { recursive: true });
    writeFileSync(join(folder, "page.json"), weekPageJson({ week, dates: `Dates of week ${week}`, avatars: {} }));
  }
  if (rankings !== undefined) {
    writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankings));
  }
  if (managers) {
    // The tile only reads that the file exists, so an empty season is enough.
    writeFileSync(join(root, "public", "2026", "managers.json"), JSON.stringify({ schema_version: 1, season: 2026, through: 6, managers: [] }));
  }
  return homeAt(root);
}

/* A temp public/ folder with the fixed copy of the published files of one client, as its client build copies them. */
async function homeOfClient(slug: FixtureClient, skip: string[] = []) {
  const root = tempRoot();
  cpSync(fixturePublished(slug), join(root, "public"), {
    recursive: true,
    filter: (source) => !skip.includes(basename(source)),
  });
  return homeAt(root);
}

/* The files of a client with no report, so the tests of the plain home page hold whether or not it has published one. */
const homeWithoutReport = (slug: FixtureClient) => homeOfClient(slug, ["midseason.json", "sim.json"]);
const homeOfCpcWithoutReport = () => homeWithoutReport("cpc");

function tempRoot(): string {
  const root = mkdtempSync(join(tmpdir(), "home-page-"));
  roots.push(root);
  return root;
}

async function homeAt(root: string) {
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return (await import("./front-page")).default;
}

describe("HomePage of the NorCal data", () => {
  it("shows kaiedmonds by 10.62 as the title, Mitseeker5000 first, and one row for week 8", async () => {
    const Home = await homeWithoutReport("norcal");
    render(<Home />);
    const hero = screen.getByRole("region", { name: "Matchup of the Week" });
    // NorCal week 8: kaiedmonds over The Mean Machine, 132.38 to 121.76.
    expect(within(hero).getByRole("heading", { level: 2 }).textContent).toBe("kaiedmonds by 10.62");
    expect(within(hero).getByText("kaiedmonds")).toBeTruthy();
    expect(within(hero).getByText("The Mean Machine")).toBeTruthy();
    const rows = within(screen.getByRole("list", { name: "Top three" })).getAllByRole("listitem");
    expect(rows[0].textContent).toContain("Mitseeker5000");
    const weeks = within(screen.getByRole("region", { name: "Weekly Reports" })).getAllByRole("link");
    expect(weeks.map((link) => link.getAttribute("href"))).toEqual(["/2026/week-08/"]);
    expect(within(screen.getByRole("region", { name: "Weekly Reports" })).getByText("1 week")).toBeTruthy();
  });
});

describe("HomePage parts from the registry", () => {
  it("shows the top three of the fixture week, with the playoff odds as a word once a team is in", async () => {
    const Home = await homeOver(fixture);
    render(<Home />);
    const rows = within(screen.getByRole("list", { name: "Top three" })).getAllByRole("listitem");
    expect(rows[0].textContent).toContain("London Cooking");
    expect(rows[1].textContent).toContain("Lil Fridge");
    expect(rows[1].textContent).toContain("Playoff odds In");
    expect(rows[2].textContent).toContain("Bo Girds");
  });

  it("hides the Power Rankings chapter when the file is missing and still lists the weeks", async () => {
    const Home = await homeOver();
    render(<Home />);
    const hero = screen.getByRole("region", { name: "Matchup of the Week" });
    // The title of the hero is an h2 too, so the list of the chapters skips it.
    const headings = within(screen.getByRole("main"))
      .getAllByRole("heading", { level: 2 })
      .filter((heading) => !hero.contains(heading))
      .map((heading) => heading.textContent);
    expect(headings).toEqual(["Week 6 in four numbers", "Tools", "Weekly Reports"]);
    expect(screen.queryByRole("list", { name: "Top three" })).toBeNull();
    expect(within(screen.getByRole("region", { name: "Weekly Reports" })).getByRole("link", { name: /Week 6/ })).toBeTruthy();
  });

  it("opens the hero on the latest week of the folder", async () => {
    const Home = await homeOver(fixture);
    render(<Home />);
    const hero = screen.getByRole("region", { name: "Matchup of the Week" });
    expect(within(hero).getByRole("link", { name: "Read Week 6" }).getAttribute("href")).toBe("/2026/week-06/");
  });

  it("links the managers index from the tools only when the managers file exists", async () => {
    const With = await homeOver(fixture, true);
    render(<With />);
    const card = within(screen.getByRole("main")).getByRole("link", { name: /Managers/ });
    expect(card.getAttribute("href")).toBe("/2026/managers/");
    cleanup();
    const Without = await homeOver(fixture);
    render(<Without />);
    expect(within(screen.getByRole("main")).queryByRole("link", { name: /Managers/ })).toBeNull();
  });
});
