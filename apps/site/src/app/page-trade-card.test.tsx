/**
 * Tests for the trade card of the front door at /: the two sides with the points of each player, the tug bar, and the
 * Lean of a Trade check, and the one card of Trade ideas with a row per offer. The streams are real runs with the card.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import checkStream from "./front-door/fixtures/trade-check-card-stream.json";
import ideasStream from "./front-door/fixtures/trade-ideas-card-stream.json";
import HomePage from "./front-door/door-page";

/* The readers of public/ read the fixed copy of the cpc data, as in page-trade.test.tsx. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const SURE = "is Courtland Sutton for Kenneth Walker fair";
const fetchStub = vi.fn();
const replies: Record<string, Response[]> = { "/ask": [], "/trade-check": [], "/trade-ideas": [] };

const sse = (parts: unknown[]) => parts.map((part) => `data: ${JSON.stringify(part)}\n\n`).join("") + "data: [DONE]\n\n";
const streamOf = (path: string, parts: unknown[]) => replies[path].push(new Response(sse(parts), { headers: { "Content-Type": "text/event-stream" } }));

function routeTo(topic: string) {
  replies["/ask"].push(Response.json({ route: "topic", topic, team: null, closest: [], suggestion: null, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } }));
}

async function ask(question: string) {
  const box = await screen.findByRole("form", { name: "Ask" });
  fireEvent.change(within(box).getByRole("textbox", { name: "Ask a question" }), { target: { value: question } });
  fireEvent.submit(box);
}

async function openTopic(name: string) {
  fireEvent.click(within(await screen.findByRole("group", { name: "Suggestions" })).getByRole("button", { name: "More" }));
  fireEvent.click(within(await screen.findByRole("list", { name: "All Topics" })).getByRole("button", { name: new RegExp(`^${name}`) }));
}

/* The detail under a row button: the region that the button controls. */
const detailOf = (button: HTMLElement) => document.getElementById(button.getAttribute("aria-controls") ?? "")!;

beforeEach(() => {
  fetchStub.mockImplementation(async (url: string) => {
    const path = Object.keys(replies).find((end) => String(url).endsWith(end));
    return path ? (replies[path].shift() ?? new Response("", { status: 500 })) : new Response("", { status: 404 });
  });
  vi.stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", "3");
  localStorage.setItem("cpc.passphrase", "cornerstone-test");
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  fetchStub.mockReset();
  for (const list of Object.values(replies)) list.length = 0;
  vi.unstubAllGlobals();
});

describe("the trade card of a Trade check", () => {
  it("shows the two sides with the points of each player, the tug bar, and closes with the Lean (AT-34)", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", checkStream);
    render(<HomePage />);
    await ask(SURE);
    const check = await screen.findByRole("region", { name: "Trade check" });
    const card = within(check).getByRole("group", { name: "Trade card" });
    const sides = within(card).getAllByRole("list", { name: /\bgets?$/ });
    expect(sides.map((side) => side.getAttribute("aria-label"))).toEqual(["You get", "Bo Girds gets"]);
    expect(sides[0].textContent).toContain("Kenneth Walker III");
    expect(sides[0].textContent).toContain("154.1");
    expect(sides[1].textContent).toContain("Courtland Sutton");
    expect(sides[1].textContent).toContain("53.1");
    const tug = within(card).getByRole("img", { name: /rest of the season/ });
    expect(tug.getAttribute("aria-label")).toBe("Projected points for the rest of the season: you get 154.1, Bo Girds gets 53.1.");
    // The Lean is the last line of the card, and the card holds no edge line in points.
    expect(card.lastElementChild?.textContent).toBe("Send it.");
    expect((card.textContent ?? "").toLowerCase()).not.toContain("edge");
  });

  it("opens the Case and the top Bullets in place (AT-34)", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", checkStream);
    render(<HomePage />);
    await ask(SURE);
    const card = within(await screen.findByRole("region", { name: "Trade check" })).getByRole("group", { name: "Trade card" });
    const why = within(card).getByRole("button", { name: /Why/ });
    expect(why.getAttribute("aria-expanded")).toBe("false");
    expect(detailOf(why).getAttribute("aria-hidden")).toBe("true");
    fireEvent.click(why);
    expect(why.getAttribute("aria-expanded")).toBe("true");
    const detail = detailOf(why);
    expect(detail.getAttribute("aria-hidden")).toBe("false");
    expect(detail.textContent).toContain("If Bo Girds will say yes, send this right away");
    expect(detail.querySelectorAll("[data-bullet-text]")).toHaveLength(3);
  });

  it("keeps the Trade page link with the trade under the card", async () => {
    routeTo("trade_check");
    streamOf("/trade-check", checkStream);
    render(<HomePage />);
    await ask(SURE);
    const check = await screen.findByRole("region", { name: "Trade check" });
    expect(within(check).getByRole("link", { name: "Open it on the Trade page" }).getAttribute("href")).toBe("/analyze/?team=3&with=6&give=5045&get=8151");
  });
});

describe("the trade card of Trade ideas", () => {
  it("shows one card with a row per offer, and the first offer opens on arrival into the full card (AT-33)", async () => {
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await openTopic("Trade ideas");
    const ideas = await screen.findByRole("region", { name: "Trade ideas" });
    const [card] = within(ideas).getAllByRole("group", { name: "Trade card" });
    const rows = Array.from(card.querySelectorAll<HTMLElement>("[data-offer] > [data-row]"));
    const offers = card.querySelectorAll("[data-offer]");
    expect(offers).toHaveLength(2);
    expect(offers[0].textContent).toContain("With Teehee");
    expect(offers[0].textContent).toContain("Sell Henry while his season rank still looks good");
    expect(rows.map((row) => row.getAttribute("aria-expanded"))).toEqual(["true", "false"]);
    const first = detailOf(rows[0]);
    expect(within(first).getAllByRole("list", { name: /\bgets?$/ }).map((side) => side.textContent)).toEqual([
      expect.stringContaining("Tee Higgins"),
      expect.stringContaining("Derrick Henry"),
    ]);
    expect(within(first).getByRole("img", { name: /rest of the season/ })).toBeTruthy();
    expect(first.querySelectorAll("[data-bullet-text]")).toHaveLength(2);
    expect(within(first).getByRole("link", { name: "Check this trade" }).getAttribute("href")).toBe("/analyze/?team=3&with=12&give=3198&get=6801");
  });

  it("opens another offer on a tap", async () => {
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await openTopic("Trade ideas");
    const ideas = await screen.findByRole("region", { name: "Trade ideas" });
    const second = within(ideas.querySelectorAll<HTMLElement>("[data-offer]")[1]).getByRole("button", { name: /Teehee/ });
    fireEvent.click(second);
    expect(second.getAttribute("aria-expanded")).toBe("true");
    expect(detailOf(second).textContent).toContain("Amon-Ra St. Brown");
  });

  it("names no inner tool and no manager word in the card", async () => {
    streamOf("/trade-ideas", ideasStream);
    render(<HomePage />);
    await openTopic("Trade ideas");
    const text = ((await screen.findByRole("region", { name: "Trade ideas" })).textContent ?? "").toLowerCase();
    for (const word of ["jev", "advisor", "finder", "rival", "brian", "front door"]) expect(text).not.toContain(word);
  });
});
