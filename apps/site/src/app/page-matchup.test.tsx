/**
 * Tests for the matchup card of Your last matchup and Your next matchup, and the rank mover list of Power rankings, on
 * the front door. Each test renders the page over the real page.json of week 9 and the topics.json that the build writes.
 */
import { cpSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import liveStream from "./front-door/fixtures/next-matchup-stream.json";

/* Bo Girds, the team of the acceptance tests, in each league. */
const BO_GIRDS = { cpc: 6, norcal: 7 } as const;
type League = keyof typeof BO_GIRDS;

const roots: string[] = [];

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(async () => new Response("", { status: 404 })));
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
  const root = mkdtempSync(join(tmpdir(), "front-door-matchup-"));
  roots.push(root);
  // The path comes from this file and not from the working folder, because the test points the working folder at root.
  cpSync(join(__dirname, "..", "fixtures", "recap", league, "public"), join(root, "public"), { recursive: true });
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them.
  vi.resetModules();
  localStorage.setItem("cpc.your-team", String(BO_GIRDS[league]));
  return (await import("./front-door/door-page")).default;
}

/* Open "More", tap one Topic, and return the block of its Answer. */
async function openBlock(topic: string, kind: string) {
  fireEvent.click(await screen.findByRole("button", { name: "More" }));
  const list = await screen.findByRole("list", { name: "All Topics" });
  fireEvent.click(within(list).getByRole("button", { name: new RegExp(`^${topic}:`) }));
  const answer = await screen.findByRole("article", { name: topic });
  await waitFor(() => expect(answer.querySelector(`[data-block="${kind}"]`)).not.toBeNull());
  return answer.querySelector<HTMLElement>(`[data-block="${kind}"]`)!;
}

describe("the matchup card", () => {
  it("shows the final scores against Teehee, then the two lineups slot by slot with a gap bar each (AT-24)", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    const card = await openBlock("Your last matchup", "matchup");
    expect(card.textContent).toContain("Final");
    expect(within(card).getByText("114.07")).toBeTruthy();
    expect(within(card).getByText("100.63")).toBeTruthy();
    expect(card.textContent).toContain("Teehee");
    const slots = within(card).getByRole("list", { name: "Slot by slot" });
    const rows = within(slots).getAllByRole("listitem");
    expect(rows.map((row) => row.getAttribute("data-slot"))).toEqual(["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "DEF"]);
    // Each slot has one bar from the center line, to the side of the player who won it.
    for (const row of rows) expect(row.querySelectorAll("[data-gap]")).toHaveLength(1);
    const flex = rows[6];
    expect(flex.textContent).toContain("M. Golden");
    expect(flex.textContent).toContain("A. St. Brown");
    expect(flex.querySelector("[data-gap]")!.getAttribute("data-gap")).toBe("you");
    expect(rows[0].querySelector("[data-gap]")!.getAttribute("data-gap")).toBe("them");
    expect(flex.getAttribute("aria-label")).toContain("+14.8");
  });

  it("shows the projected scores of Your next matchup, and an empty slot as a dash", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    const card = await openBlock("Your next matchup", "matchup");
    expect(card.textContent).toContain("Projected");
    expect(card.textContent).toContain("The Blue Tent");
    const rows = within(within(card).getByRole("list", { name: "Slot by slot" })).getAllByRole("listitem");
    // The Blue Tent holds no DEF, so its side of the slot is empty.
    expect(rows.at(-1)!.textContent).toContain("Empty");
  });

  it("shows three FLEX slots in norcal", async () => {
    const Door = await doorOf("norcal");
    render(<Door />);
    const card = await openBlock("Your last matchup", "matchup");
    expect(within(card).getByText("155.38")).toBeTruthy();
    const rows = within(within(card).getByRole("list", { name: "Slot by slot" })).getAllByRole("listitem");
    expect(rows.filter((row) => row.getAttribute("data-slot") === "FLEX")).toHaveLength(3);
  });
});

/* The stream of the live card, as the API sent it over the live Sleeper week 10 of cpc. */
const sse = (parts: unknown[]) => parts.map((part) => `data: ${JSON.stringify(part)}\n\n`).join("") + "data: [DONE]\n\n";

describe("the live card of Your next matchup", () => {
  it("swaps in the projected totals and the win odds of the live week, with the time of the read (AT-25)", async () => {
    const fetchStub = vi.fn(async (url: string) =>
      String(url).endsWith("/next-matchup") ? new Response(sse(liveStream), { headers: { "Content-Type": "text/event-stream" } }) : new Response("", { status: 404 }),
    );
    vi.stubGlobal("fetch", fetchStub);
    localStorage.setItem("cpc.passphrase", "cornerstone-test");
    const Door = await doorOf("cpc");
    render(<Door />);
    await openBlock("Your next matchup", "matchup");
    const answer = screen.getByRole("article", { name: "Your next matchup" });
    await waitFor(() => expect(answer.textContent).toContain("121.7"));
    const card = answer.querySelector<HTMLElement>('[data-block="matchup"]')!;
    expect(card.textContent).toContain("92.9");
    expect(within(card).getByRole("img", { name: "Your win odds, 82%" })).toBeTruthy();
    expect(answer.textContent).toContain("Live projections as of");
    const [url, init] = fetchStub.mock.calls.find(([each]) => String(each).endsWith("/next-matchup"))! as unknown as [string, RequestInit];
    expect(url).toMatch(/\/clients\/cpc\/next-matchup$/);
    expect(JSON.parse(String(init.body))).toEqual({ roster_id: BO_GIRDS.cpc });
  });

  it("keeps the card of the weekly build when the API sends no live card", async () => {
    localStorage.setItem("cpc.passphrase", "cornerstone-test");
    const Door = await doorOf("cpc");
    render(<Door />);
    const card = await openBlock("Your next matchup", "matchup");
    expect(card.textContent).toContain("The Blue Tent");
    expect(screen.getByRole("article", { name: "Your next matchup" }).textContent).not.toContain("Live projections");
  });
});

describe("the rank mover list", () => {
  it("shows one row per team with the rank, the name, a bar from the center, and the arrow with the places (AT-26)", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    const list = await openBlock("Power rankings", "rank_movers");
    const rows = within(within(list).getByRole("list", { name: "Power rankings" })).getAllByRole("listitem");
    expect(rows).toHaveLength(12);
    expect(rows[0].textContent).toContain("1");
    expect(rows[0].textContent).toContain("Return of T Mac");
    expect(rows[0].querySelector('[data-move="up"]')).not.toBeNull();
    expect(rows[0].getAttribute("aria-label")).toContain("up 3");
    expect(rows[5].querySelector('[data-move="down"]')).not.toBeNull();
    expect(rows[5].getAttribute("aria-label")).toContain("down 4");
    expect(rows[8].querySelector('[data-move="none"]')).not.toBeNull();
    const you = rows.filter((row) => row.hasAttribute("data-you"));
    expect(you).toHaveLength(1);
    expect(you[0].textContent).toContain("Bo Girds");
  });
});
