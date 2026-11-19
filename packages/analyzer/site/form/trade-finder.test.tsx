/**
 * Tests for Find mode: the hero, the optional partner, the find stream, the wait with its real steps and its teams,
 * the pick cards from the fixture finder document, and each error state. fetch is a test stub that sends a real event
 * stream, and each test reads the screen.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
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
const onAsker = vi.fn();

function answer(status: number, body: unknown = {}, headers: Record<string, string> = {}) {
  fetchStub.mockResolvedValueOnce(new Response(JSON.stringify(body), { status, headers }));
}

/* One part of the find stream as a `data:` line. */
const line = (part: unknown) => new TextEncoder().encode(`data: ${JSON.stringify(part)}\n\n`);
const step = (text: string, live: boolean) => ({ type: "data-step", data: { line: text, live } });
const team = (rosterId: number) => ({ type: "data-team", data: { roster_id: rosterId } });
const done = (doc: unknown) => ({ type: "data-answer", data: { kind: "find", document: doc } });

/* A find stream that the test feeds part by part, so a test can read the wait between two parts. */
function heldStream() {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const body = new ReadableStream<Uint8Array>({ start: (c) => void (controller = c) });
  fetchStub.mockResolvedValueOnce(new Response(body, { headers: { "content-type": "text/event-stream" } }));
  return {
    send: async (...parts: unknown[]) => {
      await act(async () => {
        for (const part of parts) controller.enqueue(line(part));
        // The reader takes each chunk on a later turn, so the test waits for the reads to land.
        await new Promise((resolve) => setTimeout(resolve, 0));
      });
    },
    end: () => controller.close(),
  };
}

/* The five steps of a find with every team, as the find stream sends them, then the document. */
function streamOf(doc: unknown) {
  const parts = [
    step("Reading every team", true),
    team(1),
    step("Read 11 teams", false),
    step("Looking for players who fit", true),
    step("Found 18 players who fit", false),
    step("Building offers", true),
    step("Built 42 offers", false),
    step("Making a shortlist", true),
    step("Made a shortlist of 9", false),
    step("Picking the best 3", true),
    step("Picked the best 3", false),
    done(doc),
  ];
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const part of parts) controller.enqueue(line(part));
      controller.close();
    },
  });
  fetchStub.mockResolvedValueOnce(new Response(body, { headers: { "content-type": "text/event-stream" } }));
}

/* The text of the line on the screen in the stage lines part: the last line, because an outgoing line stays a moment. */
function stageLine(): string {
  const texts = document.querySelectorAll(".t-think-text");
  return texts[texts.length - 1]?.textContent ?? "";
}

/* The roster ids of the avatars of the wait that are lit, in the order of the row. */
function litTeams(): number[] {
  return [...document.querySelectorAll<HTMLElement>("[data-team-read]")].filter((el) => el.dataset.lit === "true").map((el) => Number(el.dataset.teamRead));
}

const partnerButton = () => screen.getByRole("button", { name: /Trade with/ });
const findButton = () => screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement;
const cards = () => screen.queryAllByRole("article");

/* Opens the partner sheet and returns its rows: Every team, then the other teams. */
async function partnerRows() {
  fireEvent.click(partnerButton());
  return within(await screen.findByRole("list", { name: "Partners" })).getAllByRole("button");
}

/* Picks a row of the partner sheet by its name, and waits for the sheet to close. */
async function pickPartner(name: RegExp) {
  const rows = await partnerRows();
  fireEvent.click(rows.find((row) => name.test(row.textContent ?? "")) as HTMLElement);
  await waitFor(() => expect(screen.queryByRole("list", { name: "Partners" })).toBeNull());
}

/* Picks a partner and taps "Find a Trade". */
async function findWithPartner() {
  await pickPartner(/Lil Fridge/);
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
  onAsker.mockReset();
  vi.stubGlobal("fetch", fetchStub);
  render(
    <TradeFinder
      teams={TEAMS}
      target={apiTarget}
      asker={2}
      onAsker={onAsker}
      passphrase="localtest"
      onUnauthorized={onUnauthorized}
      onRostersStale={onRostersStale}
      onOpen={onOpen}
    />,
  );
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("TradeFinder", () => {
  it("shows the wait in the stage lines, one real step at a time, each line held until the next step", async () => {
    const stream = heldStream();
    find();
    await stream.send(step("Reading every team", true));
    expect(stageLine()).toBe("1 of 5 · Reading every team");
    // The done line of a step does not move the line, so the line holds until the next step starts.
    await stream.send(step("Read 11 teams", false));
    expect(stageLine()).toBe("1 of 5 · Reading every team");
    await stream.send(step("Looking for players who fit", true));
    expect(stageLine()).toBe("2 of 5 · Looking for players who fit");
    await stream.send(step("Found 18 players who fit", false), step("Building offers", true), step("Built 42 offers", false), step("Making a shortlist", true));
    expect(stageLine()).toBe("4 of 5 · Making a shortlist");
    // A screen reader hears the step in the one status of the wait, and no line names a chart.
    expect(screen.getByRole("status").textContent).toBe("4 of 5 · Making a shortlist");
    expect(screen.queryByText(/chart/i)).toBeNull();
  });

  it("shows the wait in the hero of the grade wait, with the same title level and the mesh", async () => {
    heldStream();
    find();
    const hero = (await screen.findByRole("region", { name: "Finding Trades" })) as HTMLElement;
    expect(within(hero).getByRole("heading", { level: 2, name: "Finding Trades" })).toBeTruthy();
    expect(within(hero).getByText("This can take about 25 seconds.")).toBeTruthy();
    expect(hero.querySelector('[aria-busy="true"]')).toBeTruthy();
    // The stage lines part is the same part as the grade wait.
    expect(hero.querySelector(".t-think")).toBeTruthy();
  });

  it("lights the avatar of each team as the stream reports it read, in the order of the stream", async () => {
    const stream = heldStream();
    find();
    await stream.send(step("Reading every team", true));
    // The wait shows the eleven partners, none lit before the first read.
    expect(document.querySelectorAll("[data-team-read]")).toHaveLength(11);
    expect(litTeams()).toEqual([]);
    await stream.send(team(7));
    expect(litTeams()).toEqual([7]);
    await stream.send(team(3), team(12));
    expect(litTeams().sort((a, b) => a - b)).toEqual([3, 7, 12]);
  });

  it("shows only the picked partner in the wait", async () => {
    const stream = heldStream();
    await findWithPartner();
    await stream.send(step("Reading their roster", true), team(3));
    expect([...document.querySelectorAll<HTMLElement>("[data-team-read]")].map((el) => el.dataset.teamRead)).toEqual(["3"]);
    expect(litTeams()).toEqual([3]);
  });

  it("tells the form that a search runs, and that it ended", async () => {
    const onFindingChange = vi.fn();
    cleanup();
    const stream = heldStream();
    render(
      <TradeFinder teams={TEAMS} target={apiTarget} asker={2} onAsker={onAsker} passphrase="localtest" onUnauthorized={onUnauthorized} onOpen={onOpen} onFindingChange={onFindingChange} />,
    );
    find();
    await waitFor(() => expect(onFindingChange).toHaveBeenLastCalledWith(true));
    await stream.send(done(fixture));
    await waitFor(() => expect(onFindingChange).toHaveBeenLastCalledWith(false));
  });

  it("lists Every team first, then the eleven other teams and not the asker", async () => {
    const rows = await partnerRows();
    expect(rows).toHaveLength(12);
    expect(rows[0].textContent).toContain("Every team");
    expect(rows.some((row) => row.textContent?.includes("All You Need Is Love"))).toBe(false);
  });

  it("keeps the find button on with no partner picked", async () => {
    expect(findButton().disabled).toBe(false);
    await pickPartner(/Lil Fridge/);
    expect(findButton().disabled).toBe(false);
  });

  it("posts the season and the asker with no partner to the find stream with the passphrase", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toBe("https://api.example.test/clients/cpc/find-stream");
    expect(init.method).toBe("POST");
    expect(init.headers["X-League-Passphrase"]).toBe("localtest");
    expect(JSON.parse(init.body)).toEqual({ season: 2026, asker: 2 });
  });

  it("posts the picked partner, and Every team clears it", async () => {
    streamOf(fixture);
    await findWithPartner();
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(JSON.parse(fetchStub.mock.calls[0][1].body)).toEqual({ season: 2026, asker: 2, partner: 3 });
    await pickPartner(/Every team/);
    expect(cards()).toHaveLength(0);
    expect(partnerButton().textContent).toContain("Every team");
    streamOf(fixture);
    fireEvent.click(findButton());
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(JSON.parse(fetchStub.mock.calls[1][1].body)).toEqual({ season: 2026, asker: 2 });
  });

  it("lands up to three cards in one list under the hero, each led by its Lean, with the Case and no headline", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const list = screen.getByRole("list", { name: "Trade ideas" });
    expect(within(list).getAllByRole("article")).toHaveLength(3);
    cards().forEach((card, i) => {
      const trade = fixture.trades[i];
      expect(within(card).getByRole("heading", { level: 3 }).textContent).toBe(trade.lean);
      expect(within(card).getByText(trade.case!)).toBeTruthy();
      for (const side of trade.sides) for (const player of side.gives) expect(card.textContent).toContain(player.name);
    });
  });

  it("clamps the Case of a card to 3 lines", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const text = within(cards()[0]).getByText(fixture.trades[0].case!);
    expect(text.classList.contains("line-clamp-3")).toBe(true);
  });

  it("folds the Bullets of a card under one button, and a tap opens the rows with their Marks", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    const card = cards()[0];
    const trade = fixture.trades[0];
    const fold = within(card).getByRole("button", { name: `Why it works · ${trade.bullets.length}` });
    expect(fold.getAttribute("aria-expanded")).toBe("false");
    expect(within(card).queryByRole("button", { name: new RegExp(trade.bullets[0].text) })).toBeNull();
    fireEvent.click(fold);
    expect(fold.getAttribute("aria-expanded")).toBe("true");
    const panel = document.getElementById(fold.getAttribute("aria-controls")!) as HTMLElement;
    expect(panel.hasAttribute("hidden")).toBe(false);
    const rows = within(panel).getAllByRole("button", { expanded: false });
    expect(rows).toHaveLength(trade.bullets.length);
    trade.bullets.forEach((bullet, n) => {
      expect(rows[n].textContent).toContain(bullet.text);
      // The glyph is decorative, so a screen reader hears the Mark as a word.
      expect(rows[n].textContent).toContain(bullet.mark);
    });
  });

  it("opens the fact of a Bullet row on a tap", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    fireEvent.click(within(cards()[0]).getByRole("button", { name: /Why it works/ }));
    const bullet = fixture.trades[0].bullets[0];
    const row = within(cards()[0]).getByRole("button", { name: new RegExp(bullet.text) });
    fireEvent.click(row);
    expect(row.getAttribute("aria-expanded")).toBe("true");
    const fact = document.getElementById(row.getAttribute("aria-controls")!) as HTMLElement;
    expect(fact.textContent).toBe(bullet.fact_text);
  });

  it("shows no letter grade on any card", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    for (const card of cards()) expect(card.textContent).not.toMatch(LETTER);
  });

  it("shows Find in one hero with its title, the line, Your team, the partner, the chips, and the button", async () => {
    const hero = screen.getAllByRole("region", { name: "Trade Ideas" }).at(-1) as HTMLElement;
    expect(within(hero).getByRole("heading", { level: 1, name: "Trade Ideas" })).toBeTruthy();
    expect(within(hero).getByText("Who has a trade for you?")).toBeTruthy();
    expect(within(hero).getByRole("button", { name: /Your team/ }).textContent).toContain("All You Need Is Love");
    expect(within(hero).getByRole("button", { name: /Trade with/ }).textContent).toContain("Every team");
    expect(within(hero).getByRole("radiogroup", { name: "Position" })).toBeTruthy();
    expect(within(hero).getByRole("button", { name: "Find a Trade" })).toBeTruthy();
    await pickPartner(/Lil Fridge/);
    expect(within(hero).getByRole("button", { name: /Trade with/ }).textContent).toContain("Lil Fridge");
  });

  it("hands a pick of Your team to the form", async () => {
    fireEvent.click(screen.getByRole("button", { name: /Your team/ }));
    const rows = within(await screen.findByRole("list", { name: "Teams" })).getAllByRole("button");
    fireEvent.click(rows.find((row) => row.textContent?.includes("Lil Fridge")) as HTMLElement);
    expect(onAsker).toHaveBeenCalledWith(3);
  });

  it("names each result card by its place, with See the Full Result", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(cards().map((card) => card.getAttribute("aria-label"))).toEqual(["Trade 1 of 3", "Trade 2 of 3", "Trade 3 of 3"]);
    expect(within(cards()[0]).getByRole("button", { name: "See the Full Result" })).toBeTruthy();
  });

  it("opens the trade of a card with the document of the find, so the form shows its read", async () => {
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    cards().forEach((card, i) => {
      fireEvent.click(within(card).getByRole("button", { name: "See the Full Result" }));
      expect(onOpen).toHaveBeenLastCalledWith(fixture.trades[i], expect.objectContaining({ season: fixture.season, trades: fixture.trades }));
    });
  });

  it("shows the fact lines of each shortlist offer after a fallback, with no Lean and no row", async () => {
    const lines = ["Tre Tucker (WR, LV) scored 11.1 points per game over 6 games before the trade.", "Second line."];
    const trades = fixture.trades.map((t) => ({ ...t, lean: null, case: null, bullets: [], fact_lines: lines }));
    streamOf({ ...fixture, fallback: true, trades });
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(screen.getByText("The picks did not come through. These are the trades the search kept, with their facts.")).toBeTruthy();
    cards().forEach((card, i) => {
      expect(card.textContent).not.toContain(fixture.trades[i].lean);
      expect(within(card).queryByRole("button", { name: /Why it works/ })).toBeNull();
      const facts = within(card).getByRole("list", { name: "Facts" });
      expect(within(facts).getAllByRole("listitem").map((item) => item.textContent)).toEqual(lines);
      expect(within(card).getByRole("button", { name: "See the Full Result" })).toBeTruthy();
    });
  });

  it("shows the empty line when no trade works", async () => {
    streamOf({ ...fixture, trades: [], empty: EMPTY_LINE });
    find();
    expect(await screen.findByText(EMPTY_LINE)).toBeTruthy();
    expect(cards()).toHaveLength(0);
  });

  it("shows the as-of line as on the analyze result", async () => {
    streamOf(fixture);
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

  it("shows the error line and Try Again in the hero when the find route answers 500", async () => {
    answer(500);
    find();
    const hero = screen.getAllByRole("region", { name: "Trade Ideas" }).at(-1) as HTMLElement;
    expect(await within(hero).findByText("The API did not answer. Try again.")).toBeTruthy();
    expect(within(hero).getByRole("button", { name: "Try Again" })).toBeTruthy();
    expect(within(hero).queryByRole("button", { name: "Find a Trade" })).toBeNull();
  });

  it("shows the line of an error part of the stream, and Try Again runs the find again", async () => {
    const stream = heldStream();
    find();
    await stream.send(step("Reading every team", true), { type: "data-error", data: { status: 503, line: "The search failed. Try again." } });
    expect(await screen.findByText("The search failed. Try again.")).toBeTruthy();
    streamOf(fixture);
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(fetchStub).toHaveBeenCalledTimes(2);
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
