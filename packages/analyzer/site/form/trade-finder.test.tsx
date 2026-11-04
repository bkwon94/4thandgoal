/**
 * Tests for the trade finder: the partner picker, the find post, the cards from the fixture finder document, and each error state.
 * fetch is a test stub, and each test reads the screen.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiTarget, findResponse as fixtureJson } from "../lib/fixtures/api";
import type { FindResponse } from "../lib/analyze-types";
import type { Team } from "../lib/api";
import { TradeFinder } from "./trade-finder";

const fixture = fixtureJson as FindResponse;
const EMPTY_LINE = "No swap between these rosters is good for both.";

/* Twelve teams, as in the league. The fixture asker is roster 2 and the fixture partner is roster 3. */
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

/* Picks the fixture partner and taps "Find a Trade". */
function find() {
  fireEvent.click(within(picker()).getByRole("radio", { name: /Lil Fridge/ }));
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
  it("lists the eleven other teams and not the asker", () => {
    const radios = within(picker()).getAllByRole("radio");
    expect(radios).toHaveLength(11);
    expect(within(picker()).queryByRole("radio", { name: /All You Need Is Love/ })).toBeNull();
  });

  it("keeps the find button off until a partner is picked", () => {
    expect(findButton().disabled).toBe(true);
    fireEvent.click(within(picker()).getByRole("radio", { name: /Lil Fridge/ }));
    expect(findButton().disabled).toBe(false);
  });

  it("posts the season, the asker, and the partner to the find route with the passphrase", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toBe("https://api.example.test/clients/cpc/find");
    expect(init.method).toBe("POST");
    expect(init.headers["X-League-Passphrase"]).toBe("localtest");
    expect(JSON.parse(init.body)).toEqual({ season: 2026, asker: 2, partner: 3 });
  });

  it("renders three cards with the two sides, the fairness line, and the reason", async () => {
    answer(200, fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const first = cards()[0];
    expect(first.textContent).toContain("Jameis Winston");
    expect(first.textContent).toContain("Tre Tucker");
    expect(first.textContent).toContain("Wan'Dale Robinson");
    expect(first.textContent).toContain("Good for both");
    expect(first.textContent).toContain(fixture.trades[0].reason);
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

  it("shows the fairness line alone when the reason is null", async () => {
    const reasons = fixture.trades.map((t) => t.reason!);
    answer(200, { ...fixture, fallback: true, trades: fixture.trades.map((t) => ({ ...t, reason: null })) });
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    cards().forEach((card, i) => {
      expect(card.textContent).toContain("Good for both");
      expect(card.textContent).not.toContain(reasons[i]);
    });
  });

  it("shows the empty line when no swap is good for both", async () => {
    answer(200, { ...fixture, trades: [], empty: EMPTY_LINE });
    find();
    expect(await screen.findByText(EMPTY_LINE)).toBeTruthy();
    expect(cards()).toHaveLength(0);
  });

  it("shows the as-of line as on the analyze result", async () => {
    answer(200, fixture);
    find();
    expect(await screen.findByText(/Stats through week 5 · Chart week 6 · rosters fetched/)).toBeTruthy();
  });

  it("shows the wait line on a 429", async () => {
    answer(429, { detail: "slow down" }, { "Retry-After": "12" });
    find();
    expect(await screen.findByText("Too many requests. Try again in 12 seconds.")).toBeTruthy();
  });

  it("shows the API message on a 422", async () => {
    answer(422, { detail: { message: "Pick two different teams." } });
    find();
    expect(await screen.findByText("Pick two different teams.")).toBeTruthy();
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
