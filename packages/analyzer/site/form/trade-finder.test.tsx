/**
 * Tests for Find mode: the hero, the optional partner, the find stream, the wait with its real steps and its teams,
 * the pick cards from the fixture finder document, and each error state. fetch is a test stub that sends a real event
 * stream, and each test reads the screen.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { apiTarget, findResponse as fixtureJson } from "../lib/fixtures/api";
import type { FindResponse, FinderTrade, NearIdea } from "../lib/analyze-types";
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

/* The players of the fixture by name, and one more player of the asker, so a test can build a 3-for-2. */
type Player = FinderTrade["sides"][number]["gives"][number];
const PLAYERS: Record<string, Player> = Object.fromEntries(
  [...fixture.trades, ...fixture.near].flatMap((trade) => trade.sides.flatMap((side) => side.gives)).map(({ to: _to, ...player }) => [player.name, player]),
);
PLAYERS["Kenneth Walker III"] = { player_id: "8151", name: "Kenneth Walker III", position: "RB", nfl_team: "SEA", headshot: "https://sleepercdn.com/content/nfl/players/8151.jpg", season_rank: "RB8", recent_rank: null };
const ASKER = fixture.trade_pair.asker;
const PARTNER = { roster_id: 10, team: "behold the lamb" };

/* One offer of the asker with roster 10, in the shape of the find answer: the sides in order and the trade value total
   of each side, the chart sum of the players that the side gives. */
function offerOf(give: string[], get: string[], [giveValue, getValue]: [number | null, number | null]) {
  const gives = give.map((name) => PLAYERS[name]);
  const gets = get.map((name) => PLAYERS[name]);
  return {
    offer_id: `2:${gives.map((p) => p.player_id).join("+")}-10:${gets.map((p) => p.player_id).join("+")}`,
    sides: [
      { ...ASKER, gives: gives.map((p) => ({ ...p, to: 10 })), gets: gets.map((p) => ({ ...p, from: 10 })) },
      { ...PARTNER, gives: gets.map((p) => ({ ...p, to: 2 })), gets: gives.map((p) => ({ ...p, from: 2 })) },
    ],
    totals: [
      { roster_id: 2, trade_value: giveValue },
      { roster_id: 10, trade_value: getValue },
    ],
  };
}

/* A pick of the find answer with the read of the first fixture trade. */
function pickOf(give: string[], get: string[], totals: [number | null, number | null]): FinderTrade {
  const { lean, case: text, bullets, fact_lines } = fixture.trades[0];
  return { ...offerOf(give, get, totals), lean, case: text, bullets, fact_lines };
}

function nearOf(give: string[], get: string[], reason: string): NearIdea {
  return { ...offerOf(give, get, [30, 28]), reason };
}

/* A find answer of 5 picks, a 1-for-1, a 2-for-1, a 3-for-2, and two more, and 3 near ideas. */
const ONE_FOR_ONE = pickOf(["Tre Tucker"], ["Emeka Egbuka"], [24.5, 22.0]);
const TWO_FOR_ONE = pickOf(["Tre Tucker", "Colston Loveland"], ["Emeka Egbuka"], [26.5, 25.0]);
const THREE_FOR_TWO = pickOf(["Kenneth Walker III", "Tre Tucker", "Colston Loveland"], ["Emeka Egbuka", "Roschon Johnson"], [62.5, 68.0]);
const FIVE: FindResponse = {
  ...fixture,
  trades: [
    ONE_FOR_ONE,
    TWO_FOR_ONE,
    THREE_FOR_TWO,
    pickOf(["Colston Loveland"], ["Germie Bernard"], [10.0, 10.2]),
    pickOf(["Kenneth Walker III"], ["Emeka Egbuka"], [40.0, 30.0]),
  ],
  near: [
    nearOf(["Tre Tucker"], ["Germie Bernard"], "The other lineup gets worse."),
    nearOf(["Colston Loveland"], ["Roschon Johnson"], "Your lineup gets no better."),
    nearOf(["Kenneth Walker III", "Tre Tucker"], ["Emeka Egbuka"], "You give much more than you get."),
  ],
};

/* One part of the find stream as a `data:` line. */
const line = (part: unknown) => new TextEncoder().encode(`data: ${JSON.stringify(part)}\n\n`);
const step = (text: string, live: boolean) => ({ type: "data-step", data: { line: text, live } });
const team = (rosterId: number) => ({ type: "data-team", data: { roster_id: rosterId } });
const done = (doc: unknown) => ({ type: "data-answer", data: { kind: "find", document: doc } });
const trade = (index: number, most: number, item: unknown) => ({ type: "data-trade", data: { index, most, trade: item } });
/* The part that says the pick has no more trades. */
const tradesDone = { type: "data-trades-done", data: {} };
/* The Shortlist part: each trade by its players, the full name and the short name of each, from the side of the asker. */
const named = (name: string, last: string) => ({ name, last });
const shortlist = (...trades: { gives: { name: string; last: string }[]; gets: { name: string; last: string }[] }[]) => ({
  type: "data-shortlist",
  data: { trades: trades.map((item, i) => ({ offer_id: `offer-${i}`, ...item })) },
});
/* Three Shortlist trades: two short ones that fit one line by full names, and one long one that needs last names. */
const SHORT_A = { gives: [named("Tre Tucker", "Tucker")], gets: [named("Emeka Egbuka", "Egbuka")] };
const SHORT_B = { gives: [named("Zay Flowers", "Flowers")], gets: [named("Tony Pollard", "Pollard")] };
const LONG = {
  gives: [named("Kenneth Walker III", "Walker")],
  gets: [named("Trey Lawrence", "Lawrence"), named("Tony Pollard", "Pollard"), named("Rondale Moore", "Moore")],
};

/* The fixed clock of a wait test: the timers of the page move only when the test moves them. The stream reads land on
   setImmediate, which the clock leaves real, so a part still reaches the page. */
function fixedClock() {
  vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "setInterval", "clearInterval", "Date"] });
}
/* Steps 1 to 4 of a find, each live line with its done line, then the time for each line to show. */
async function firstFourSteps(stream: ReturnType<typeof heldStream>) {
  await stream.send(step("Reading 11 teams", true), step("Read 11 teams", false), step("Matching trade value", true), step("Matched 4,667 trades by trade value", false), step("Checking 4,667 trades for fairness", true), step("Checked 4,667 trades for fairness", false), step("Checking 77 against both lineups", true), step("Made a shortlist of 9", false));
  await tick(6000);
}
/* React starts the timer of a new line only after the act of the line before it ends, so the clock moves 1 ms per act,
   and each timer starts at the time it would start in a browser. */
async function tick(ms: number) {
  for (let left = ms; left > 0; left -= 1) {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1);
    });
  }
}

/* A find stream that the test feeds part by part, so a test can read the wait between two parts. */
function heldStream() {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const body = new ReadableStream<Uint8Array>({ start: (c) => void (controller = c) });
  fetchStub.mockResolvedValueOnce(new Response(body, { headers: { "content-type": "text/event-stream" } }));
  return {
    send: async (...parts: unknown[]) => {
      await act(async () => {
        for (const part of parts) controller.enqueue(line(part));
        // The reader takes each chunk on a later turn, so the test waits for the reads to land. setImmediate is never
        // on the fixed clock of a wait test, so the wait works with the clock fixed or free.
        await new Promise((resolve) => setImmediate(resolve));
        await new Promise((resolve) => setImmediate(resolve));
      });
    },
    end: () => controller.close(),
  };
}

/* The five steps of a find with every team, as the find stream sends them, then the document. */
function streamOf(doc: unknown) {
  const parts = [
    step("Reading 11 teams", true),
    team(1),
    step("Read 11 teams", false),
    step("Matching trade value", true),
    step("Matched 4,667 trades by trade value", false),
    step("Checking 4,667 trades for fairness", true),
    step("Checked 4,667 trades for fairness", false),
    step("Checking 77 against both lineups", true),
    step("Made a shortlist of 9", false),
    step("Picking the best 5", true),
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
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("TradeFinder", () => {
  it("shows the wait in the stage lines, one real step at a time, each line held until the next step", async () => {
    fixedClock();
    const stream = heldStream();
    find();
    await stream.send(step("Reading 11 teams", true));
    expect(stageLine()).toBe("1 of 5 · Reading 11 teams");
    // The done line of a step does not move the line, so the line holds until the next step starts.
    await stream.send(step("Read 11 teams", false));
    await tick(5000);
    expect(stageLine()).toBe("1 of 5 · Reading 11 teams");
    await stream.send(step("Matching trade value", true));
    expect(stageLine()).toBe("2 of 5 · Matching trade value");
    await stream.send(step("Matched 4,667 trades by trade value", false), step("Checking 4,667 trades for fairness", true), step("Checked 4,667 trades for fairness", false), step("Checking 77 against both lineups", true));
    await tick(3000);
    expect(stageLine()).toBe("4 of 5 · Checking 77 against both lineups");
    // A screen reader hears the step in the one status of the wait, and no line names a chart.
    expect(screen.getByRole("status").textContent).toBe("4 of 5 · Checking 77 against both lineups");
    expect(screen.queryByText(/chart/i)).toBeNull();
  });

  it("holds each step line at least 1.5 s, even when the steps end faster", async () => {
    // AT-36 and decision 20: the stream can end three steps in the same moment, and each line still stays readable.
    fixedClock();
    const stream = heldStream();
    find();
    await stream.send(step("Reading 11 teams", true), step("Read 11 teams", false), step("Matching trade value", true), step("Matched 4,667 trades by trade value", false), step("Checking 4,667 trades for fairness", true), step("Checked 4,667 trades for fairness", false), step("Checking 77 against both lineups", true));
    expect(stageLine()).toBe("1 of 5 · Reading 11 teams");
    await tick(1499);
    expect(stageLine()).toBe("1 of 5 · Reading 11 teams");
    await tick(1);
    expect(stageLine()).toBe("2 of 5 · Matching trade value");
    await tick(1499);
    expect(stageLine()).toBe("2 of 5 · Matching trade value");
    await tick(1);
    expect(stageLine()).toBe("3 of 5 · Checking 4,667 trades for fairness");
    await tick(1500);
    expect(stageLine()).toBe("4 of 5 · Checking 77 against both lineups");
    // The last line has nothing queued behind it, so it holds until the next step starts.
    await tick(10_000);
    expect(stageLine()).toBe("4 of 5 · Checking 77 against both lineups");
    // A step that starts after the hold of the line on screen shows at once.
    await stream.send(step("Made a shortlist of 9", false), step("Picking the best 5", true));
    expect(stageLine()).toBe("5 of 5 · Picking the best 5");
  });

  it("names one Shortlist trade at a time on step 5, each held about 3 s, and loops", async () => {
    // AT-73 and decision 20: the line changes about every 3 s, and each line names a Shortlist trade by its players.
    fixedClock();
    const stream = heldStream();
    find();
    await firstFourSteps(stream);
    await stream.send(shortlist(SHORT_A, LONG, SHORT_B), step("Picking the best 5", true));
    expect(stageLine()).toBe("5 of 5 · Picking the best 5");
    await tick(2999);
    expect(stageLine()).toBe("5 of 5 · Picking the best 5");
    await tick(1);
    // A line that fits one phone line keeps the full names.
    expect(stageLine()).toBe("Weighing Tre Tucker for Emeka Egbuka");
    await tick(2999);
    expect(stageLine()).toBe("Weighing Tre Tucker for Emeka Egbuka");
    await tick(1);
    // A line too long for a phone takes the last names, so it never runs past one line.
    expect(stageLine()).toBe("Weighing Walker for Lawrence, Pollard, Moore");
    await tick(3000);
    expect(stageLine()).toBe("Weighing Zay Flowers for Tony Pollard");
    // The pick still runs after the last trade, so the lines start again at the first.
    await tick(3000);
    expect(stageLine()).toBe("Weighing Tre Tucker for Emeka Egbuka");
    // A screen reader hears the same line, and no line names an inner tool, states a time, or says rival.
    expect(screen.getByRole("status").textContent).toBe("Weighing Tre Tucker for Emeka Egbuka");
    const hero = screen.getByRole("region", { name: "Finding Trades" });
    expect(hero.textContent).not.toMatch(/\b(?:jev|advisor|finder|front door|lock|rival|brian)\b/i);
    expect(hero.textContent).not.toMatch(/\b(?:seconds?|minutes?)\b/i);
  });

  it("stops the step 5 lines when the first card shows", async () => {
    fixedClock();
    const stream = heldStream();
    find();
    await firstFourSteps(stream);
    await stream.send(shortlist(SHORT_A, SHORT_B), step("Picking the best 5", true));
    await tick(3000);
    expect(stageLine()).toBe("Weighing Tre Tucker for Emeka Egbuka");
    await stream.send(trade(0, 5, FIVE.trades[0]));
    // The card is the answer now, so the wait line goes back to the step and holds there.
    expect(stageLine()).toBe("5 of 5 · Picking the best 5");
    await tick(12_000);
    expect(stageLine()).toBe("5 of 5 · Picking the best 5");
  });

  it("keeps the step 5 line when the stream sends no Shortlist", async () => {
    fixedClock();
    const stream = heldStream();
    find();
    await firstFourSteps(stream);
    await stream.send(step("Picking the best 5", true));
    await tick(12_000);
    expect(stageLine()).toBe("5 of 5 · Picking the best 5");
  });

  it("shows the wait in the hero of the grade wait, with the same title level and the mesh", async () => {
    heldStream();
    find();
    const hero = (await screen.findByRole("region", { name: "Finding Trades" })) as HTMLElement;
    expect(within(hero).getByRole("heading", { level: 2, name: "Finding Trades" })).toBeTruthy();
    // The wait makes no promise of how long it takes, so no line counts seconds or minutes (AT-68).
    expect(hero.textContent).not.toMatch(/This can take/);
    expect(hero.textContent).not.toMatch(/\d+\s*(?:s|sec|secs|seconds?|min|mins|minutes?)\b/i);
    expect(hero.textContent).not.toMatch(/\b(?:seconds?|minutes?)\b/i);
    expect(hero.querySelector('[aria-busy="true"]')).toBeTruthy();
    // The stage lines part is the same part as the grade wait.
    expect(hero.querySelector(".t-think")).toBeTruthy();
  });

  it("lights the avatar of each team as the stream reports it read, in the order of the stream", async () => {
    const stream = heldStream();
    find();
    await stream.send(step("Reading 11 teams", true));
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

  it("lands the cards in one list under the hero, each led by its Lean, with the Case and no headline", async () => {
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

  it("shows each trade as a Ledger: You get and You give columns, a row per player with the rank, and a total under each", async () => {
    streamOf(FIVE);
    find();
    await waitFor(() => expect(cards()).toHaveLength(5));
    const [one, two, three] = cards();
    const column = (card: HTMLElement, name: RegExp) => within(card).getByRole("list", { name });
    // The 1-for-1, the 2-for-1, and the 3-for-2 each name the count of each column.
    expect(within(one).getByText("You get · 1")).toBeTruthy();
    expect(within(one).getByText("You give · 1")).toBeTruthy();
    expect(within(two).getByText("You get · 1")).toBeTruthy();
    expect(within(two).getByText("You give · 2")).toBeTruthy();
    expect(within(three).getByText("You get · 2")).toBeTruthy();
    expect(within(three).getByText("You give · 3")).toBeTruthy();
    // Each row shows the name, then the position, the NFL team, and the rank.
    const gets = within(column(three, /You get/)).getAllByRole("listitem");
    expect(gets.map((row) => row.textContent)).toEqual(["Emeka EgbukaWR · TB · WR24", "Roschon JohnsonRB · CHI · RB50"]);
    const gives = within(column(three, /You give/)).getAllByRole("listitem");
    expect(gives.map((row) => row.textContent)).toEqual(["Kenneth Walker IIIRB · SEA · RB8", "Tre TuckerWR · LV · WR16", "Colston LovelandTE · CHI · TE26"]);
    // No row shows a trade value. The total of each column sits under it.
    for (const row of [...gets, ...gives]) expect(row.textContent).not.toMatch(/\d+\.\d/);
    expect(within(three).getByText("68.0").closest("[data-total]")?.textContent).toBe("Trade value 68.0");
    expect(within(three).getByText("62.5").closest("[data-total]")?.textContent).toBe("Trade value 62.5");
  });

  it("states the gap of the two totals in one plain line under them", async () => {
    streamOf(FIVE);
    find();
    await waitFor(() => expect(cards()).toHaveLength(5));
    const gap = (card: HTMLElement) => card.querySelector("[data-gap]")?.textContent;
    // 68.0 for You get and 62.5 for You give (AT-66).
    expect(gap(cards()[2])).toBe("You get 9% more trade value");
    // 22.0 back for 24.5 given: the asker gives 11% more.
    expect(gap(cards()[0])).toBe("You give 11% more trade value");
    // 10.2 back for 10.0 given is within a few percent.
    expect(gap(cards()[3])).toBe("Even in trade value");
    expect(gap(cards()[4])).toBe("You give 33% more trade value");
  });

  it("shows no total and no gap line when the week has no chart", async () => {
    streamOf({ ...fixture, trades: [pickOf(["Tre Tucker"], ["Emeka Egbuka"], [null, null])], near: [] });
    find();
    await waitFor(() => expect(cards()).toHaveLength(1));
    expect(cards()[0].querySelector("[data-total]")).toBeNull();
    expect(cards()[0].querySelector("[data-gap]")).toBeNull();
    expect(cards()[0].textContent).toContain("You get · 1");
  });

  it("shows no gap line when a side has no trade value", async () => {
    // The first fixture trade gets Roschon Johnson, who has no chart value, so the get total is 0.0.
    streamOf(fixture);
    find();
    await waitFor(() => expect(cards()).toHaveLength(3));
    expect(cards()[0].querySelector("[data-gap]")).toBeNull();
    expect(cards()[1].querySelector("[data-gap]")?.textContent).toBe("You give 56% more trade value");
  });

  it("shows each card as its trade part comes, and the count line counts the trades still to come down to none", async () => {
    // AT-72 and decision 20: the first card shows long before the last.
    const stream = heldStream();
    find();
    await stream.send(step("Picking the best 5", true));
    expect(cards()).toHaveLength(0);
    expect(screen.queryByText(/^Writing \d+ more trade/)).toBeNull();
    await stream.send(trade(0, 5, FIVE.trades[0]));
    expect(cards()).toHaveLength(1);
    expect(within(cards()[0]).getByText(FIVE.trades[0].lean as string)).toBeTruthy();
    expect(screen.getByText("Writing 4 more trades")).toBeTruthy();
    // The wait stays on screen while the cards come, and the near fold waits for the end.
    expect(screen.getByRole("region", { name: "Finding Trades" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: /^Close, but not sent/ })).toBeNull();
    // A card of the stream has no document of the find yet, so its button waits for the end.
    expect((within(cards()[0]).getByRole("button", { name: "See the Full Result" }) as HTMLButtonElement).disabled).toBe(true);
    await stream.send(trade(1, 5, FIVE.trades[1]), trade(2, 5, FIVE.trades[2]));
    expect(cards()).toHaveLength(3);
    expect(screen.getByText("Writing 2 more trades")).toBeTruthy();
    await stream.send(trade(3, 5, FIVE.trades[3]));
    expect(screen.getByText("Writing 1 more trade")).toBeTruthy();
    await stream.send(trade(4, 5, FIVE.trades[4]));
    expect(cards()).toHaveLength(5);
    expect(screen.queryAllByText(/^Writing \d+ more trade/)).toHaveLength(0);
    // The cards keep the order of the stream.
    expect(cards().map((card) => card.getAttribute("aria-label"))).toEqual([1, 2, 3, 4, 5].map((n) => `Trade ${n} of 5`));
    await stream.send(step("Picked the best 5", false), done(FIVE));
    stream.end();
    await screen.findByRole("button", { name: /^Close, but not sent/ });
    expect(cards()).toHaveLength(5);
    expect((within(cards()[0]).getByRole("button", { name: "See the Full Result" }) as HTMLButtonElement).disabled).toBe(false);
  });

  it("shows the cards of the answer when it keeps fewer trades than the stream counted", async () => {
    // The pick can keep 3 of 5, so the answer ends the count line, and the answer is the truth.
    const stream = heldStream();
    find();
    await stream.send(trade(0, 5, FIVE.trades[0]), trade(1, 5, FIVE.trades[1]), trade(2, 5, FIVE.trades[2]));
    expect(screen.getByText("Writing 2 more trades")).toBeTruthy();
    await stream.send(done({ ...FIVE, trades: FIVE.trades.slice(0, 3) }));
    stream.end();
    await screen.findByRole("button", { name: /^Close, but not sent/ });
    expect(cards()).toHaveLength(3);
    expect(screen.queryAllByText(/^Writing \d+ more trade/)).toHaveLength(0);
  });

  it("drops the count line as soon as the stream says the pick has no more trades, before the answer", async () => {
    // Ticket 17: the count line counts the trades still to come until the last card shows. The pick kept 3 of 5.
    const stream = heldStream();
    find();
    await stream.send(trade(0, 5, FIVE.trades[0]), trade(1, 5, FIVE.trades[1]), trade(2, 5, FIVE.trades[2]));
    expect(screen.getByText("Writing 2 more trades")).toBeTruthy();
    await stream.send(tradesDone);
    expect(screen.queryAllByText(/^Writing \d+ more trade/)).toHaveLength(0);
    expect(cards().map((card) => card.getAttribute("aria-label"))).toEqual(["Trade 1 of 3", "Trade 2 of 3", "Trade 3 of 3"]);
    // The answer has not come, so the wait stays on screen.
    expect(screen.getByRole("region", { name: "Finding Trades" })).toBeTruthy();
    await stream.send(done({ ...FIVE, trades: FIVE.trades.slice(0, 3) }));
    stream.end();
    await screen.findByRole("button", { name: /^Close, but not sent/ });
    expect(cards()).toHaveLength(3);
  });

  it("shows up to 5 cards, then the near ideas folded under Close, but not sent", async () => {
    streamOf(FIVE);
    find();
    await waitFor(() => expect(cards()).toHaveLength(5));
    expect(cards().map((card) => card.getAttribute("aria-label"))).toEqual(["Trade 1 of 5", "Trade 2 of 5", "Trade 3 of 5", "Trade 4 of 5", "Trade 5 of 5"]);
    const fold = screen.getByRole("button", { name: "Close, but not sent · 3" });
    expect(fold.getAttribute("aria-expanded")).toBe("false");
    // The closed fold shows no idea.
    expect(screen.queryByText(FIVE.near[0].reason)).toBeNull();
    fireEvent.click(fold);
    expect(fold.getAttribute("aria-expanded")).toBe("true");
    const panel = document.getElementById(fold.getAttribute("aria-controls")!) as HTMLElement;
    expect(panel.hasAttribute("hidden")).toBe(false);
    const ideas = within(panel).getAllByRole("listitem");
    expect(ideas).toHaveLength(3);
    FIVE.near.forEach((idea, i) => {
      expect(ideas[i].textContent).toContain(idea.reason);
      for (const side of idea.sides) for (const player of side.gives) expect(ideas[i].textContent).toContain(player.name);
    });
    // The fold sits after the last card.
    expect(cards()[4].compareDocumentPosition(fold) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("keeps at most 5 picks and 3 near ideas", async () => {
    const extra = pickOf(["Tre Tucker"], ["Roschon Johnson"], [20, 21]);
    const more = nearOf(["Tre Tucker"], ["Roschon Johnson"], "One more reason.");
    streamOf({ ...FIVE, trades: [...FIVE.trades, extra], near: [...FIVE.near, more] });
    find();
    await waitFor(() => expect(cards()).toHaveLength(5));
    expect(screen.getByRole("button", { name: "Close, but not sent · 3" })).toBeTruthy();
  });

  it("shows no near fold when the answer has no near idea", async () => {
    streamOf({ ...FIVE, near: [] });
    find();
    await waitFor(() => expect(cards()).toHaveLength(5));
    expect(screen.queryByRole("button", { name: /Close, but not sent/ })).toBeNull();
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
    await stream.send(step("Reading 11 teams", true), { type: "data-error", data: { status: 503, line: "The search failed. Try again." } });
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
