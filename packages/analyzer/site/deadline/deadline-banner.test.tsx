/**
 * Tests of the Deadline banner: its text in each phase, its tick, its one button, and the Trade Wire sheet it opens.
 * The clock and the answer of the Trade Wire route are fixed test inputs: the real Lock of CPC, and the real route answer
 * of leg 9 of CPC, which holds trade W. Each expected text comes from the spec.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
// The jsdom stand-ins that the Drawer of the sheet needs.
import "@cpc/design/ui/sheet-jsdom";
import type { ApiTarget } from "../lib/api";
import { DeadlineBanner } from "./deadline-banner";
import WEEK_9 from "./fixtures/trade-wire-cpc-week-9.json";

const LOCK = Date.parse("2026-11-24T00:00:00-05:00");
const TARGET: ApiTarget = { url: "https://api.example.test", client: "cpc", season: 2026 };
const GRADE = "/analyze/?mode=grade";
const FIND = "/analyze/?mode=find";
// Trade W, in which roster 4 sends $5 of FAAB to roster 8, and the other trade of leg 9.
const TRADE_W = "1424578776058155008";
const OTHER = "1425209111854747648";
const EMPTY = { leg: 11, trades: [] };
const onlyOther = { leg: 9, trades: WEEK_9.trades.filter((trade) => trade.transaction_id === OTHER) };

/* The answer that the route gives now. A test changes it to show a new trade or a failed read. */
let answer: { status: number; body: unknown };
let fetchStub: ReturnType<typeof vi.fn>;
let hidden = false;

beforeEach(() => {
  answer = { status: 200, body: EMPTY };
  hidden = false;
  fetchStub = vi.fn(async () => new Response(JSON.stringify(answer.body), { status: answer.status }));
  vi.stubGlobal("fetch", fetchStub);
  Object.defineProperty(document, "visibilityState", { configurable: true, get: () => (hidden ? "hidden" : "visible") });
  localStorage.setItem("cpc.passphrase", "league-word");
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
  localStorage.clear();
});

/* Lets the answer of each call that went out reach the page. */
async function settle() {
  await act(async () => {
    await Promise.resolve();
  });
  await act(async () => {
    await Promise.resolve();
  });
}

/* The banner at the time `iso`, after its first tick and its first read of the Trade Wire. */
async function bannerAt(iso: string, findHref: string | null = FIND) {
  vi.useFakeTimers({ toFake: ["Date", "setInterval", "clearInterval", "setTimeout", "clearTimeout"] });
  vi.setSystemTime(new Date(iso));
  const view = render(<DeadlineBanner lock={LOCK} api={TARGET} gradeHref={GRADE} findHref={findHref} />);
  act(() => vi.advanceTimersByTime(0));
  await settle();
  return view;
}

/* Moves the clock on `ms`, and lets each read that went out answer. */
async function wait(ms: number) {
  act(() => vi.advanceTimersByTime(ms));
  await settle();
}

function setHidden(value: boolean) {
  hidden = value;
  act(() => {
    document.dispatchEvent(new Event("visibilitychange"));
  });
}

const sheet = () => screen.getByRole("dialog", { name: "Trade Wire" });
const rows = () => within(sheet()).queryAllByRole("listitem");

const trigger = () => screen.getByRole("button", { name: /^Open the Trade Wire/ });

describe("the Deadline banner", () => {
  it("is one button that shows the trade deadline over the countdown (AT-1)", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00");
    expect(screen.getByRole("button", { name: "Open the Trade Wire, 0 new trades" })).toBeTruthy();
    expect(trigger().textContent).toContain("Trade deadline");
    expect(trigger().textContent).toContain("~2d 14h 05m");
    expect(trigger().closest("[data-deadline-banner]")?.getAttribute("data-phase")).toBe("open");
  });

  it("ticks one minute on when the clock moves on 60 s (AT-2)", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00");
    await wait(60_000);
    expect(trigger().textContent).toContain("~2d 14h 04m");
  });

  it("shows the seconds in the last hours (AT-3)", async () => {
    await bannerAt("2026-11-23T21:18:50-05:00");
    expect(trigger().textContent).toContain("~2h 41m 10s");
    expect(trigger().closest("[data-deadline-banner]")?.getAttribute("data-phase")).toBe("last-hours");
  });

  it("says the trade deadline has passed, with the badge Final, after the Lock (AT-9)", async () => {
    await bannerAt("2026-11-24T00:00:01-05:00");
    const button = screen.getByRole("button", { name: "Open the Trade Wire, final. The trade deadline has passed." });
    expect(button.textContent).toContain("The trade deadline has passed. Good luck in the playoffs.");
    expect(button.textContent).toContain("Final");
    expect(button.textContent).not.toContain("Trade deadline~");
  });

  it("goes away one day after the Lock (AT-10)", async () => {
    await bannerAt("2026-11-25T00:00:01-05:00");
    expect(screen.queryByRole("button")).toBeNull();
    expect(document.querySelector("[data-deadline-banner]")).toBeNull();
  });

  it("opens the shared sheet with the eyebrow, the title Trade Wire, and the empty line", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    const sheet = screen.getByRole("dialog", { name: "Trade Wire" });
    expect(within(sheet).getByText("Trade deadline ~2d 14h 05m")).toBeTruthy();
    expect(within(sheet).getByText("No trades yet this week.")).toBeTruthy();
  });

  it("shows the closed empty line in the sheet after the Lock", async () => {
    await bannerAt("2026-11-24T00:00:01-05:00");
    fireEvent.click(trigger());
    const sheet = screen.getByRole("dialog", { name: "Trade Wire" });
    expect(within(sheet).getByText("No trades this week.")).toBeTruthy();
  });

  it("never says Lock or that rosters are locked", async () => {
    for (const iso of ["2026-11-21T09:55:00-05:00", "2026-11-23T21:18:50-05:00", "2026-11-24T00:00:01-05:00"]) {
      answer = { status: 200, body: WEEK_9 };
      const view = await bannerAt(iso);
      fireEvent.click(trigger());
      expect(document.body.textContent).not.toMatch(/\block/i);
      view.unmount();
      vi.useRealTimers();
    }
  });
});

describe("the Trade Wire", () => {
  it("reads the Trade Wire route of the client with the passphrase", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00");
    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toBe("https://api.example.test/clients/cpc/deadline/trades");
    expect((init as RequestInit).headers).toMatchObject({ "X-League-Passphrase": "league-word" });
  });

  it("sends no call with no passphrase, and shows the note of a failed read", async () => {
    localStorage.clear();
    await bannerAt("2026-11-21T09:55:00-05:00");
    await wait(10_000);
    expect(fetchStub).not.toHaveBeenCalled();
    fireEvent.click(trigger());
    expect(within(sheet()).getByText("The last update failed.")).toBeTruthy();
  });

  it("names the button and the badge from the count of the route (AT-5, AT-6)", async () => {
    answer = { status: 200, body: WEEK_9 };
    await bannerAt("2026-11-21T09:55:00-05:00");
    expect(screen.getByRole("button", { name: "Open the Trade Wire, 2 new trades" })).toBeTruthy();
    expect(trigger().textContent).toContain("2 new");
  });

  it("shows no badge when the week has no trade (AT-6)", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00");
    expect(trigger().textContent).not.toMatch(/new/);
  });

  it("holds the links, the eyebrow, the title, the live line, and the trades, in that order (AT-18)", async () => {
    answer = { status: 200, body: WEEK_9 };
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    const text = sheet().textContent ?? "";
    const order = ["Grade a trade", "Find a trade", "Trade deadline ~2d 14h 05m", "Trade Wire", "Updated 0s ago", "NFC Least"];
    const places = order.map((part) => text.indexOf(part));
    expect(places.every((place) => place >= 0)).toBe(true);
    expect([...places].sort((a, b) => a - b)).toEqual(places);
    expect(within(sheet()).getByRole("link", { name: "Grade a trade" }).getAttribute("href")).toBe(GRADE);
    expect(within(sheet()).getByRole("link", { name: "Find a trade" }).getAttribute("href")).toBe(FIND);
  });

  it("shows each trade with its time, each team, the players it gets with positions, and the FAAB (AT-13, AT-19)", async () => {
    answer = { status: 200, body: WEEK_9 };
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    const [newest, tradeW] = rows();
    expect(newest.textContent).toContain("Puka Deez...");
    expect(tradeW.textContent).toContain("Fri 7:04 PM");
    expect(tradeW.textContent).toContain("NFC Least gets");
    expect(tradeW.textContent).toContain("Tetairoa McMillan WR, Makai Lemon WR, Seth McGowan RB, Chase Brown RB");
    expect(tradeW.textContent).toContain("Return of T Mac gets");
    expect(tradeW.textContent).toContain("Rome Odunze WR, CeeDee Lamb WR, Jordan Mason RB");
    expect(tradeW.textContent).toContain("$5 FAAB");
    expect(tradeW.textContent?.match(/FAAB/g)).toHaveLength(1);
    expect(tradeW.querySelectorAll("img")).toHaveLength(2);
  });

  it("puts a new trade at the top within 15 s, and the badge counts it (AT-20)", async () => {
    answer = { status: 200, body: onlyOther };
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    expect(trigger().textContent).toContain("1 new");
    expect(rows()).toHaveLength(1);
    answer = { status: 200, body: { leg: 9, trades: [...WEEK_9.trades].reverse() } };
    await wait(10_000);
    expect(rows()).toHaveLength(2);
    expect(rows()[0].getAttribute("data-trade")).toBe(TRADE_W);
    expect(trigger().textContent).toContain("2 new");
    expect(screen.getByRole("button", { name: "Open the Trade Wire, 2 new trades" })).toBeTruthy();
  });

  it("slides a new trade in from above with a short blur, and leaves the rows on screen still (AT-20)", async () => {
    answer = { status: 200, body: onlyOther };
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    expect(rows()[0].getAttribute("style") ?? "").not.toMatch(/opacity: 0/);
    answer = { status: 200, body: WEEK_9 };
    await wait(10_000);
    expect(rows().find((row) => row.getAttribute("data-trade") === OTHER)?.getAttribute("style") ?? "").not.toMatch(/opacity: 0/);
    const arrived = rows().find((row) => row.getAttribute("data-trade") === TRADE_W);
    expect(arrived?.getAttribute("style")).toMatch(/opacity: 0/);
    expect(arrived?.getAttribute("style")).toMatch(/translateY\(-[\d.]+px\)|blur\([\d.]+px\)/);
  });

  it("says when it last updated, and the seconds tick (AT-21)", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    expect(sheet().textContent).toContain("Updated 0s ago");
    await wait(3000);
    expect(sheet().textContent).toContain("Updated 3s ago");
  });

  it("polls each 10 s, sends no call while the tab hides, and calls at once when it shows (AT-22)", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00");
    expect(fetchStub).toHaveBeenCalledTimes(1);
    await wait(10_000);
    expect(fetchStub).toHaveBeenCalledTimes(2);
    setHidden(true);
    await wait(30_000);
    expect(fetchStub).toHaveBeenCalledTimes(2);
    setHidden(false);
    await settle();
    expect(fetchStub).toHaveBeenCalledTimes(3);
    await wait(10_000);
    expect(fetchStub).toHaveBeenCalledTimes(4);
  });

  it("stops the poll at the Lock (AT-22)", async () => {
    await bannerAt("2026-11-23T23:59:45-05:00");
    // One poll before the trade deadline, then one last read at it for the final list.
    await wait(10_000);
    await wait(5_000);
    expect(fetchStub).toHaveBeenCalledTimes(3);
    const calls = fetchStub.mock.calls.length;
    await wait(60_000);
    expect(fetchStub).toHaveBeenCalledTimes(calls);
    expect(trigger().textContent).toContain("Final");
  });

  it("keeps the list and shows a short note when a read fails (AT-25)", async () => {
    answer = { status: 200, body: WEEK_9 };
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    answer = { status: 500, body: { detail: "down" } };
    await wait(10_000);
    expect(rows()).toHaveLength(2);
    expect(within(sheet()).getByText("The last update failed.")).toBeTruthy();
    answer = { status: 200, body: WEEK_9 };
    await wait(10_000);
    expect(within(sheet()).queryByText("The last update failed.")).toBeNull();
  });

  it("shows no Find a trade while the finder flag is off (AT-27)", async () => {
    await bannerAt("2026-11-21T09:55:00-05:00", null);
    fireEvent.click(trigger());
    expect(within(sheet()).getByRole("link", { name: "Grade a trade" })).toBeTruthy();
    expect(within(sheet()).queryByRole("link", { name: "Find a trade" })).toBeNull();
  });

  it("hides both trade links after the Lock, and keeps the final list (AT-29)", async () => {
    answer = { status: 200, body: WEEK_9 };
    await bannerAt("2026-11-24T00:00:01-05:00");
    fireEvent.click(trigger());
    expect(within(sheet()).queryByRole("link")).toBeNull();
    expect(rows()).toHaveLength(2);
  });

  it("links to no Deadline Board (AT-52)", async () => {
    answer = { status: 200, body: WEEK_9 };
    await bannerAt("2026-11-21T09:55:00-05:00");
    fireEvent.click(trigger());
    const hrefs = within(sheet()).getAllByRole("link").map((link) => link.getAttribute("href"));
    expect(hrefs).toEqual([GRADE, FIND]);
    expect(document.body.textContent).not.toMatch(/board/i);
  });
});
