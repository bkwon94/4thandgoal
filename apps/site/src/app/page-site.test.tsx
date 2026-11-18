/**
 * Tests for the Site answer of the front door at /: the page list that each ask sends, and the page card of a site route.
 * fetch is a test stub at the fetch seam that answers as the ask route of the API does, with the real Menu of the cpc build.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import HomePage from "./front-door/door-page";
// The jsdom stand-ins that the Drawer of the menu sheet needs.
import "@cpc/design/ui/sheet-jsdom";

/* The readers of public/ read the fixed copy of the cpc data, to week 8, so a weekly publish never changes these tests. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const PASSPHRASE = "cornerstone-test";
const fetchStub = vi.fn();
const replies: Response[] = [];
const askCalls = () => fetchStub.mock.calls.filter(([url]) => String(url).endsWith("/ask"));

/* One site route of the ask route, as the API sends it. */
function siteRoute(page: string) {
  return { route: "site", line: null, topic: null, team: null, closest: [], suggestion: null, page, jev: { model: "jev-1.14.0", nouls: {}, choices: {} } };
}

function answerWith(body: unknown) {
  replies.push(new Response(JSON.stringify(body), { status: 200 }));
}

async function ask(question: string) {
  const box = await screen.findByRole("form", { name: "Ask" });
  fireEvent.change(within(box).getByRole("textbox", { name: "Ask a question" }), { target: { value: question } });
  fireEvent.submit(box);
}

async function articleWith(question: string, text: string) {
  await waitFor(() => expect(screen.getByRole("article", { name: question }).textContent).toContain(text));
  return screen.getByRole("article", { name: question });
}

beforeEach(() => {
  fetchStub.mockImplementation(async (url: string) =>
    String(url).endsWith("/ask") ? (replies.shift() ?? new Response("", { status: 500 })) : new Response("", { status: 404 }),
  );
  vi.stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", "3");
  localStorage.setItem("cpc.passphrase", PASSPHRASE);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  fetchStub.mockReset();
  replies.length = 0;
  vi.unstubAllGlobals();
});

/* The pages of the cpc Menu with no Home, then the midseason report and the sim, each with its label and its blurb. */
const CPC_PAGES = [
  { key: "week", label: "Week 8", blurb: "The recap, scores, and awards of the week." },
  { key: "rankings", label: "Power Rankings", blurb: "Every team ranked, with the weekly moves." },
  { key: "managers", label: "Managers", blurb: "Each manager, with the grades of the season." },
  { key: "analyzer", label: "Trade Analyzer", blurb: "Grades a trade between two or more teams." },
  { key: "midseason", label: "Midseason Report", blurb: "The midseason awards, grades, and roasts." },
  { key: "sim", label: "Playoff Sim", blurb: "Plays out the rest of the season, game by game." },
];

describe("the page list of each ask", () => {
  it("sends the pages of the cpc Menu with no Home, plus the midseason report and the sim", async () => {
    answerWith(siteRoute("analyzer"));
    render(<HomePage />);
    await ask("where is the trade analyzer");
    await waitFor(() => expect(askCalls()).toHaveLength(1));
    expect(JSON.parse(askCalls()[0][1].body).pages).toEqual(CPC_PAGES);
  });
});

describe("the page card of a site question", () => {
  it("shows the card of the Trade Analyzer for 'where is the trade analyzer' (AT-1)", async () => {
    answerWith(siteRoute("analyzer"));
    render(<HomePage />);
    await ask("where is the trade analyzer");
    const card = await articleWith("where is the trade analyzer", "The Trade Analyzer has its own page.");
    expect(card.textContent).toContain("Grades a trade between two or more teams.");
    expect(within(card).getByRole("link", { name: "Open the Trade Analyzer" }).getAttribute("href")).toBe("/analyze/");
  });

  it.each([
    { question: "how do I use the sim", page: "sim", label: "Playoff Sim", blurb: "Plays out the rest of the season, game by game.", href: "/midseason/2026/#sim", at: "AT-4" },
    { question: "take me to the weekly reports", page: "week", label: "Week 8", blurb: "The recap, scores, and awards of the week.", href: "/2026/week-08/", at: "AT-5" },
    { question: "midseason report?", page: "midseason", label: "Midseason Report", blurb: "The midseason awards, grades, and roasts.", href: "/midseason/2026/", at: "AT-6" },
    { question: "wheres the trade thing", page: "analyzer", label: "Trade Analyzer", blurb: "Grades a trade between two or more teams.", href: "/analyze/", at: "AT-7" },
  ])("shows the card of the $label for '$question' ($at)", async ({ question, page, label, blurb, href }) => {
    answerWith(siteRoute(page));
    render(<HomePage />);
    await ask(question);
    const card = await articleWith(question, `The ${label} has its own page.`);
    expect(card.textContent).toContain(blurb);
    expect(within(card).getByRole("link", { name: `Open the ${label}` }).getAttribute("href")).toBe(href);
    // The card holds no tutorial and no Menu line under the name.
    expect(card.textContent).not.toMatch(/Menu ·|Step 1/);
  });

  it("stays on / with the card in view, and only the Open link leads to the page (AT-10)", async () => {
    answerWith(siteRoute("analyzer"));
    render(<HomePage />);
    await ask("where is the trade analyzer");
    const card = await articleWith("where is the trade analyzer", "The Trade Analyzer has its own page.");
    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(window.location.pathname).toBe("/");
    const open = within(card).getByRole("link", { name: "Open the Trade Analyzer" });
    expect(open.tagName).toBe("A");
  });

  it("holds the other 5 pages of cpc in the fold 'All pages · 5', each with its blurb and its link (AT-11)", async () => {
    answerWith(siteRoute("analyzer"));
    render(<HomePage />);
    await ask("where is the trade analyzer");
    const card = await articleWith("where is the trade analyzer", "The Trade Analyzer has its own page.");
    const fold = within(card).getByRole("button", { name: "All pages · 5" });
    expect(fold.getAttribute("aria-expanded")).toBe("false");
    expect(within(card).queryByRole("list", { name: "Pages" })).toBeNull();
    fireEvent.click(fold);
    expect(fold.getAttribute("aria-expanded")).toBe("true");
    const rows = within(within(card).getByRole("list", { name: "Pages" })).getAllByRole("link");
    expect(rows.map((row) => [row.textContent, row.getAttribute("href")])).toEqual([
      ["Week 8The recap, scores, and awards of the week.", "/2026/week-08/"],
      ["Power RankingsEvery team ranked, with the weekly moves.", "/rankings/"],
      ["ManagersEach manager, with the grades of the season.", "/2026/managers/"],
      ["Midseason ReportThe midseason awards, grades, and roasts.", "/midseason/2026/"],
      ["Playoff SimPlays out the rest of the season, game by game.", "/midseason/2026/#sim"],
    ]);
  });

  it("names no internal part in the card or the fold (AT-17, card half)", async () => {
    answerWith(siteRoute("analyzer"));
    render(<HomePage />);
    await ask("where is the trade analyzer");
    const card = await articleWith("where is the trade analyzer", "The Trade Analyzer has its own page.");
    fireEvent.click(within(card).getByRole("button", { name: "All pages · 5" }));
    expect(card.textContent).not.toMatch(/jev|advisor|finder|front door|rival/i);
  });

  it("shows the same card after a reload, with no new ask request (AT-12)", async () => {
    answerWith(siteRoute("analyzer"));
    const first = render(<HomePage />);
    await ask("where is the trade analyzer");
    await articleWith("where is the trade analyzer", "The Trade Analyzer has its own page.");
    first.unmount();
    render(<HomePage />);
    const card = await articleWith("where is the trade analyzer", "The Trade Analyzer has its own page.");
    expect(within(card).getByRole("link", { name: "Open the Trade Analyzer" }).getAttribute("href")).toBe("/analyze/");
    expect(askCalls()).toHaveLength(1);
  });
});

describe("the none case of a site question", () => {
  it("shows the none rows of every cpc page for a kept key that the client lacks (AT-21)", async () => {
    localStorage.setItem("cpc.thread", JSON.stringify({ "3": { week: 8, entries: [{ kind: "site", question: "where are the waivers", page: "waiver" }] } }));
    render(<HomePage />);
    const card = await articleWith("where are the waivers", "The site has no page for that. Here is what it has.");
    const rows = within(within(card).getByRole("list", { name: "Pages" })).getAllByRole("link");
    expect(rows.map((row) => row.getAttribute("href"))).toEqual(["/2026/week-08/", "/rankings/", "/2026/managers/", "/analyze/", "/midseason/2026/", "/midseason/2026/#sim"]);
    expect(within(card).queryByRole("link", { name: /^Open the/ })).toBeNull();
    expect(askCalls()).toHaveLength(0);
  });

  it("shows the none rows for the route page 'missing'", async () => {
    answerWith(siteRoute("missing"));
    render(<HomePage />);
    await ask("is there a waiver page");
    const card = await articleWith("is there a waiver page", "The site has no page for that. Here is what it has.");
    expect(within(within(card).getByRole("list", { name: "Pages" })).getAllByRole("link")).toHaveLength(6);
  });
});
