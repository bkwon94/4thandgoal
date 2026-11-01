/**
 * Tests for the home page. Most render the page with the real public/ data and read what a reader sees.
 * The week 6 JSON is the fixture, so these tests break if the publish layout changes. The rankings tests build a temp public/ folder.
 */
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/lib/week-page-fixture";
import fixture from "@/components/rankings/fixture.json";
import { season } from "@/lib/config";
import HomePage from "./page";

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
  it("names the league and the page", () => {
    render(<HomePage />);
    expect(screen.getByText("Cornerstone Fantasy Football League")).toBeTruthy();
    expect(screen.queryByText("League Weekly")).toBeNull();
    // The label and the red season number are separate text nodes.
    expect(screen.getByText("SEASON")).toBeTruthy();
    expect(screen.getByText(String(season)).className).toContain("text-red");
    expect(screen.getByText("Weekly Reports")).toBeTruthy();
  });

  it("links week 6 with its dates", () => {
    render(<HomePage />);
    const link = screen.getAllByRole("link").find((item) => item.getAttribute("href") === "/2026/week-06/");
    expect(link).toBeTruthy();
    expect(screen.getByText("Week 6")).toBeTruthy();
    expect(screen.getByText("Oct 15 – Oct 19, 2026")).toBeTruthy();
  });

  it("shows no empty-list blurb when weeks exist", () => {
    render(<HomePage />);
    expect(screen.queryByText("No weeks are published yet.")).toBeNull();
  });

  it("links the trade analyzer", () => {
    render(<HomePage />);
    const link = within(screen.getByRole("main")).getByRole("link", { name: /Trade Analyzer/ });
    expect(link.getAttribute("href")).toMatch(/\/analyze\/$/);
  });

  it("puts the trade analyzer before the weeks", () => {
    render(<HomePage />);
    const analyzer = within(screen.getByRole("main")).getByRole("link", { name: /Trade Analyzer/ });
    const week = screen.getAllByRole("link").find((item) => item.getAttribute("href") === "/2026/week-06/")!;
    expect(analyzer.compareDocumentPosition(week) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
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
  const root = mkdtempSync(join(tmpdir(), "home-page-"));
  roots.push(root);
  for (const week of [5, 6]) {
    const folder = join(root, "public", "2026", `week-0${week}`);
    mkdirSync(folder, { recursive: true });
    writeFileSync(join(folder, "page.json"), weekPageJson({ week, dates: `Dates of week ${week}`, avatars: {} }));
  }
  if (rankings !== undefined) {
    writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankings));
  }
  if (managers) {
    // The card only reads that the file exists, so an empty season is enough.
    writeFileSync(join(root, "public", "2026", "managers.json"), JSON.stringify({ schema_version: 1, season: 2026, through: 6, managers: [] }));
  }
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return (await import("./page")).default;
}

describe("HomePage power rankings", () => {
  it("opens each chapter with a level-two heading, in order", async () => {
    const Home = await homeOver(fixture);
    render(<Home />);
    const headings = within(screen.getByRole("main"))
      .getAllByRole("heading", { level: 2 })
      .map((heading) => heading.textContent);
    expect(headings).toEqual(["Tools", "Power Rankings", "Weekly Reports"]);
  });

  it("shows the top three, the biggest mover, and the link to the rankings", async () => {
    const Home = await homeOver(fixture);
    render(<Home />);
    // The menu row in the banner has a Power Rankings link too, so the test reads the chapter in the page content.
    expect(within(screen.getByRole("main")).getByText("Power Rankings")).toBeTruthy();
    const link = screen.getByRole("link", { name: /Top Three/ });
    expect(link.getAttribute("href")).toBe("/rankings/");
    const top = Array.from(link.querySelectorAll("li")).map((item) => item.textContent);
    expect(top).toEqual(["1London Cooking", "2Lil Fridge", "3Bo Girds"]);
    // London Cooking moved up four places, the largest movement in the fixture week.
    expect(link.textContent).toContain("Biggest mover: ▲Up4 London Cooking");
  });

  it("puts the chapter after the analyzer and before the weeks", async () => {
    const Home = await homeOver(fixture);
    render(<Home />);
    // The masthead link to the home page sits in the banner, above every chapter.
    const links = screen
      .getAllByRole("link")
      .filter((link) => !link.closest("header"))
      .map((link) => link.getAttribute("href"));
    expect(links).toEqual(["/analyze/", "/rankings/", "/2026/week-06/", "/2026/week-05/"]);
  });

  it("hides the chapter when the file is missing and still lists the weeks", async () => {
    const Home = await homeOver();
    render(<Home />);
    expect(within(screen.getByRole("main")).queryByText("Power Rankings")).toBeNull();
    const headings = within(screen.getByRole("main"))
      .getAllByRole("heading", { level: 2 })
      .map((heading) => heading.textContent);
    expect(headings).toEqual(["Tools", "Weekly Reports"]);
    expect(screen.queryByRole("link", { name: /Top Three/ })).toBeNull();
    expect(within(screen.getByRole("main")).getByRole("link", { name: /Week 6/ })).toBeTruthy();
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
