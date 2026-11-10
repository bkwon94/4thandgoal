/**
 * Tests for the Suggestions that the API serves at /, and for the stale personal Answers of the Thread. Each test renders
 * the page with the fixed copy of the published data of cpc, and the API plays responses that it gave in a live run.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import ideasStream from "./front-door/fixtures/trade-ideas-stream.json";
import { dayOrder } from "./front-door/topics";
import HomePage from "./page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const PASSPHRASE = "cornerstone-test";
const LIL_FRIDGE = 3;
const fetchStub = vi.fn();
const streams: (() => Response)[] = [];

// The path comes from this file and not from the working folder, because the tests point the working folder at the fixed copy.
const fixture = (...parts: string[]) => readFileSync(join(__dirname, "..", "fixtures", ...parts), "utf8");
// The Suggestions of Lil Fridge on Wednesday of week 9 from a live run with the real Jev: power rankings and the week
// recap lift above 0.7.
const SUGGESTIONS = JSON.parse(fixture("suggestions", "lil-fridge-wednesday.json"));
// The Suggestions of Lil Fridge on Thursday of week 10 from a live run with the real Jev: trade ideas has the weakest
// slot of weak spots as its fact. The sell high pick of Jev was under 0.7, so sell high has no fact.
const THURSDAY = JSON.parse(fixture("suggestions", "lil-fridge-thursday.json"));
// The key check of a live run: the key of the kept weak spots Answer of ticket 06 is stale, and the fresh key is current.
const CURRENT = JSON.parse(fixture("suggestions", "current-lil-fridge.json")) as { answers: { key: string; current: boolean; kept_at: string | null }[] };
const callsTo = (path: string) => fetchStub.mock.calls.filter(([url]) => String(url).endsWith(path));

function sse(body: string): Response {
  return new Response(body, { headers: { "Content-Type": "text/event-stream", "x-vercel-ai-ui-message-stream": "v1" } });
}

/* The kept weak spots Answer of Lil Fridge, from the recorded stream of a kept Answer: its block, its text, its key. */
function keptWeakSpots() {
  const parts = fixture("personal-answer", "weak-spots-kept.sse")
    .split("\n\n")
    .map((line) => line.replace(/^data: /, ""))
    .filter((line) => line.startsWith("{"))
    .map((line) => JSON.parse(line));
  const block = parts.find((part) => part.type === "data-block").data;
  const key = parts.find((part) => part.type === "data-key").data.key;
  const text = parts.filter((part) => part.type === "text-delta").map((part) => part.delta).join("").trim();
  return { block, text, key };
}

function keepThread(entries: unknown[]) {
  localStorage.setItem("cpc.thread", JSON.stringify({ [String(LIL_FRIDGE)]: { week: 8, entries } }));
}

/* The clock of a test: 2026-11-12 is a Thursday. */
function onThursday() {
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date("2026-11-12T12:00:00"));
}

/* The clock of a test: 2026-11-11 is a Wednesday. */
function onWednesday() {
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date("2026-11-11T12:00:00"));
}

async function suggestionChips() {
  const row = await screen.findByRole("group", { name: "Suggestions" });
  return within(row).getAllByRole("button");
}

beforeEach(() => {
  fetchStub.mockImplementation(async (url: string, init?: RequestInit) => {
    const path = String(url);
    if (path.endsWith("/suggestions")) return Response.json(SUGGESTIONS);
    if (path.endsWith("/personal/current")) {
      // The API answers each key that the site sends, as the live run answered it.
      const { answers } = JSON.parse(String(init?.body)) as { answers: { key: string }[] };
      return Response.json({ answers: answers.map(({ key }) => CURRENT.answers.find((answer) => answer.key === key) ?? { key, current: true, kept_at: null }) });
    }
    if (path.endsWith("/personal")) return streams.shift()?.() ?? new Response("", { status: 500 });
    return new Response("", { status: 404 });
  });
  vi.stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", String(LIL_FRIDGE));
  localStorage.setItem("cpc.passphrase", PASSPHRASE);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  fetchStub.mockReset();
  streams.length = 0;
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("the Suggestions that the API serves", () => {
  it("lift each urgent Topic above the order of the day (AT-6)", async () => {
    onWednesday();
    render(<HomePage />);
    await waitFor(async () => {
      const [, ...chips] = await suggestionChips();
      expect(chips.map((chip) => chip.getAttribute("aria-label"))).toEqual([
        "Power rankings: 6th, down 5",
        "Week recap: You scored 80.11, 12th of 12",
        "Waiver targets: 19 free agents on the list",
      ]);
    });
    // The site sends the order of Wednesday, where the waivers lead, and the passphrase.
    const [, init] = callsTo("/suggestions")[0];
    const body = JSON.parse(String(init?.body));
    expect(body).toMatchObject({ roster_id: LIL_FRIDGE, opened: {} });
    expect(body.order.slice(0, 2)).toEqual(["waiver_targets", "weak_spots"]);
    expect(new Headers(init?.headers).get("X-League-Passphrase")).toBe(PASSPHRASE);
    expect(callsTo("/suggestions")).toHaveLength(1);
  });

  it("keep the Suggestions of the build when the API does not answer", async () => {
    onWednesday();
    fetchStub.mockImplementation(async () => new Response("", { status: 503 }));
    render(<HomePage />);
    const [, ...chips] = await suggestionChips();
    expect(chips).toHaveLength(3);
    expect(chips.map((chip) => chip.getAttribute("aria-label")).join(" ")).not.toContain("free agents");
  });

  it("drop an opened personal Topic until its fact changes", async () => {
    onWednesday();
    streams.push(() => sse(fixture("personal-answer", "waiver-targets.sse")));
    render(<HomePage />);
    await waitFor(async () => expect((await suggestionChips()).map((chip) => chip.getAttribute("aria-label"))).toContain("Waiver targets: 19 free agents on the list"));
    fireEvent.click(screen.getByRole("button", { name: "Waiver targets: 19 free agents on the list" }));
    await waitFor(() => expect(localStorage.getItem("cpc.opened-topics") ?? "").toContain("19 free agents on the list"));
    await waitFor(async () => expect((await suggestionChips()).map((chip) => chip.getAttribute("aria-label"))).not.toContain("Waiver targets: 19 free agents on the list"));
  });
});

describe("the trade Topics as Suggestions", () => {
  it("show trade ideas with its fact, and a tap runs the Topic and drops the chip", async () => {
    onThursday();
    const sse = ideasStream.map((part) => `data: ${JSON.stringify(part)}\n\n`).join("") + "data: [DONE]\n\n";
    fetchStub.mockImplementation(async (url: string) => {
      const path = String(url);
      if (path.endsWith("/suggestions")) return Response.json(THURSDAY);
      if (path.endsWith("/trade-ideas")) return new Response(sse, { headers: { "Content-Type": "text/event-stream" } });
      return new Response("", { status: 404 });
    });
    render(<HomePage />);
    const chip = "Trade ideas: Offers for your QB, 7th of 12";
    await waitFor(async () => expect((await suggestionChips()).map((each) => each.getAttribute("aria-label"))).toContain(chip));
    fireEvent.click(screen.getByRole("button", { name: chip }));
    // The tap runs the Topic as "More" does: the trade ideas route with Your team and no partner.
    await waitFor(() => expect(callsTo("/trade-ideas")).toHaveLength(1));
    expect(JSON.parse(String(callsTo("/trade-ideas")[0][1]?.body))).toEqual({ roster_id: LIL_FRIDGE, partner: null });
    await screen.findByRole("region", { name: "Trade ideas" });
    await waitFor(async () => expect((await suggestionChips()).map((each) => each.getAttribute("aria-label"))).not.toContain(chip));
  });

  it("never lead a day with the trade check, which has no weekly fact", () => {
    for (const day of [0, 1, 2, 3, 4, 5, 6]) expect(dayOrder(day).slice(0, 5)).not.toContain("trade_check");
  });
});

describe("a stale personal Answer of the Thread", () => {
  it("shows dimmed with the stale line, Refresh, and no checked mark (AT-34)", async () => {
    onWednesday();
    keepThread([{ kind: "personal", key: "weak_spots", team: LIL_FRIDGE, question: null, result: keptWeakSpots() }]);
    render(<HomePage />);
    const answer = await screen.findByRole("article", { name: "Weak spots" });
    await waitFor(() => expect(answer.textContent).toContain("Your roster changed since Tuesday."));
    expect(answer.hasAttribute("data-stale")).toBe(true);
    expect(answer.textContent).not.toContain("Checked");
    expect(within(answer).getByRole("button", { name: "Refresh" })).toBeTruthy();
    // The key check sends the key of the kept Answer, and it costs no stream.
    const [, init] = callsTo("/personal/current")[0];
    expect(JSON.parse(String(init?.body)).answers).toEqual([{ topic: "weak_spots", roster_id: LIL_FRIDGE, team: null, key: keptWeakSpots().key }]);
    expect(callsTo("/personal")).toHaveLength(0);
  });

  it("shows a current Answer as checked, with no stale line", async () => {
    onWednesday();
    const fresh = CURRENT.answers.find((answer) => answer.current)!;
    keepThread([{ kind: "personal", key: "weak_spots", team: LIL_FRIDGE, question: null, result: { ...keptWeakSpots(), key: fresh.key } }]);
    render(<HomePage />);
    const answer = await screen.findByRole("article", { name: "Weak spots" });
    await waitFor(() => expect(callsTo("/personal/current")).toHaveLength(1));
    expect(answer.textContent).toContain("Checked");
    expect(answer.textContent).not.toContain("Your roster changed");
  });

  it("streams a fresh checked Answer in its place on Refresh (AT-35)", async () => {
    onWednesday();
    keepThread([{ kind: "personal", key: "weak_spots", team: LIL_FRIDGE, question: null, result: keptWeakSpots() }]);
    streams.push(() => sse(fixture("personal-answer", "weak-spots-fresh.sse")));
    render(<HomePage />);
    const stale = await screen.findByRole("article", { name: "Weak spots" });
    fireEvent.click(await within(stale).findByRole("button", { name: "Refresh" }));
    await waitFor(() => expect(screen.getByRole("article", { name: "Weak spots" }).textContent).toContain("Checked"), { timeout: 3000 });
    const fresh = screen.getByRole("article", { name: "Weak spots" });
    expect(fresh.hasAttribute("data-stale")).toBe(false);
    expect(fresh.textContent).not.toContain("Your roster changed");
    expect(fresh.textContent).toContain("Bryce Young");
    expect(JSON.parse(String(callsTo("/personal")[0][1]?.body))).toMatchObject({ topic: "weak_spots", roster_id: LIL_FRIDGE, team: null });
    // Only one Answer of weak spots stays in the Thread, with the fresh key.
    await waitFor(() => expect(localStorage.getItem("cpc.thread")).toContain(CURRENT.answers.find((answer) => answer.current)!.key));
    expect(screen.getAllByRole("article", { name: "Weak spots" })).toHaveLength(1);
  });
});
