/**
 * Tests for the cap lines of the front door at /. Each test renders the page with the fixed copy of the published data of cpc.
 * fetch is a test stub that answers as the ask route and the trade routes of the API do past a cap.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import HomePage from "./page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const PASSPHRASE = "cornerstone-test";
const QUESTION = "highest scoring team this season";
const TEAM_LINE = "That's 25 questions today. Ask again tomorrow.";
const LEAGUE_LINE = "The league's question budget is used up for this month. It resets on Dec 1.";
const CLOSEST = ["playoff_race", "your_season", "power_rankings"];
// The words that a cap line never holds: no internal name, no "rival", and never the commissioner by name.
const INNER_NAMES = ["jev", "advisor", "finder", "rival", "brian"];
const TEAMS = ["lil fridge", "bo girds"];
const fetchStub = vi.fn();
const replies: Record<string, Response[]> = { "/ask": [], "/ask/free": [], "/trade-ideas": [] };

const callsTo = (path: string) => fetchStub.mock.calls.filter(([url]) => String(url).endsWith(path));

/* The answer of the ask route at a cap, as the API sends it: the cap route, its line, and the 3 closest Topics. */
function capRoute(line: string) {
  replies["/ask"].push(
    Response.json({ route: "cap", line, topic: null, team: null, closest: CLOSEST, suggestion: null, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } }),
  );
}

async function ask(question: string) {
  const box = await screen.findByRole("form", { name: "Ask" });
  fireEvent.change(within(box).getByRole("textbox", { name: "Ask a question" }), { target: { value: question } });
  fireEvent.submit(box);
}

async function capCard(question: string, line: string) {
  await waitFor(() => expect(screen.getByRole("article", { name: question }).textContent).toContain(line));
  return screen.getByRole("article", { name: question });
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

describe("the caps of the front door", () => {
  it("shows the team line with the 3 closest Topics, and makes no call for a free answer (AT-37)", async () => {
    capRoute(TEAM_LINE);
    render(<HomePage />);
    await screen.findByRole("group", { name: "Suggestions" });
    await ask(QUESTION);
    const card = await capCard(QUESTION, TEAM_LINE);
    const topics = within(within(card).getByRole("group", { name: "Closest Topics" })).getAllByRole("button");
    expect(topics.map((topic) => topic.textContent)).toEqual(["Playoff race", "Your season", "Power rankings"]);
    // The 3 closest Topics show once, so the chips of the dock hide.
    expect(screen.queryByRole("group", { name: "Suggestions" })).toBeNull();
    expect(callsTo("/ask/free")).toHaveLength(0);
    expect(card.textContent).not.toContain("no injury news");
  });

  it("shows the league line with the date it resets (AT-38)", async () => {
    capRoute(LEAGUE_LINE);
    render(<HomePage />);
    await ask(QUESTION);
    const card = await capCard(QUESTION, LEAGUE_LINE);
    expect(within(card).getByRole("group", { name: "Closest Topics" })).toBeTruthy();
  });

  it("names no manager and no internal name in a cap line", async () => {
    capRoute(TEAM_LINE);
    render(<HomePage />);
    await ask(QUESTION);
    const text = (await capCard(QUESTION, TEAM_LINE)).textContent!.replace(QUESTION, "").toLowerCase();
    // Lil Fridge is Your team, and Bo Girds is another team of the league.
    expect([...TEAMS, ...INNER_NAMES].filter((word) => text.includes(word))).toEqual([]);
  });

  it("still opens the power rankings Answer in full past the team cap (AT-40)", async () => {
    capRoute(TEAM_LINE);
    render(<HomePage />);
    await ask(QUESTION);
    const card = await capCard(QUESTION, TEAM_LINE);
    fireEvent.click(within(card).getByRole("button", { name: "Power rankings" }));
    const answer = await screen.findByRole("article", { name: "Power rankings" });
    expect(within(answer).getByRole("link", { name: "Read the full report" })).toBeTruthy();
    expect(answer.textContent!.length).toBeGreaterThan(80);
    // The kept Answer comes from the published week, so it makes no call to the API.
    expect(callsTo("/ask")).toHaveLength(1);
  });

  it("shows the cap line for a tap on trade ideas, with the Suggestions of the day as the closest Topics", async () => {
    replies["/trade-ideas"].push(
      new Response(
        [{ type: "start" }, { type: "data-cap", data: { cap: "team", line: TEAM_LINE } }, { type: "finish" }]
          .map((part) => `data: ${JSON.stringify(part)}\n\n`)
          .join("") + "data: [DONE]\n\n",
        { headers: { "Content-Type": "text/event-stream" } },
      ),
    );
    render(<HomePage />);
    const suggestions = await screen.findByRole("group", { name: "Suggestions" });
    const picks = within(suggestions).getAllByRole("button").length - 1;
    fireEvent.click(within(suggestions).getByRole("button", { name: "More" }));
    fireEvent.click(within(await screen.findByRole("list", { name: "All Topics" })).getByRole("button", { name: /^Trade ideas/ }));
    const card = await capCard("Trade ideas", TEAM_LINE);
    const topics = within(within(card).getByRole("group", { name: "Closest Topics" })).getAllByRole("button");
    expect(topics).toHaveLength(Math.min(picks, 3));
    expect(topics.length).toBeGreaterThan(0);
    expect(within(card).queryByRole("region", { name: "Trade ideas" })).toBeNull();
  });
});
