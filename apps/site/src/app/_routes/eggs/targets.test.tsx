/**
 * Tests for the targets of the egg hunt on the real pages of CPC 2026: each class of target of the catalog carries a
 * stable id on each element, and the listener sends one check for each action on the real markup, and none for a tap.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { EggCheck } from "@cpc/eggs/lib/api";
import { listenForEggs, SELECT_SETTLE_MS, TAP_GAP_MS } from "@cpc/eggs/listener/listener";
import midseasonFixture from "@cpc/midseason/fixtures/midseason.json";
import { sim as simFixture } from "@cpc/sim/fixtures/sim";
import { beatsOf } from "@cpc/sim/replay/beats";
import { replaySeason } from "@cpc/sim/replay/season";
import { SimReplay } from "@cpc/sim/replay/sim-replay";
import AnalyzeResult from "@cpc/analyzer/form/analyze-result";
import { analyzeResponse } from "@cpc/analyzer/lib/fixtures/api";
import type { AnalyzeResponse } from "@cpc/analyzer/lib/analyze-types";
import NotFound from "../../not-found";
import { publicOver, removePublics } from "../midseason/temp-public";

/* jsdom has no matchMedia and no IntersectionObserver. Framer Motion and Reveal read them. */
vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList,
);
vi.stubGlobal(
  "IntersectionObserver",
  class {
    observe() {}
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  },
);

let sent: EggCheck[];
let stop: (() => void) | undefined;

beforeEach(() => {
  sent = [];
});

afterEach(() => {
  stop?.();
  stop = undefined;
  cleanup();
  removePublics();
  vi.useRealTimers();
  vi.restoreAllMocks();
});

/* Starts the listener of the egg hunt on the page, as the hunt does. */
function listen(page: string) {
  stop = listenForEggs(document, { page: () => page, send: (check) => sent.push(check) });
}

/* Each stable id on the page, in the order of the page. */
const ids = () => [...document.querySelectorAll("[data-stable-id]")].map((element) => element.getAttribute("data-stable-id")!);
const idsOf = (prefix: string) => ids().filter((id) => id.startsWith(`${prefix}-`));
const target = (id: string) => document.querySelector(`[data-stable-id="${id}"]`)!;

/* A tap on an element: the pointer goes down and comes up, then the click. */
function tap(element: Element, gap = 100) {
  fireEvent.pointerDown(element, { isPrimary: true });
  fireEvent.pointerUp(element, { isPrimary: true });
  fireEvent.click(element);
  act(() => {
    vi.advanceTimersByTime(gap);
  });
}

/* Each id once, so a check names one element of the page. */
function expectUnique(list: string[]) {
  expect(list.filter((id, index) => list.indexOf(id) !== index)).toEqual([]);
}

const WEEK_8 = JSON.parse(readFileSync(join(process.cwd(), "public", "2026", "week-08", "page.json"), "utf8"));

describe("the targets of the week page", () => {
  async function renderWeek8() {
    vi.resetModules();
    const { default: WeekPage } = await import("../week/page");
    render(await WeekPage({ params: Promise.resolve({ season: "2026", week: "week-08" }) }));
  }

  it("gives each number tile, award tile, leaders row, median bar, next game, heading, and blurb a stable id", async () => {
    await renderWeek8();
    expect(idsOf("number").length).toBeGreaterThanOrEqual(3);
    expect(idsOf("award")).toHaveLength(WEEK_8.awards.length);
    expect(idsOf("median")).toHaveLength(WEEK_8.median.bars.length);
    expect(idsOf("next-game")).toHaveLength(WEEK_8.next.length);
    expect(idsOf("leader")).toHaveLength(WEEK_8.leaders[0].rows.length);
    expect(idsOf("heading")).toEqual(expect.arrayContaining(["heading-awards", "heading-median", "heading-next-week"]));
    expect(idsOf("blurb").length).toBeGreaterThanOrEqual(4);
    // The median bar of a roster names the roster, so two renders of the week give one id.
    expect(idsOf("median")).toContain(`median-${WEEK_8.median.bars[0].team.roster_id}`);
    expectUnique(ids());
  });

  it("gives the recap line of each game a stable id once its card opens, and a normal tap sends no check (AT-25)", async () => {
    await renderWeek8();
    vi.useFakeTimers();
    listen("/2026/week-08/");
    const games = within(document.getElementById("matchups")!).getAllByRole("button");
    tap(games[0], TAP_GAP_MS + 1);
    expect(games[0].getAttribute("aria-expanded")).toBe("true");
    expect(idsOf("recap")).toHaveLength(1);
    expect(sent).toEqual([]);
  });

  it("sends one check for a tap combo with the trail of the two taps before the double-tap (AT-28)", async () => {
    await renderWeek8();
    vi.useFakeTimers();
    listen("/2026/week-08/");
    const [a, b] = idsOf("number");
    const c = idsOf("award")[0];
    tap(target(a), 600);
    tap(target(b), 600);
    tap(target(c));
    tap(target(c), TAP_GAP_MS + 1);
    expect(sent).toEqual([
      { page: "/2026/week-08/", target: c, action: "tap2", trail: [a, b], conditions: { theme: "light", open: ["chip-qb"] } },
    ]);
  });
});

describe("the targets of the midseason report", () => {
  async function renderReport() {
    publicOver({ report: midseasonFixture, sim: simFixture });
    const route = await import("../midseason/page");
    render(await route.default({ params: Promise.resolve({ season: "2026" }) }));
  }

  it("gives each Luck cell, Top 10 row, bench row, Look Ahead game, sim row, heading, and blurb a stable id", async () => {
    await renderReport();
    expect(idsOf("luck")).toHaveLength(12);
    expect(idsOf("top10").length).toBeGreaterThan(0);
    expect(idsOf("bench").length).toBeGreaterThanOrEqual(5);
    expect(idsOf("look-ahead").length).toBeGreaterThan(0);
    expect(idsOf("sim-row")).toHaveLength(12);
    expect(idsOf("heading").length).toBeGreaterThan(5);
    expect(idsOf("blurb").length).toBeGreaterThan(5);
    expect(ids()).toContain("luck-3");
    expectUnique(ids());
  });

  it("names the open Show all of a long list among the open states", async () => {
    await renderReport();
    vi.useFakeTimers();
    listen("/midseason/2026/");
    const showAll = screen.getAllByRole("button", { name: /^Show all/ })[0];
    tap(showAll, TAP_GAP_MS + 1);
    tap(target("luck-3"));
    tap(target("luck-3"), TAP_GAP_MS + 1);
    expect(sent).toHaveLength(1);
    expect(sent[0].conditions.open).toEqual(expect.arrayContaining([showAll.getAttribute("data-open-id")]));
  });

  it("sends one check with the hold for a hold of 3.5 seconds on the Luck cell of Lil Fridge (AT-27)", async () => {
    await renderReport();
    vi.useFakeTimers();
    listen("/midseason/2026/");
    fireEvent.pointerDown(target("luck-3"), { isPrimary: true });
    act(() => {
      vi.advanceTimersByTime(3500);
    });
    fireEvent.pointerUp(target("luck-3"), { isPrimary: true });
    // The chosen chip of the Top 10 is an open state, so the check names it.
    expect(sent).toEqual([
      { page: "/midseason/2026/", target: "luck-3", action: "hold", conditions: { theme: "light", open: ["chip-rb"] } },
    ]);
  });

  it("sends one check with the word and the id of the blurb for one selected word (AT-29)", async () => {
    await renderReport();
    vi.useFakeTimers();
    listen("/midseason/2026/");
    const blurb = target(idsOf("blurb")[0]);
    const text = blurb.firstChild!;
    const word = text.textContent!.match(/[A-Za-z]{4,}/)!;
    const range = document.createRange();
    range.setStart(text, word.index!);
    range.setEnd(text, word.index! + word[0].length);
    document.getSelection()!.removeAllRanges();
    document.getSelection()!.addRange(range);
    fireEvent(document, new Event("selectionchange"));
    act(() => {
      vi.advanceTimersByTime(SELECT_SETTLE_MS + 1);
    });
    expect(sent).toEqual([
      {
        page: "/midseason/2026/",
        target: blurb.getAttribute("data-stable-id"),
        action: "select",
        word: word[0].toLowerCase(),
        conditions: { theme: "light", open: ["chip-rb"] },
      },
    ]);
  });
});

describe("the targets of the sim replay", () => {
  it("counts 2 taps on one standings row as one double-tap while the frame of the replay changes (AT-30)", () => {
    vi.useFakeTimers();
    render(<SimReplay sim={simFixture} pick={() => 0} />);
    listen("/midseason/2026/");
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    const first = beatsOf(replaySeason(simFixture, 0))[0];
    const row = () => target(`sim-row-${replaySeason(simFixture, 0).weeks[0].standings[0].roster_id}`);
    const frame = () => screen.getByRole("status").textContent;
    act(() => {
      vi.advanceTimersByTime(first.ms - 150);
    });
    const before = frame();
    tap(row(), 200);
    // The beat ends inside the gap, so the second tap lands on the next frame.
    expect(frame()).not.toBe(before);
    tap(row(), TAP_GAP_MS + 1);
    expect(sent.map((check) => [check.target, check.action])).toEqual([[row().getAttribute("data-stable-id"), "tap2"]]);
  });
});

const MANAGERS = JSON.parse(readFileSync(join(process.cwd(), "public", "2026", "managers.json"), "utf8"));

describe("the targets of a manager page", () => {
  it("gives each result chip, odds tile, roster row, move row, and best add row a stable id", async () => {
    const manager = MANAGERS.managers.find((entry: { roster_id: number }) => entry.roster_id === 3);
    // The readers read the working folder when they load, so they load again after the temp folder of a report test.
    vi.resetModules();
    const { default: ManagerPage } = await import("../managers/manager-page");
    render(await ManagerPage({ params: Promise.resolve({ season: "2026", roster: "3" }) }));
    expect(idsOf("result")).toHaveLength(manager.weeks.length);
    expect(idsOf("odds")).toEqual(["odds-playoff", "odds-bye", "odds-seed"]);
    expect(idsOf("roster-slot")).toHaveLength(manager.grade.slots.length);
    expect(idsOf("roster-part")).toHaveLength(manager.grade.parts.length);
    expect(idsOf("best-adds")).toHaveLength(manager.best_adds.length);
    expect(idsOf("move").length).toBeGreaterThan(0);
    expectUnique(ids());
  });
});

describe("the targets of the rankings page", () => {
  it("gives the 01 of the hero, each ladder tile, and each movement row a stable id", async () => {
    vi.resetModules();
    const { default: RankingsPage } = await import("../rankings/page");
    render(<RankingsPage />);
    expect(idsOf("rank-hero")).toHaveLength(1);
    expect(idsOf("movement")).toHaveLength(11);
    expect(idsOf("ladder")).toHaveLength(11 * 4);
    expect(idsOf("hero-tile")).toHaveLength(3);
    expectUnique(ids());
  });
});

describe("the targets of the analyzer result", () => {
  it("gives the Lean word, the swap card, and each Bullet row a stable id, and puts the trade key on its root", () => {
    const doc = analyzeResponse as AnalyzeResponse;
    const { container } = render(<AnalyzeResult doc={doc} />);
    expect(ids()).toEqual(expect.arrayContaining(["verdict-word", "swap-card"]));
    const bullets = doc.sides.reduce((count, side) => count + side.bullets.length, 0);
    expect(idsOf("bullet")).toHaveLength(bullets);
    const root = container.firstElementChild!;
    const key = doc.trade.sides
      .map((side) => [side.roster_id, side.gives.map((player) => player.player_id).sort().join(",")] as const)
      .sort((a, b) => a[0] - b[0])
      .map(([roster, gives]) => `${roster}:${gives}`)
      .join("|");
    expect(root.getAttribute("data-trade-key")).toBe(key);
    // The fixture leans yes, so the answer of the egg hunt is yes.
    expect(root.getAttribute("data-trade-answer")).toBe("yes");
    expectUnique(ids());
  });

  it("sends the two teams of the trade and the answer on a double-tap of the Lean word (AT-54)", () => {
    const doc = analyzeResponse as AnalyzeResponse;
    render(<AnalyzeResult doc={doc} />);
    vi.useFakeTimers();
    listen("/analyzer/");
    tap(target("verdict-word"));
    tap(target("verdict-word"), TAP_GAP_MS + 1);
    const teams = doc.trade.sides.map((side) => side.roster_id).sort((a, b) => a - b);
    expect(sent).toEqual([
      expect.objectContaining({
        target: "verdict-word",
        action: "tap2",
        conditions: expect.objectContaining({ trade_teams: teams, trade_answer: "yes" }),
      }),
    ]);
    expect(sent[0].conditions).not.toHaveProperty("trade");
  });
});

describe("the targets of the 404 page", () => {
  it("gives the 404 hero a stable id and marks the page as the 404 page", () => {
    render(<NotFound />);
    expect(ids()).toContain("not-found-hero");
    expect(document.querySelector("[data-not-found]")).not.toBeNull();
  });
});
