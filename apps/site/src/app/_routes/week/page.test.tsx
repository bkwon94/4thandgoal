/**
 * Tests for the week page. They render the page with the real public/ data and read what a reader sees.
 * The week 7 JSON is the fixture, so these tests break if the publish layout changes.
 */
import { act, cleanup, render, screen, within } from "@testing-library/react";
import { copyFileSync, mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";
import WeekPage from "./page";

/* The nine chapters in the report's order: the id each chapter sets and the words of its own label. */
const CHAPTERS = [
  { id: "motw", label: "Matchup of the Week" },
  { id: "game-changer", label: "Game Changer" },
  { id: "awards", label: "Awards" },
  { id: "leaders", label: "Position Leaders" },
  { id: "trades", label: "Trades" },
  { id: "matchups", label: "All Matchups" },
  { id: "median", label: "The Median Game" },
  { id: "standings", label: "Standings" },
  { id: "next-week", label: "Next Week" },
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

  it("opens each chapter with a level 2 heading in the report's order", async () => {
    await renderWeek7();
    const headings = within(screen.getByRole("main")).getAllByRole("heading", { level: 2 });
    // The matchup of the week heading also holds its reason tag, so each heading starts with the chapter label.
    expect(headings).toHaveLength(CHAPTERS.length);
    headings.forEach((heading, index) => {
      expect(heading.textContent?.startsWith(CHAPTERS[index].label)).toBe(true);
      expect(document.getElementById(CHAPTERS[index].id)?.contains(heading)).toBe(true);
    });
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

  it("marks the chapter nearest the top when two chapters are in view", async () => {
    await renderWeek7();
    reportChapter("median", true);
    reportChapter("standings", true);
    expect(currentLabels()).toEqual(["The Median Game"]);
    reportChapter("median", false);
    expect(currentLabels()).toEqual(["Standings"]);
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
   so the footer test of the empty right slot reads it and not the real tree, which gains a week on each publish.
   Returns the week page read from that folder. */
async function publicWithWeeks() {
  const root = mkdtempSync(join(tmpdir(), "week-page-"));
  roots.push(root);
  const season = join(root, "public", "2026");
  for (const week of ["week-05", "week-06", "week-07"]) mkdirSync(join(season, week), { recursive: true });
  writeFileSync(join(season, "week-05", "page.json"), weekPageJson({ week: 5, dates: "Oct 8 – Oct 12, 2026" }));
  for (const week of ["week-06", "week-07"]) {
    copyFileSync(join(process.cwd(), "..", "..", "clients", "cpc", "published", "2026", week, "page.json"), join(season, week, "page.json"));
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
    // The number comes before the dates in the link.
    expect(prior.textContent).toBe("Week 5Oct 8 – Oct 12, 2026");
  });

  it("gives every footer link the base path", async () => {
    // A build can set a base path, so the test sets one before the page loads its config.
    vi.stubEnv("NEXT_PUBLIC_BASE_PATH", "/cpc");
    await renderWeek6();
    const links = within(screen.getByRole("navigation", { name: "Weeks" })).getAllByRole("link");
    expect(links.map((link) => link.getAttribute("href"))).toEqual(["/cpc/2026/week-05/", "/cpc/2026/week-07/"]);
  });

  it("shows the footer at rest with motion off", async () => {
    setReducedMotion(true);
    await renderWeek6();
    // jsdom ignores opacity, so the test proves the links are there on the first render. The browser pass proves no motion.
    const links = within(screen.getByRole("navigation", { name: "Weeks" })).getAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual(["Week 5Oct 8 – Oct 12, 2026", "Week 7Oct 22 – Oct 26, 2026"]);
  });
});
