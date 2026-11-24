/**
 * Tests for the front door of a build with Trades closed: no trade Topic in More, no trade chip, the closed line for a
 * typed trade question, a Tour that names no trade, and the Topic of the recent trades that stays. Each test renders the
 * page with the fixed copy of the published data of cpc, and sets the client values to the state after the Lock.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, mock } from "bun:test";
import { stubPhone } from "../../test/phone";
import { stubGlobal } from "../../test/stubs";
import { readFixtureSite } from "@/fixtures/sites";
import { clientValues } from "@/generated/client-values";
import HomePage from "./front-door/door-page";
// The jsdom stand-ins of the browser APIs that the popover and the menu sheet need.
import "@cpc/design/ui/sheet-jsdom";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. */
beforeEach(() => readFixtureSite("cpc"));
beforeEach(stubPhone);

const LINE = "The trade deadline has passed. Trades open again next season.";
const TRADE_NAMES = /Trade ideas|Trade check|Sell high or buy low/;
const fetchStub = mock();

const built = clientValues.tradesClosed;
beforeEach(() => {
  clientValues.tradesClosed = true;
  fetchStub.mockImplementation(async (url: string) =>
    String(url).endsWith("/ask")
      ? Response.json({
          route: "closed",
          line: LINE,
          topic: null,
          team: null,
          closest: [],
          suggestion: null,
          jev: { model: "jev-1.14.0", nouls: {}, choices: {} },
        })
      : new Response("", { status: 404 }),
  );
  stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", "6");
  localStorage.setItem("cpc.passphrase", "cornerstone-test");
  // Each test starts as a browser that saw the Tour, except the test of the Tour itself.
  localStorage.setItem("cpc.tour-seen", "1");
});

afterEach(() => {
  cleanup();
  clientValues.tradesClosed = built;
  localStorage.clear();
  fetchStub.mockReset();
});

async function openMore() {
  const group = await screen.findByRole("group", { name: "Suggestions" });
  fireEvent.click(within(group).getByRole("button", { name: "More" }));
  return screen.findByRole("list", { name: "All Topics" });
}

describe("the front door with Trades closed", () => {
  it("lists no trade Topic in More, and shows no trade chip (AT-6)", async () => {
    render(<HomePage />);
    const list = await openMore();
    const names = within(list)
      .getAllByRole("button")
      .map((button) => button.getAttribute("aria-label") ?? "");
    expect(names.length).toBe(11);
    expect(names.join("|")).not.toMatch(TRADE_NAMES);
    const group = screen.getByRole("group", { name: "Suggestions" });
    for (const chip of ["Trades", "Check", "Sell high"])
      expect(within(group).queryByText(chip)).toBeNull();
  });

  it("answers a typed trade question with the closed line, never the refusal, and calls no trade route (AT-7)", async () => {
    render(<HomePage />);
    const box = await screen.findByRole("form", { name: "Ask" });
    fireEvent.change(within(box).getByRole("textbox", { name: "Ask a question" }), {
      target: { value: "Who should I trade for at RB?" },
    });
    fireEvent.submit(box);
    expect(await screen.findByText(LINE)).toBeTruthy();
    expect(screen.queryByText(/I can't answer that/)).toBeNull();
    const paths = fetchStub.mock.calls.map(([url]) => String(url).split("/").pop());
    expect(paths).toContain("ask");
    expect(paths.filter((path) => path?.startsWith("trade") || path === "sell-high")).toEqual([]);
  });

  it("names no trade in the Ask Stop of the Tour (AT-9)", async () => {
    localStorage.removeItem("cpc.tour-seen");
    render(<HomePage />);
    fireEvent.click(
      within(
        await screen.findByRole("dialog", { name: "Suggestions" }, { timeout: 2000 }),
      ).getByRole("button", { name: "Next" }),
    );
    const card = await screen.findByRole("dialog", { name: "Ask" }, { timeout: 2000 });
    expect(card.textContent).not.toMatch(/trade/i);
  });

  it("keeps the Topic of the recent trades (AT-12)", async () => {
    render(<HomePage />);
    const list = await openMore();
    fireEvent.click(
      within(list).getByRole("button", { name: /^Position leaders and recent trades/ }),
    );
    const answer = await screen.findByRole("article", {
      name: "Position leaders and recent trades",
    });
    await waitFor(() => expect(answer.textContent?.length).toBeGreaterThan(50));
  });
});
