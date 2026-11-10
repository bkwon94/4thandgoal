/**
 * Tests for the week page. They render the page with the fixed copy of the public/ data and read what a reader sees.
 * The week 7 JSON is the fixture, so these tests break if the publish layout changes.
 */
import { act, cleanup, render, screen, within } from "@testing-library/react";
import { copyFileSync, mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fixturePublished, readFixtureSite } from "@/fixtures/sites";
import { weekPageJson } from "@/fixtures/week-page-json";
import WeekPage from "./page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

/* The hero and the eight chapters in the order of the spec (decision 05): the id each one sets and the words of its heading.
   The hero holds the level 1 heading of the page, and each chapter opens with a level 2 heading. */
const CHAPTERS = [
  { id: "motw", label: "Matchup of the Week" },
  { id: "matchups", label: "Every game" },
  { id: "game-changer", label: "Game Changer" },
  { id: "awards", label: "Awards" },
  { id: "leaders", label: "Position leaders" },
  { id: "trades", label: "Trades" },
  { id: "median", label: "The median game" },
  { id: "standings", label: "Standings" },
  { id: "next-week", label: "Next week" },
];

/* The reduced-motion setting of the system. A test turns it on, and the stub tells Framer Motion of the change. */
let reduceMotion = false;
let motionChange: (() => void) | undefined;

function setReducedMotion(on: boolean) {
  reduceMotion = on;
  motionChange?.();
}

/* jsdom has no matchMedia. Framer Motion reads it once per file and then listens for a change, so the stub runs at the top. */
vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      // Framer Motion asks for "(prefers-reduced-motion)" with no value, so the stub matches the feature name.
      get matches() {
        return reduceMotion && query.includes("prefers-reduced-motion");
      },
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: (_type: string, listener: () => void) => {
        motionChange = listener;
      },
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList,
);

/* jsdom has no IntersectionObserver. The stub keeps each observer and its targets, so a test reports a chapter in or out of view. */
const observers = new Set<ObserverStub>();

class ObserverStub {
  targets: Element[] = [];
  constructor(private callback: IntersectionObserverCallback) {
    observers.add(this);
  }
  observe(target: Element) {
    this.targets.push(target);
  }
  unobserve() {}
  disconnect() {
    observers.delete(this);
  }
  takeRecords() {
    return [];
  }
}

vi.stubGlobal("IntersectionObserver", ObserverStub);

/* Reports to each observer of the chapter with this id that the chapter is in or out of view, as a scroll does. */
function reportChapter(id: string, inView: boolean) {
  act(() => {
    for (const observer of observers) {
      const target = observer.targets.find((item) => item.id === id);
      if (!target) continue;
      const entry = { isIntersecting: inView, target } as IntersectionObserverEntry;
      observer["callback"]([entry], observer as unknown as IntersectionObserver);
    }
  });
}

/* The rail link of the chapter with this label. */
function railLink(label: string) {
  return within(screen.getByRole("navigation", { name: "Chapters" })).getByRole("link", { name: label });
}

/* The labels of the rail links that carry the current state. */
function currentLabels() {
  const links = within(screen.getByRole("navigation", { name: "Chapters" })).getAllByRole("link");
  return links.filter((link) => link.hasAttribute("aria-current")).map((link) => link.textContent);
}

/* Renders the week 7 report as the static export builds it. */
async function renderWeek7() {
  render(await WeekPage({ params: Promise.resolve({ season: "2026", week: "week-07" }) }));
}

/* The temp public/ folders that publicWithWeeks made, so each test removes its own folder. */
const roots: string[] = [];

afterEach(() => {
  cleanup();
  setReducedMotion(false);
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

afterAll(() => {
  vi.unstubAllGlobals();
});

describe("WeekPage chapters", () => {
  it("renders the nine chapters in the report's order with their ids", async () => {
    await renderWeek7();
    const main = screen.getByRole("main");
    const chapters = CHAPTERS.map(({ id }) => document.getElementById(id));
    chapters.forEach((chapter, index) => {
      expect(chapter, CHAPTERS[index].id).toBeTruthy();
      expect(main.contains(chapter)).toBe(true);
      expect(chapter?.textContent).toContain(CHAPTERS[index].label);
    });
    // Each chapter comes after the one before it in the document.
    for (let index = 1; index < chapters.length; index++) {
      const order = chapters[index - 1]!.compareDocumentPosition(chapters[index]!);
      expect(order & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }
  });

  it("opens each chapter after the hero with a level 2 heading in the order of the spec", async () => {
    await renderWeek7();
    const headings = within(screen.getByRole("main")).getAllByRole("heading", { level: 2 });
    const chapters = CHAPTERS.slice(1);
    expect(headings.map((heading) => heading.textContent)).toEqual(chapters.map(({ label }) => label));
    headings.forEach((heading, index) => {
      expect(document.getElementById(chapters[index].id)?.contains(heading)).toBe(true);
    });
  });
});

/* Renders the week 8 report of CPC, the week of the acceptance tests. */
async function renderWeek8() {
  render(await WeekPage({ params: Promise.resolve({ season: "2026", week: "week-08" }) }));
}

describe("WeekPage order of week 8 (AT-16)", () => {
  it("shows one scroll with no tabs: the hero, the four numbers, every chapter, and the footer, in order", async () => {
    await renderWeek8();
    const main = screen.getByRole("main");
    expect(within(main).queryByRole("tablist")).toBeNull();
    expect(within(main).queryByRole("tab")).toBeNull();
    const parts = [
      screen.getByRole("region", { name: "Matchup of the Week" }),
      screen.getByRole("region", { name: "The week in numbers" }),
      ...CHAPTERS.slice(1).map(({ label }) => screen.getByRole("region", { name: label })),
      screen.getByRole("navigation", { name: "Weeks" }),
    ];
    for (const part of parts) expect(main.contains(part)).toBe(true);
    for (let index = 1; index < parts.length; index++) {
      const order = parts[index - 1].compareDocumentPosition(parts[index]);
      expect(order & Node.DOCUMENT_POSITION_FOLLOWING, `part ${index} follows part ${index - 1}`).toBeTruthy();
    }
  });

  it("opens on the hero, which holds the one level 1 heading of the page, and no week line under the top band", async () => {
    await renderWeek8();
    const headings = screen.getAllByRole("heading", { level: 1 });
    expect(headings.map((heading) => heading.textContent)).toEqual(["The Blue Tent by 1.43"]);
    expect(screen.getByRole("region", { name: "Matchup of the Week" }).contains(headings[0])).toBe(true);
  });

  it("shows Joe Burrow at 42.48 in Game Changer", async () => {
    await renderWeek8();
    const chapter = screen.getByRole("region", { name: "Game Changer" });
    expect(within(chapter).getByText("Joe Burrow")).toBeTruthy();
    expect(within(chapter).getAllByRole("listitem")[0].textContent).toBe("Scored42.48");
  });

  it("links each open recap to one manager page of the season", async () => {
    await renderWeek8();
    const recap = document.getElementById("recap-3")!;
    // The closed recap stays in the DOM for find-in-page, and hidden="until-found" keeps its link out of the tab order.
    expect(recap.getAttribute("hidden")).toBe("until-found");
    act(() => {
      screen
        .getAllByRole("button")
        .find((button) => button.getAttribute("aria-controls") === "recap-3")!
        .click();
    });
    const links = within(recap).getAllByRole("link");
    expect(links).toHaveLength(1);
    expect(links[0].getAttribute("href")).toMatch(/^\/2026\/managers\/\d+\/$/);
  });
});

/* The bars of the Top Score tile of the week numbers: the week of each bar and the week of the lit bar. */
function topScoreBars() {
  const region = screen.getByRole("region", { name: "The week in numbers" });
  const tile = within(region)
    .getAllByRole("listitem")
    .find((item) => item.textContent?.startsWith("Top Score"))!;
  const chart = within(tile).getByRole("img");
  const weeks = [...chart.querySelectorAll("[data-week]")].map((bar) => Number(bar.getAttribute("data-week")));
  return { weeks, lit: Number(chart.querySelector("[data-lit]")?.getAttribute("data-week")) };
}

describe("WeekPage Trend tiles", () => {
  it("draws the top score of weeks 1 to 8 on week 8, with week 8 lit (AT-14)", async () => {
    await renderWeek8();
    expect(topScoreBars()).toEqual({ weeks: [1, 2, 3, 4, 5, 6, 7, 8], lit: 8 });
  });

  it("stops the trend at week 6 on the week 6 page (AT-16)", async () => {
    render(await WeekPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    expect(topScoreBars()).toEqual({ weeks: [1, 2, 3, 4, 5, 6], lit: 6 });
  });

  it("reads the number and one sentence of the Median trend (AT-15, AT-18)", async () => {
    await renderWeek8();
    const region = screen.getByRole("region", { name: "The week in numbers" });
    const median = within(region)
      .getAllByRole("listitem")
      .find((item) => item.textContent?.startsWith("Median"))!;
    expect(within(median).getByText("99.6")).toBeTruthy();
    expect(within(median).getByRole("img").getAttribute("aria-label")).toBe("Down from 103.87 in week 7.");
  });
});

describe("WeekPage chapter rail", () => {
  it("is a labeled navigation landmark with a link to each chapter in order", async () => {
    await renderWeek7();
    const rail = screen.getByRole("navigation", { name: "Chapters" });
    const links = within(rail).getAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual(CHAPTERS.map(({ label }) => label));
    expect(links.map((link) => link.getAttribute("href"))).toEqual(CHAPTERS.map(({ id }) => `#${id}`));
  });

  it("links only to ids that the page renders", async () => {
    await renderWeek7();
    const links = within(screen.getByRole("navigation", { name: "Chapters" })).getAllByRole("link");
    for (const link of links) {
      expect(document.getElementById(link.getAttribute("href")!.slice(1))).toBeTruthy();
    }
  });
});

describe("WeekPage chapter in view", () => {
  it("marks the chapter that the observer reports in view", async () => {
    await renderWeek7();
    expect(currentLabels()).toEqual([]);
    reportChapter("awards", true);
    expect(railLink("Awards").getAttribute("aria-current")).toBe("location");
    expect(currentLabels()).toEqual(["Awards"]);
  });

  it("moves the mark when another chapter comes into view", async () => {
    await renderWeek7();
    reportChapter("awards", true);
    reportChapter("awards", false);
    reportChapter("standings", true);
    expect(currentLabels()).toEqual(["Standings"]);
  });

  it("marks the later chapter when two chapters are in view, as its heading is the one in the band (AT-18)", async () => {
    await renderWeek7();
    reportChapter("median", true);
    reportChapter("standings", true);
    expect(currentLabels()).toEqual(["Standings"]);
    reportChapter("standings", false);
    expect(currentLabels()).toEqual(["The median game"]);
  });
});

describe("WeekPage with motion off", () => {
  it("renders every chapter and the rail at rest, and the mark still moves", async () => {
    setReducedMotion(true);
    await renderWeek7();
    // jsdom ignores opacity, so the test proves the content is there on the first render. The browser pass proves no motion.
    for (const { id, label } of CHAPTERS) {
      expect(document.getElementById(id)?.textContent).toContain(label);
      expect(railLink(label).getAttribute("href")).toBe(`#${id}`);
    }
    reportChapter("standings", true);
    expect(currentLabels()).toEqual(["Standings"]);
  });
});

/* The two slots of the week footer, the prior week first and the next week second. */
function footerSlots() {
  return within(screen.getByRole("navigation", { name: "Weeks" })).getAllByRole("listitem");
}

/* The link in a footer slot, or null when the slot is empty. */
function slotLink(slot: HTMLElement) {
  return within(slot).queryByRole("link");
}

describe("WeekPage week footer", () => {
  it("links week 6 on the left and leaves the right slot empty on week 7", async () => {
    await renderWeek7FromTemp();
    const [prior, next] = footerSlots();
    expect(slotLink(prior)?.getAttribute("href")).toBe("/2026/week-06/");
    expect(slotLink(prior)?.textContent).toContain("Week 6");
    expect(slotLink(next)).toBeNull();
    expect(next.textContent).toBe("");
  });

  it("comes after the next week chapter", async () => {
    await renderWeek7();
    const footer = screen.getByRole("navigation", { name: "Weeks" });
    const order = document.getElementById("next-week")!.compareDocumentPosition(footer);
    expect(order & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getByRole("main").contains(footer)).toBe(true);
  });
});

/* A temp public/ folder with weeks 5, 6, and 7, so week 6 has a week on each side. Weeks 6 and 7 are the real pages.
   Week 5 is only what the footer reads, because the test never renders it. Week 7 is the last week in that folder,
   so the footer test of the empty right slot reads it and not the fixed tree, which ends at week 8.
   Returns the week page read from that folder. */
async function publicWithWeeks() {
  const root = mkdtempSync(join(tmpdir(), "week-page-"));
  roots.push(root);
  const season = join(root, "public", "2026");
  for (const week of ["week-05", "week-06", "week-07"]) mkdirSync(join(season, week), { recursive: true });
  writeFileSync(join(season, "week-05", "page.json"), weekPageJson({ week: 5, dates: "Oct 8 – Oct 12, 2026" }));
  for (const week of ["week-06", "week-07"]) {
    copyFileSync(fixturePublished("cpc", "2026", week, "page.json"), join(season, week, "page.json"));
  }
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them to pick up the temp folder.
  vi.resetModules();
  return (await import("./page")).default;
}

/* Renders the week 7 report from the temp folder, where week 7 is the last week. */
async function renderWeek7FromTemp() {
  const Page = await publicWithWeeks();
  render(await Page({ params: Promise.resolve({ season: "2026", week: "week-07" }) }));
}

/* Renders the week 6 report from the temp folder. */
async function renderWeek6() {
  const Page = await publicWithWeeks();
  render(await Page({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
}

describe("WeekPage week footer with a week on each side", () => {
  it("links week 5 on the left and week 7 on the right on week 6", async () => {
    await renderWeek6();
    const [prior, next] = footerSlots();
    expect(slotLink(prior)?.getAttribute("href")).toBe("/2026/week-05/");
    expect(slotLink(next)?.getAttribute("href")).toBe("/2026/week-07/");
  });

  it("shows the week number as the lead and the dates under it in each link", async () => {
    await renderWeek6();
    const [prior, next] = footerSlots().map((slot) => slotLink(slot)!);
    expect(within(prior).getByText("Week 5")).toBeTruthy();
    expect(within(prior).getByText("Oct 8 – Oct 12, 2026")).toBeTruthy();
    expect(within(next).getByText("Week 7")).toBeTruthy();
    expect(within(next).getByText("Oct 22 – Oct 26, 2026")).toBeTruthy();
    // The side comes first, then the number, then the dates.
    expect(prior.textContent).toBe("PreviousWeek 5Oct 8 – Oct 12, 2026");
  });

  it("gives every footer link a path from the root", async () => {
    await renderWeek6();
    const links = within(screen.getByRole("navigation", { name: "Weeks" })).getAllByRole("link");
    expect(links.map((link) => link.getAttribute("href"))).toEqual(["/2026/week-05/", "/2026/week-07/"]);
  });

  it("shows the footer at rest with motion off", async () => {
    setReducedMotion(true);
    await renderWeek6();
    // jsdom ignores opacity, so the test proves the links are there on the first render. The browser pass proves no motion.
    const links = within(screen.getByRole("navigation", { name: "Weeks" })).getAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual([
      "PreviousWeek 5Oct 8 – Oct 12, 2026",
      "NextWeek 7Oct 22 – Oct 26, 2026",
    ]);
  });
});

/* A league with no median game: the pipeline writes median as null and no median blurb (AT-11). */
async function renderWeekWithNoMedian() {
  const root = mkdtempSync(join(tmpdir(), "week-page-"));
  roots.push(root);
  const folder = join(root, "public", "2026", "week-06");
  mkdirSync(folder, { recursive: true });
  const { median: _median, ...blurbs } = JSON.parse(weekPageJson()).blurbs;
  writeFileSync(join(folder, "page.json"), weekPageJson({ median: null, blurbs }));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  vi.resetModules();
  const Page = (await import("./page")).default;
  render(await Page({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
}

describe("WeekPage with no median game", () => {
  it("renders no Median Game chapter and no rail link to it", async () => {
    await renderWeekWithNoMedian();
    expect(document.getElementById("median")).toBeNull();
    expect(screen.queryByText("The median game")).toBeNull();
    const rail = within(screen.getByRole("navigation", { name: "Chapters" }));
    expect(rail.queryByRole("link", { name: "The median game" })).toBeNull();
    // The other chapters stay, so the rail still links the standings after the trades.
    const labels = rail.getAllByRole("link").map((link) => link.textContent);
    expect(labels.slice(labels.indexOf("Trades"), labels.indexOf("Trades") + 2)).toEqual(["Trades", "Standings"]);
  });
});
