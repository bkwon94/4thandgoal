/**
 * Tests for the trade finder: the optional partner, the find post, the pick cards from the fixture finder document, and each error state.
 * fetch is a test stub, and each test reads the screen.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiTarget, findResponse as fixtureJson } from "../lib/fixtures/api";
import type { FindResponse } from "../lib/analyze-types";
import type { Team } from "../lib/api";
import { TradeFinder } from "./trade-finder";

const fixture = fixtureJson as FindResponse;
const EMPTY_LINE = "The search found no trade that works for both teams.";
// A letter grade, such as B or C+, as a word of its own.
const LETTER = /(?:^|\s)[A-F][+-]?(?=[\s.,]|$)/;

/* Twelve teams, as in the league. The fixture asker is roster 2, and the fixture find has no partner. */
const TEAMS: Team[] = Array.from({ length: 12 }, (_, i) => ({
  roster_id: i + 1,
  team: i === 1 ? "All You Need Is Love" : i === 2 ? "Lil Fridge" : `Team ${i + 1}`,
  manager: `Manager ${i + 1}`,
  avatar: null,
  players: [],
}));

const fetchStub = vi.fn();
const onUnauthorized = vi.fn();
const onOpen = vi.fn();
const onRostersStale = vi.fn();

function answer(status: number, body: unknown = {}, headers: Record<string, string> = {}) {
  fetchStub.mockResolvedValueOnce(new Response(JSON.stringify(body), { status, headers }));
}

const picker = () => screen.getByRole("group", { name: "Trade Partner" });
const findButton = () => screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement;
const cards = () => screen.queryAllByRole("article");

/* Picks a partner and taps "Find a Trade". */
function findWithPartner() {
  fireEvent.click(within(picker()).getByRole("radio", { name: /Lil Fridge/ }));
  fireEvent.click(findButton());
}

/* Taps "Find a Trade" with no partner, as the fixture find does. */
function find() {
  fireEvent.click(findButton());
}

beforeEach(() => {
  fetchStub.mockReset();
  onUnauthorized.mockReset();
  onOpen.mockReset();
  onRostersStale.mockReset();
  vi.stubGlobal("fetch", fetchStub);
  render(<TradeFinder teams={TEAMS} target={apiTarget} asker={2} passphrase="localtest" onUnauthorized={onUnauthorized} onRostersStale={onRostersStale} onOpen={onOpen} />);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("TradeFinder", () => {
  it("shows the wait text while the search runs, with no chart named", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    find();
    expect(await screen.findByText("The search tries every small swap. This can take up to a minute.")).toBeTruthy();
    expect(screen.queryByText(/chart/i)).toBeNull();
  });

  it("shows the sweep and Finding… while the search runs", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    find();
    expect(await screen.findByRole("button", { name: "Finding…" })).toBeTruthy();
    // The sweep sits with the status line. The track is aria-hidden, so the query includes hidden elements.
    const wait = screen.getByRole("status").parentElement as HTMLElement;
    expect(within(wait).getByRole("presentation", { hidden: true })).toBeTruthy();
  });

  it("lists the eleven other teams and not the asker", () => {
    const radios = within(picker()).getAllByRole("radio");
    expect(radios).toHaveLength(11);
    expect(within(picker()).queryByRole("radio", { name: /All You Need Is Love/ })).toBeNull();
  });

  it("keeps the find button on with no partner picked", () => {
    expect(findButton().disabled).toBe(false);
    fireEvent.click(within(picker()).getByRole("radio", { name: /Lil Fridge/ }));
    expect(findButton().disabled).toBe(false);
  });

  it("posts the season and the asker with no partner to the find route with the passphrase", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toBe("https://api.example.test/clients/cpc/find");
    expect(init.method).toBe("POST");
    expect(init.headers["X-League-Passphrase"]).toBe("localtest");
    expect(JSON.parse(init.body)).toEqual({ season: 2026, asker: 2 });
  });

  it("posts the picked partner, and Search Every Team clears it", async () => {
    answer(200, fixture);
    findWithPartner();
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(JSON.parse(fetchStub.mock.calls[0][1].body)).toEqual({ season: 2026, asker: 2, partner: 3 });
    fireEvent.click(screen.getByRole("button", { name: "Search Every Team" }));
    expect(cards()).toHaveLength(0);
    answer(200, fixture);
    fireEvent.click(findButton());
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(JSON.parse(fetchStub.mock.calls[1][1].body)).toEqual({ season: 2026, asker: 2 });
  });

  it("renders three cards with the headline, the two sides, and the Bullet rows with their Marks", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    cards().forEach((card, i) => {
      const trade = fixture.trades[i];
      expect(within(card).getByText(trade.headline!)).toBeTruthy();
      for (const side of trade.sides) for (const player of side.gives) expect(card.textContent).toContain(player.name);
      const rows = within(card).getAllByRole("button", { expanded: false });
      expect(rows).toHaveLength(trade.bullets.length);
      trade.bullets.forEach((bullet, n) => {
        expect(rows[n].textContent).toContain(bullet.text);
        // The glyph is decorative, so a screen reader hears the Mark as a word.
        expect(rows[n].textContent).toContain(bullet.mark);
      });
    });
  });

  it("opens the fact of a Bullet row on a tap", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const bullet = fixture.trades[0].bullets[0];
    const row = within(cards()[0]).getByRole("button", { name: new RegExp(bullet.text) });
    fireEvent.click(row);
    expect(row.getAttribute("aria-expanded")).toBe("true");
    const fact = document.getElementById(row.getAttribute("aria-controls")!) as HTMLElement;
    expect(fact.textContent).toBe(bullet.fact_text);
  });

  it("shows no letter grade on any card", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    for (const card of cards()) expect(card.textContent).not.toMatch(LETTER);
  });

  it("shows the finder as one card with its title, the copy, the partner row, and the button", async () => {
    const finder = screen.getByRole("region", { name: "Find a Trade" });
    expect(within(finder).getByText("Pick a partner, or search every team. The search finds up to 3 trades.")).toBeTruthy();
    expect(within(finder).getByRole("group", { name: "Trade Partner" })).toBeTruthy();
    expect(within(finder).getByRole("button", { name: "Find a Trade" })).toBeTruthy();
    fireEvent.click(within(picker()).getByRole("radio", { name: /Lil Fridge/ }));
    // A pick folds the list to the partner row with Change.
    // The other rows animate out, so the test waits for them to leave.
    await waitFor(() => expect(within(picker()).getAllByRole("radio")).toHaveLength(1));
    expect(within(finder).getByRole("button", { name: "Change trade partner" })).toBeTruthy();
  });

  it("names each result card by its place, with See the Full Result", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(cards().map((card) => within(card).getByRole("heading", { level: 3 }).textContent)).toEqual([
      "Trade 1 of 3",
      "Trade 2 of 3",
      "Trade 3 of 3",
    ]);
    expect(within(cards()[0]).getByRole("button", { name: "See the Full Result" })).toBeTruthy();
  });

  it("opens the full result of the trade on a card", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    cards().forEach((card, i) => {
      fireEvent.click(within(card).getByRole("button", { name: "See the Full Result" }));
      expect(onOpen).toHaveBeenLastCalledWith(fixture.trades[i], fixture.season);
    });
  });

  it("shows the fact lines of each shortlist offer after a fallback, with no headline and no row", async () => {
    const lines = ["Tre Tucker (WR, LV) scored 11.1 points per game over 6 games before the trade.", "Second line."];
    const trades = fixture.trades.map((t) => ({ ...t, headline: null, bullets: [], fact_lines: lines }));
    answer(200, { ...fixture, fallback: true, trades });
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(screen.getByText("The picks did not come through. These are the trades the search kept, with their facts.")).toBeTruthy();
    cards().forEach((card, i) => {
      expect(card.textContent).not.toContain(fixture.trades[i].headline);
      expect(within(card).queryAllByRole("button", { expanded: false })).toHaveLength(0);
      const facts = within(card).getByRole("list", { name: "Facts" });
      expect(within(facts).getAllByRole("listitem").map((item) => item.textContent)).toEqual(lines);
      expect(within(card).getByRole("button", { name: "See the Full Result" })).toBeTruthy();
    });
  });

  it("shows the empty line when no trade works", async () => {
    answer(200, { ...fixture, trades: [], empty: EMPTY_LINE });
    find();
    expect(await screen.findByText(EMPTY_LINE)).toBeTruthy();
    expect(cards()).toHaveLength(0);
  });

  it("shows the as-of line as on the analyze result", async () => {
    answer(200, fixture);
    find();
    // The fixture find ran with 14 known games of week 6, so the line names them as on the analyze result.
    const asOf = await screen.findByText(/^Stats through/);
    expect(asOf.textContent).toMatch(/^Stats through week 5, plus 14 week 6 games · Usage pending for 8 games · rosters fetched /);
  });

  it("shows the wait line on a 429", async () => {
    answer(429, { detail: "slow down" }, { "Retry-After": "12" });
    find();
    expect(await screen.findByText("Too many requests. Try again in 12 seconds.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try Again" })).toBeTruthy();
  });

  it("shows the API message on a 422", async () => {
    answer(422, { detail: { message: "Pick two different teams." } });
    find();
    expect(await screen.findByText("Pick two different teams.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try Again" })).toBeTruthy();
    // The rosters are stale, so the page fetches the current ones.
    expect(onRostersStale).toHaveBeenCalledTimes(1);
  });

  it("shows the same down line as the trade form on a 503 with no detail", async () => {
    answer(503);
    find();
    expect(await screen.findByText("The analyzer is down for the moment. Try again in a few minutes.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try Again" })).toBeTruthy();
    expect(onRostersStale).not.toHaveBeenCalled();
  });

  it("asks for the passphrase again on a 401", async () => {
    answer(401, { detail: "bad passphrase" });
    find();
    await waitFor(() => expect(onUnauthorized).toHaveBeenCalledTimes(1));
  });
});
