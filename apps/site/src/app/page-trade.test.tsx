/**
 * Tests for the trade Topics of the front door at /: the trade check, trade ideas, and sell high. Each test renders the
 * page with the fixed copy of the published data of cpc. fetch is a test stub that sends the streams of real live runs of the API.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import checkStream from "./front-door/fixtures/trade-check-stream.json";
import formStream from "./front-door/fixtures/trade-form-stream.json";
import ideasStream from "./front-door/fixtures/trade-ideas-stream.json";
import sellStream from "./front-door/fixtures/sell-high-stream.json";
import HomePage from "./front-door/door-page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const PASSPHRASE = "cornerstone-test";
const SURE = "is Courtland Sutton for Kenneth Walker fair";
const VAGUE = "is my RB for their WR fair";
const fetchStub = vi.fn();
/* The answer of each route of the API by the end of its path, in the order of the calls. */
const replies: Record<string, Response[]> = { "/ask": [], "/trade-check": [], "/trade-ideas": [], "/sell-high": [] };

const callsTo = (path: string) => fetchStub.mock.calls.filter(([url]) => String(url).endsWith(path));

/* The route of the ask box to a trade Topic, as the API sends it. */
function routeTo(topic: string, team: number | null = null) {
  replies["/ask"].push(Response.json({ route: "topic", topic, team, closest: [], suggestion: null, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } }));
}

const sse = (parts: unknown[]) => parts.map((part) => `data: ${JSON.stringify(part)}\n\n`).join("") + "data: [DONE]\n\n";

function streamOf(path: string, parts: unknown[]) {
  replies[path].push(new Response(sse(parts), { headers: { "Content-Type": "text/event-stream" } }));
}

/* A stream that the test feeds part by part, so it can read the Thread between two parts. */
function heldStream(path: string) {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const body = new ReadableStream<Uint8Array>({ start: (c) => void (controller = c) });
  replies[path].push(new Response(body, { headers: { "Content-Type": "text/event-stream" } }));
  const encoder = new TextEncoder();
  return {
    send: async (part: unknown) => act(async () => controller.enqueue(encoder.encode(`data: ${JSON.stringify(part)}\n\n`))),
    end: async () => act(async () => controller.close()),
  };
}

async function ask(question: string) {
  const box = await screen.findByRole("form", { name: "Ask" });
  fireEvent.change(within(box).getByRole("textbox", { name: "Ask a question" }), { target: { value: question } });
  fireEvent.submit(box);
}

async function openTopic(name: string) {
  const more = within(await screen.findByRole("group", { name: "Suggestions" })).getByRole("button", { name: "More" });
  fireEvent.click(more);
  fireEvent.click(within(await screen.findByRole("list", { name: "All Topics" })).getByRole("button", { name: new RegExp(`^${name}`) }));
}

beforeEach(() => {
  fetchStub.mockImplementation(async (url: string) => {
    const path = Object.keys(replies).find((end) => String(url).endsWith(end));
    return path ? (replies[path].shift() ?? new Response("", { status: 500 })) : new Response("", { status: 404 });
  });
  vi.stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", "3");
  localStorage.setItem("cpc.passphrase", PASSPHRASE);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  fetchStub.mockReset();
  for (const list of Object.values(replies)) list.length = 0;
  vi.unstubAllGlobals();
});

describe("the trade check of Lil Fridge", () => {
  it("sends the typed trade on to the trade check with Your team and the passphrase", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", checkStream);
    render(<HomePage />);
    await ask(SURE);
    await waitFor(() => expect(callsTo("/trade-check")).toHaveLength(1));
    const [url, init] = callsTo("/trade-check")[0];
    expect(url).toMatch(/\/clients\/cpc\/trade-check$/);
    expect(init.headers["X-League-Passphrase"]).toBe(PASSPHRASE);
    expect(JSON.parse(init.body)).toEqual({ question: SURE, roster_id: 3 });
  });

  it("shows the Lean, the Case, the top Bullets, and a Trade page link with the trade (AT-24)", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", checkStream);
    render(<HomePage />);
    await ask(SURE);
    const check = await screen.findByRole("region", { name: "Trade check" });
    expect(check.textContent).toContain("You give Courtland Sutton and get Kenneth Walker III from Bo Girds.");
    const scale = within(check).getByRole("list", { name: "The Lean scale" });
    expect(within(scale).getAllByRole("listitem").find((step) => step.getAttribute("aria-current") === "step")?.textContent).toBe("Send it");
    expect(check.textContent).toContain("If Bo Girds will say yes, send this right away");
    const bullets = check.querySelectorAll("[data-bullet-text]");
    expect(bullets).toHaveLength(3);
    expect(bullets[0].textContent).toContain("22.9 points per game");
    const link = within(check).getByRole("link", { name: "Open it on the Trade page" });
    expect(link.getAttribute("href")).toBe("/analyze/?team=3&with=6&give=5045&get=8151");
  });

  it("leads the Case with the reason for the Lean, and the fairness line agrees with it (AT-25)", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", checkStream);
    render(<HomePage />);
    await ask(SURE);
    const check = await screen.findByRole("region", { name: "Trade check" });
    // Send it with "because you turn a slumping WR into the RB2", and Bo Girds gives more, so it helps Lil Fridge.
    expect(check.textContent).toMatch(/send this right away, because you turn a slumping WR into the RB2 on the season\./);
    expect(check.textContent).toContain("It helps Lil Fridge more.");
  });

  it("opens the Trade page and fills no unsure player for a trade with no named player (AT-58)", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", formStream);
    render(<HomePage />);
    await ask(VAGUE);
    const card = await screen.findByRole("region", { name: "Trade check" });
    expect(card.textContent).toContain("Name the players");
    expect(within(card).getByRole("link", { name: "Open the Trade page" }).getAttribute("href")).toBe("/analyze/?team=3");
  });

  it("opens the Trade page with Your team for a tap on the trade check Topic, with no call", async () => {
    render(<HomePage />);
    await openTopic("Trade check");
    const card = await screen.findByRole("region", { name: "Trade check" });
    expect(within(card).getByRole("link", { name: "Open the Trade page" }).getAttribute("href")).toBe("/analyze/?team=3");
    expect(callsTo("/trade-check")).toHaveLength(0);
  });

  it("shows the line of a failed press and no Answer", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", [{ type: "start" }, { type: "data-error", data: { status: 503, line: "The question did not go through. Ask again." } }]);
    render(<HomePage />);
    await ask(SURE);
    await waitFor(() => expect(screen.getByRole("article", { name: SURE }).textContent).toContain("Ask again"));
    expect(screen.queryByRole("region", { name: "Trade check" })).toBeNull();
  });
});

describe("the trade ideas of Lil Fridge", () => {
  it("shows the real offers of the find press for the weak spots of Lil Fridge (AT-26)", async () => {
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await openTopic("Trade ideas");
    const ideas = await screen.findByRole("region", { name: "Trade ideas" });
    expect(JSON.parse(callsTo("/trade-ideas")[0][1].body)).toEqual({ roster_id: 3, partner: null });
    const offers = within(ideas).getAllByRole("link", { name: "Check this trade" });
    expect(offers).toHaveLength(2);
    expect(ideas.textContent).toContain("You give Derrick Henry and get Tee Higgins.");
    expect(ideas.textContent).toContain("With Teehee");
    // Each offer leads with its headline and shows its top 2 Bullets. The Trade page holds the rest.
    expect(ideas.textContent).toContain("St. Brown is WR8 at 15.6 points per game");
    expect(ideas.querySelectorAll("[data-bullet-text]")).toHaveLength(4);
  });

  it("sends a typed question of trade ideas with the team it names as the partner", async () => {
    routeTo("trade_ideas", 6);
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await ask("any trades with Bo Girds");
    await waitFor(() => expect(callsTo("/trade-ideas")).toHaveLength(1));
    expect(JSON.parse(callsTo("/trade-ideas")[0][1].body)).toEqual({ roster_id: 3, partner: 6, question: "any trades with Bo Girds", turns: [] });
  });

  it("sends a typed question of trade ideas around one player, so the API can find him", async () => {
    routeTo("trade_ideas");
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await ask("trade ideas for kenneth walker");
    await waitFor(() => expect(callsTo("/trade-ideas")).toHaveLength(1));
    expect(JSON.parse(callsTo("/trade-ideas")[0][1].body)).toEqual({ roster_id: 3, partner: null, question: "trade ideas for kenneth walker", turns: [] });
  });

  it("sends a follow-up of trade ideas with the trade turn before it, so the API reads its limit (H18)", async () => {
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await openTopic("Trade ideas");
    await waitFor(() => expect(callsTo("/trade-ideas")).toHaveLength(1));
    await screen.findByRole("article", { name: "Trade ideas", busy: false });
    routeTo("trade_ideas");
    await ask("id rather not trade a WR");
    await waitFor(() => expect(callsTo("/trade-ideas")).toHaveLength(2));
    const body = JSON.parse(callsTo("/trade-ideas")[1][1].body);
    expect(body.question).toBe("id rather not trade a WR");
    expect(body.turns).toHaveLength(1);
    expect(body.turns[0].question).toBe("Trade ideas");
    expect(body.turns[0].answer).toMatch(/^\d+ offers?\. Offer 1: /);
  });

  it("shows each plain step one by one before the whole Answer (AT-28)", async () => {
    const stream = heldStream("/trade-ideas");
    render(<HomePage />);
    await openTopic("Trade ideas");
    const article = await screen.findByRole("article", { name: "Trade ideas" });
    const steps = () => within(within(article).getByRole("list", { name: "Steps" })).getAllByRole("listitem").map((step) => step.querySelector("[data-line]")?.textContent);
    // Every kind waits on the same first line, and the newest step is the live one, with one ellipsis.
    expect(steps()).toEqual(["Reading the league…"]);
    const lines = ideasStream.filter((part) => part.type === "data-step");
    await stream.send({ type: "start" });
    await stream.send(lines[0]);
    await waitFor(() => expect(steps()).toEqual(["Checked 11 teams for a fit…"]));
    await stream.send(lines[1]);
    await stream.send(lines[2]);
    await waitFor(() => expect(steps()).toEqual(["Checked 11 teams for a fit", "Built 56 offers", "Weighed 56 offers…"]));
    expect(screen.queryByRole("region", { name: "Trade ideas" })).toBeNull();
    for (const part of ideasStream.slice(ideasStream.indexOf(lines[2]) + 1)) await stream.send(part);
    await stream.end();
    const region = await screen.findByRole("region", { name: "Trade ideas" });
    // The steps stay above the Answer, each one done.
    expect(steps()).toEqual(["Checked 11 teams for a fit", "Built 56 offers", "Weighed 56 offers", "Picked the best 2"]);
    const list = within(article).getByRole("list", { name: "Steps" });
    expect(list.compareDocumentPosition(region) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(within(list).getAllByRole("listitem").map((step) => step.getAttribute("data-state"))).toEqual(["done", "done", "done", "done"]);
  });

  it("names no inner tool and no manager word in any step or Answer", async () => {
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await openTopic("Trade ideas");
    const ideas = await screen.findByRole("region", { name: "Trade ideas" });
    const text = (ideas.textContent ?? "").toLowerCase();
    for (const word of ["jev", "advisor", "finder", "rival", "brian"]) expect(text).not.toContain(word);
    for (const part of ideasStream.filter((each) => each.type === "data-step")) {
      expect(JSON.stringify(part).toLowerCase()).not.toMatch(/jev|advisor|finder|rival|brian/);
    }
  });

  /* The ideas stream with the offers of the fixture moved to near ideas, each with a reason, so no offer is a pick. */
  function nearStream(picks: number) {
    const parts = structuredClone(ideasStream) as typeof ideasStream;
    const answer = parts.find((part) => part.type === "data-answer") as unknown as { data: { document: Record<string, unknown> & { trades: { offer_id: string; sides: unknown[] }[] } } };
    const doc = answer.data.document;
    doc.near = doc.trades.slice(picks).map((trade, i) => ({ offer_id: trade.offer_id, sides: trade.sides, reason: `Reason ${i + 1}: you give up your RB for a WR you do not need.` }));
    doc.trades = doc.trades.slice(0, picks);
    doc.empty = picks === 0 ? "No offer on the list helps your lineup enough to send." : null;
    return parts;
  }

  it("shows the near ideas with the reason under each, under a plain label, when no offer is a clear win (H21)", async () => {
    streamOf("/trade-ideas", nearStream(0));
    render(<HomePage />);
    await openTopic("Trade ideas");
    const ideas = await screen.findByRole("region", { name: "Trade ideas" });
    const near = within(ideas).getByRole("list", { name: "Ideas, none a clear win" });
    expect(within(near).getAllByRole("listitem")).toHaveLength(2);
    expect(near.textContent).toContain("You give Derrick Henry and get Tee Higgins.");
    expect(near.textContent).toContain("Reason 1: you give up your RB for a WR you do not need.");
    expect(near.textContent).toContain("Reason 2:");
    // Each idea keeps the link to check it on the Trade page, as an offer does.
    expect(within(near).getAllByRole("link", { name: "Check this trade" })).toHaveLength(2);
    const text = (ideas.textContent ?? "").toLowerCase();
    for (const word of ["jev", "advisor", "finder", "rival", "brian", "front door"]) expect(text).not.toContain(word);
  });

  it("lists the near ideas after the picks under their own label (H21)", async () => {
    streamOf("/trade-ideas", nearStream(1));
    render(<HomePage />);
    await openTopic("Trade ideas");
    const ideas = await screen.findByRole("region", { name: "Trade ideas" });
    const near = within(ideas).getByRole("list", { name: "Also weighed" });
    expect(within(near).getAllByRole("listitem")).toHaveLength(1);
    expect(near.textContent).toContain("You give Derrick Henry and get Amon-Ra St. Brown.");
    expect(within(ideas).getAllByRole("link", { name: "Check this trade" })).toHaveLength(2);
    // The pick comes first, then the near idea.
    const pick = within(ideas).getAllByRole("link", { name: "Check this trade" })[0];
    expect(near.compareDocumentPosition(pick) & Node.DOCUMENT_POSITION_PRECEDING).toBeTruthy();
  });

  it("keeps the whole Answer in the Thread after a reload, at no cost", async () => {
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await openTopic("Trade ideas");
    await screen.findByRole("region", { name: "Trade ideas" });
    cleanup();
    render(<HomePage />);
    expect(await screen.findByRole("region", { name: "Trade ideas" })).toBeTruthy();
    expect(callsTo("/trade-ideas")).toHaveLength(1);
  });
});

describe("sell high or buy low for Lil Fridge", () => {
  it("names a player of the roster of Lil Fridge to sell, with the reason (AT-27)", async () => {
    streamOf("/sell-high", sellStream);
    render(<HomePage />);
    await openTopic("Sell high or buy low");
    const sell = await screen.findByRole("region", { name: "Sell high or buy low" });
    const [url, init] = callsTo("/sell-high")[0];
    expect(url).toMatch(/\/clients\/cpc\/sell-high$/);
    expect(init.headers["X-League-Passphrase"]).toBe(PASSPHRASE);
    expect(JSON.parse(init.body)).toEqual({ roster_id: 3 });
    const picks = within(sell).getAllByRole("listitem", { name: /^Sell / });
    expect(picks.map((pick) => pick.getAttribute("aria-label"))).toEqual(["Sell Romeo Doubs", "Sell Tyler Allgeier"]);
    expect(picks[0].textContent).toContain("WR · NE");
    expect(picks[0].textContent).toContain("his hot last four weeks still make him look good to another manager");
    // The manager page of Your team is the full report.
    expect(within(sell).getByRole("link", { name: "Open your manager page" }).getAttribute("href")).toBe("/2026/managers/3/");
  });

  it("shows the sell list: each row with the player, his ranks, and the headline, and a tap opens the bullets (AT-32)", async () => {
    streamOf("/sell-high", sellStream);
    render(<HomePage />);
    await openTopic("Sell high or buy low");
    const sell = await screen.findByRole("region", { name: "Sell high or buy low" });
    expect(sell.querySelector('[data-block="sell_list"]')).not.toBeNull();
    const [first, second] = within(sell).getAllByRole("listitem", { name: /^Sell / });
    const toggle = within(first).getByRole("button", { name: /Romeo Doubs/ });
    expect(toggle.textContent).toContain("Season WR54");
    expect(toggle.textContent).toContain("Recent WR26");
    expect(toggle.textContent).toContain("his hot last four weeks still make him look good to another manager");
    // The row starts closed, so the bullets wait in place under it.
    const panel = document.getElementById(toggle.getAttribute("aria-controls") ?? "")!;
    expect(toggle.getAttribute("aria-expanded")).toBe("false");
    expect(panel.hasAttribute("hidden")).toBe(true);
    fireEvent.click(toggle);
    expect(toggle.getAttribute("aria-expanded")).toBe("true");
    await waitFor(() => expect(panel.hasAttribute("hidden")).toBe(false));
    const bullets = within(panel).getAllByRole("listitem");
    expect(bullets[0].textContent).toContain("He is out now and not due back until week 14");
    // The other row does not open with it.
    expect(within(second).getByRole("button", { name: /Tyler Allgeier/ }).getAttribute("aria-expanded")).toBe("false");
  });

  it("sends a typed sell high question for Your team", async () => {
    routeTo("sell_high");
    streamOf("/sell-high", sellStream);
    render(<HomePage />);
    await ask("who should I sell high");
    await waitFor(() => expect(callsTo("/sell-high")).toHaveLength(1));
    expect(JSON.parse(callsTo("/sell-high")[0][1].body)).toEqual({ roster_id: 3 });
  });

  it("shows each plain step before the whole Answer", async () => {
    const stream = heldStream("/sell-high");
    render(<HomePage />);
    await openTopic("Sell high or buy low");
    const article = await screen.findByRole("article", { name: "Sell high or buy low" });
    const steps = () => within(within(article).getByRole("list", { name: "Steps" })).getAllByRole("listitem").map((step) => step.querySelector("[data-line]")?.textContent);
    expect(steps()).toEqual(["Reading the league…"]);
    const lines = sellStream.filter((part) => part.type === "data-step");
    await stream.send({ type: "start" });
    await stream.send(lines[0]);
    await waitFor(() => expect(steps()).toEqual(["Lined up your 14 players…"]));
    expect(screen.queryByRole("region", { name: "Sell high or buy low" })).toBeNull();
    for (const part of sellStream.slice(sellStream.indexOf(lines[0]) + 1)) await stream.send(part);
    await stream.end();
    expect(await screen.findByRole("region", { name: "Sell high or buy low" })).toBeTruthy();
  });

  it("shows the plain line of a roster with no clear sell", async () => {
    const line = "No player on your roster is priced above what he gives you.";
    const answer = sellStream.find((part) => part.type === "data-answer")!;
    const block = sellStream.find((part) => part.type === "data-block")!;
    const empty = { ...answer, data: { ...answer.data, document: { ...answer.data!.document, picks: [], empty: line } } };
    const emptyBlock = { ...block, data: { ...block.data, rows: [], empty: line } };
    streamOf("/sell-high", [{ type: "start" }, emptyBlock, empty, { type: "finish" }]);
    render(<HomePage />);
    await openTopic("Sell high or buy low");
    const sell = await screen.findByRole("region", { name: "Sell high or buy low" });
    expect(sell.querySelector('[data-block="sell_list"]')?.textContent).toContain(line);
    expect(within(sell).queryAllByRole("listitem", { name: /^Sell / })).toHaveLength(0);
  });

  it("names no inner tool and no manager word in any step or Answer", async () => {
    streamOf("/sell-high", sellStream);
    render(<HomePage />);
    await openTopic("Sell high or buy low");
    const text = ((await screen.findByRole("region", { name: "Sell high or buy low" })).textContent ?? "").toLowerCase();
    for (const word of ["jev", "advisor", "finder", "rival", "brian"]) expect(text).not.toContain(word);
    expect(JSON.stringify(sellStream).toLowerCase()).not.toMatch(/jev|advisor|finder|rival|brian/);
  });
});

describe("an older trade Answer in the Thread", () => {
  it("keeps a settled trade check whole, with its Lean and its link, when a new question lands", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", checkStream);
    render(<HomePage />);
    await ask(SURE);
    await screen.findByRole("region", { name: "Trade check" });
    await openTopic("Week recap");
    const [trade] = await screen.findAllByRole("article", { name: SURE });
    await screen.findAllByRole("article", { name: "Week recap" });
    expect(within(trade).getByRole("region", { name: "Trade check" }).textContent).toContain("Send it");
    expect(within(trade).getByRole("link", { name: "Open it on the Trade page" })).toBeTruthy();
    expect(within(trade).queryByRole("button", { name: `${SURE}: Send it` })).toBeNull();
  });

  it("keeps a trade Answer in flight open, with its steps, under a newer question", async () => {
    const stream = heldStream("/trade-ideas");
    render(<HomePage />);
    await openTopic("Trade ideas");
    const article = await screen.findByRole("article", { name: "Trade ideas" });
    await stream.send({ type: "start" });
    await openTopic("Week recap");
    await screen.findAllByRole("article", { name: "Week recap" });
    expect(within(article).getByRole("list", { name: "Steps" })).toBeTruthy();
    expect(within(article).queryByRole("button", { expanded: false })).toBeNull();
    await stream.end();
  });
});
