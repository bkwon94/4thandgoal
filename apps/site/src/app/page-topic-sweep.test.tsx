/**
 * The sweep of the 14 Topics of the front door: in cpc and in norcal, each Topic Answer shows one block or none.
 * The league Topics read the real week 9 files, and the API Topics play the streams that real runs of the API recorded.
 */
import { cpSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import sellStream from "./front-door/fixtures/sell-high-stream.json";
import ideasStream from "./front-door/fixtures/trade-ideas-card-stream.json";
import { TOPICS } from "./front-door/topics";

/* Bo Girds, the team of the acceptance tests, in each league. */
const BO_GIRDS = { cpc: 6, norcal: 7 } as const;
type League = keyof typeof BO_GIRDS;

/* The block that each Topic shows for Bo Girds in week 9, or null for a Topic that shows none (the PRD table). Your
   next matchup shows the matchup card of the weekly build here, because the live read of the API is not in reach. A
   tap on Trade check opens the link to the Trade page and makes no call, so it shows no block. */
const BLOCK_OF: Record<string, string | null> = {
  week_recap: "recap",
  last_matchup: "matchup",
  next_matchup: "matchup",
  power_rankings: "rank_movers",
  playoff_race: "ladder",
  your_season: "schedule",
  leaders_trades: null,
  waiver_targets: "waiver_list",
  stack_up: "slot_ranks",
  weak_spots: "bye_grid",
  start_sit: "lineup",
  sell_high: "sell_list",
  trade_ideas: "trade",
  trade_check: null,
};

// The path comes from this file and not from the working folder, because the test points the working folder at root.
const recorded = (name: string) => readFileSync(join(__dirname, "..", "fixtures", "personal-answer", `${name}.sse`), "utf8");
const sseOf = (parts: unknown[]) => parts.map((part) => `data: ${JSON.stringify(part)}\n\n`).join("") + "data: [DONE]\n\n";
const eventStream = (body: string) =>
  new Response(body, { headers: { "Content-Type": "text/event-stream", "x-vercel-ai-ui-message-stream": "v1" } });

/* The recorded stream of each API Topic. The four personal Topics share one route, so the test sends the stream of the
   Topic that it opens. */
const STREAM_OF: Record<string, () => Response> = {
  waiver_targets: () => eventStream(recorded("waiver-list")),
  stack_up: () => eventStream(recorded("stack-up-bars")),
  weak_spots: () => eventStream(recorded("weak-spots-byes")),
  start_sit: () => eventStream(recorded("start-sit")),
  sell_high: () => eventStream(sseOf(sellStream)),
  trade_ideas: () => eventStream(sseOf(ideasStream)),
};

const roots: string[] = [];
let opened = "";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const end = String(url).split("/").pop();
      const routed = end === "personal" || end === "sell-high" || end === "trade-ideas";
      return routed && STREAM_OF[opened] ? STREAM_OF[opened]() : new Response("", { status: 404 });
    }),
  );
  localStorage.setItem("cpc.passphrase", "cornerstone-test");
});

afterEach(() => {
  cleanup();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
  localStorage.clear();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

/* The front door over week 9 of one league, with Bo Girds as Your team. */
async function doorOf(league: League) {
  const root = mkdtempSync(join(tmpdir(), "front-door-sweep-"));
  roots.push(root);
  cpSync(join(__dirname, "..", "fixtures", "recap", league, "public"), join(root, "public"), { recursive: true });
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them.
  vi.resetModules();
  localStorage.setItem("cpc.your-team", String(BO_GIRDS[league]));
  return (await import("./front-door/door-page")).default;
}

/* The outer blocks of an Answer. A block inside another block, such as a part of the trade card, is part of it. */
const blocksIn = (answer: HTMLElement) =>
  Array.from(answer.querySelectorAll<HTMLElement>("[data-block]")).filter((block) => block.parentElement?.closest("[data-block]") === null);

/* Open "More", tap one Topic, and return its Answer once the Answer is whole. */
async function openTopic(key: string, name: string) {
  opened = key;
  fireEvent.click(await screen.findByRole("button", { name: "More" }));
  const list = await screen.findByRole("list", { name: "All Topics" });
  fireEvent.click(within(list).getByRole("button", { name: new RegExp(`^${name}`) }));
  const answer = await screen.findByRole("article", { name });
  const want = BLOCK_OF[key];
  if (want !== null) await waitFor(() => expect(answer.querySelector(`[data-block="${want}"]`)).not.toBeNull(), { timeout: 4000 });
  // A personal Answer ends with the line of its check, so the sweep counts the blocks of the whole Answer.
  if (key in STREAM_OF && !key.startsWith("sell") && !key.startsWith("trade")) {
    await waitFor(() => expect(answer.textContent).toContain("Checked"), { timeout: 4000 });
  }
  return answer;
}

describe.each(["cpc", "norcal"] as const)("the 14 Topics of Bo Girds in %s, week 9", (league) => {
  it("lists each Topic of the sweep", () => {
    expect(Object.keys(BLOCK_OF)).toEqual(TOPICS.map((topic) => topic.key));
  });

  it.each(TOPICS.map((topic) => [topic.name, topic.key] as const))("%s shows one block or none (AT-21)", async (name, key) => {
    const Door = await doorOf(league);
    render(<Door />);
    const answer = await openTopic(key, name);
    const blocks = blocksIn(answer);
    expect(blocks.length).toBeLessThanOrEqual(1);
    expect(blocks.map((block) => block.getAttribute("data-block"))).toEqual(BLOCK_OF[key] === null ? [] : [BLOCK_OF[key]]);
  });

  it("shows Position leaders and recent trades as text with one leader per position in a list (AT-21)", async () => {
    const Door = await doorOf(league);
    render(<Door />);
    const answer = await openTopic("leaders_trades", "Position leaders and recent trades");
    expect(blocksIn(answer)).toEqual([]);
    const items = await waitFor(() => {
      const lists = answer.querySelectorAll("ul");
      const list = Array.from(lists).find((ul) => ul.textContent?.includes("QB"));
      expect(list).toBeTruthy();
      return Array.from(list!.querySelectorAll("li")).map((li) => li.textContent ?? "");
    });
    // One item per position of the leaders of the week page, in its order. Norcal starts no DEF, so it has no DEF leader.
    const page = JSON.parse(readFileSync(join(__dirname, "..", "fixtures", "recap", league, "public", "2026", "week-09", "page.json"), "utf8"));
    const positions = (page.leaders as { position: string; rows: unknown[] }[]).filter((group) => group.rows.length > 0).map((group) => group.position);
    expect(positions.slice(0, 4)).toEqual(["QB", "RB", "WR", "TE"]);
    expect(items.map((item) => item.split(" ")[0])).toEqual(positions);
    // Each position names one player, his points, and his team, as in "RB Kenneth Walker III, 34.3, Bo Girds".
    for (const item of items) expect(item).toMatch(/^[A-Z]+ .+, \d+(\.\d+)?, .+$/);
    if (league === "cpc") expect(items[1]).toBe("RB Kenneth Walker III, 34.3, Bo Girds");
  });
});
