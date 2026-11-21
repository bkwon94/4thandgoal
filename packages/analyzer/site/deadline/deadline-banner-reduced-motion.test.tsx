/**
 * The Trade Wire under reduced motion: a new trade shows at rest at once, with no slide and no blur.
 * Framer Motion reads the media query once per test file, so this file asks for reduced motion before the first render.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, mock, setSystemTime, spyOn } from "bun:test";
import "@cpc/design/ui/sheet-jsdom";
import { fakeClock } from "../lib/fake-clock";
import { DeadlineBanner } from "./deadline-banner";
import WEEK_9 from "./fixtures/trade-wire-cpc-week-9.json";

const LOCK = Date.parse("2026-11-24T00:00:00-05:00");
const TRADE_W = "1424578776058155008";
const OTHER = "1425209111854747648";

let body: unknown = {
  leg: 9,
  trades: WEEK_9.trades.filter((trade) => trade.transaction_id === OTHER),
};

/* The reader asks the system for reduced motion. The stand-in answers each query of reduced motion with a match. */
window.matchMedia = (query: string) =>
  ({
    matches: query.includes("prefers-reduced-motion"),
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }) as unknown as MediaQueryList;

beforeEach(() => {
  spyOn(globalThis, "fetch").mockImplementation(
    (async () => new Response(JSON.stringify(body))) as unknown as typeof fetch,
  );
  localStorage.setItem("cpc.passphrase", "league-word");
});

/* The fake clock of the test, so the countdown and the reads of the Trade Wire move only when the test moves them. */
let clock: ReturnType<typeof fakeClock> | null = null;

afterEach(() => {
  cleanup();
  clock = null;
  setSystemTime();
  localStorage.clear();
});

async function settle() {
  for (let i = 0; i < 2; i += 1) {
    await act(async () => {
      await Promise.resolve();
    });
  }
}

describe("the Trade Wire under reduced motion", () => {
  it("shows a new trade at rest at once, with no slide (AT-20)", async () => {
    clock = fakeClock();
    clock.setTime(new Date("2026-11-21T09:55:00-05:00"));
    render(
      <DeadlineBanner
        lock={LOCK}
        api={{ url: "https://api.example.test", client: "cpc", season: 2026 }}
        gradeHref="/analyze/?mode=grade"
        findHref={null}
      />,
    );
    act(() => clock!.advance(0));
    await settle();
    fireEvent.click(screen.getByRole("button", { name: /^Open the Trade Wire/ }));
    body = WEEK_9;
    act(() => clock!.advance(10_000));
    await settle();
    const sheet = screen.getByRole("dialog", { name: "Trade Wire" });
    const arrived = within(sheet)
      .getAllByRole("listitem")
      .find((row) => row.getAttribute("data-trade") === TRADE_W);
    expect(arrived).toBeTruthy();
    const style = arrived?.getAttribute("style") ?? "";
    expect(style).not.toMatch(/opacity: 0/);
    expect(style).not.toMatch(/translateY\(-8px\)/);
    expect(style).not.toMatch(/blur\(2px\)/);
  });
});
