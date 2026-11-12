/**
 * Tests for the slot rank bars of How you stack up and the bye grid of Weak spots at /. The personal route plays the
 * streams that the API test client recorded for Bo Girds of cpc in week 10, over the recorded week 9 Sleeper data.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import HomePage from "./front-door/door-page";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

const PASSPHRASE = "cornerstone-test";
const BO_GIRDS = 6;
const fetchStub = vi.fn();
const streams: (() => Response)[] = [];

// The path comes from this file and not from the working folder, because the tests point the working folder at the fixed copy.
const recorded = (name: string) => readFileSync(join(__dirname, "..", "fixtures", "personal-answer", `${name}.sse`), "utf8");

function sse(body: string): Response {
  return new Response(body, { headers: { "Content-Type": "text/event-stream", "x-vercel-ai-ui-message-stream": "v1" } });
}

async function tapInMore(name: string) {
  fireEvent.click(await screen.findByRole("button", { name: "More" }));
  const list = await screen.findByRole("list", { name: "All Topics" });
  fireEvent.click(within(list).getByRole("button", { name: new RegExp(`^${name}:`) }));
}

async function checkedArticle(name: string) {
  await waitFor(() => expect(screen.getByRole("article", { name }).textContent).toContain("Checked"), { timeout: 3000 });
  return screen.getByRole("article", { name });
}

beforeEach(() => {
  fetchStub.mockImplementation(async (url: string) => {
    if (String(url).endsWith("/personal")) return streams.shift()?.() ?? new Response("", { status: 500 });
    return new Response("", { status: 404 });
  });
  vi.stubGlobal("fetch", fetchStub);
  localStorage.setItem("cpc.your-team", String(BO_GIRDS));
  localStorage.setItem("cpc.passphrase", PASSPHRASE);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  fetchStub.mockReset();
  streams.length = 0;
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("the blocks of the roster grade of Bo Girds", () => {
  it("shows the slot rank bars of How you stack up: four rows only, and the grade with its read (AT-30)", async () => {
    streams.push(() => sse(recorded("stack-up-bars")));
    render(<HomePage />);
    await tapInMore("How you stack up");
    const answer = await checkedArticle("How you stack up");
    const bars = within(answer).getByRole("list", { name: "Slot ranks" });
    const rows = within(bars).getAllByRole("listitem");
    expect(rows.map((row) => row.textContent)).toEqual(["QB10th of 12", "RB6th of 12", "WR4th of 12", "TE5th of 12"]);
    expect(answer.textContent).not.toMatch(/FLEX|DEF/);
    // The header holds the grade and its read.
    const head = within(answer).getByRole("group", { name: "Roster grade" });
    expect(head.textContent).toContain("B");
    expect(head.textContent).toContain("Soft at QB. Thin at WR.");
    // A rank under the league middle leans left, and a rank above it leans right.
    expect(rows[0].querySelector("[data-lean]")?.getAttribute("data-lean")).toBe("worse");
    expect(rows[2].querySelector("[data-lean]")?.getAttribute("data-lean")).toBe("better");
    // The block takes the place of the stats and the part rows of the rows block.
    expect(answer.textContent).not.toContain("Projection Ahead");
  });

  it("shows the bye grid of Weak spots, with a red dot for each starter in his bye week (AT-31)", async () => {
    streams.push(() => sse(recorded("weak-spots-byes")));
    render(<HomePage />);
    await tapInMore("Weak spots");
    const answer = await checkedArticle("Weak spots");
    const grid = within(answer).getByRole("table", { name: "Byes, weeks 10 to 14" });
    const weeks = within(grid).getAllByRole("columnheader").map((cell) => cell.textContent);
    expect(weeks).toEqual(["Player", "10", "11", "12", "13", "14"]);
    const marked = (label: string) =>
      within(grid)
        .getAllByRole("row")
        .flatMap((row) => {
          const cells = within(row).queryAllByRole("cell");
          const name = within(row).queryByRole("rowheader")?.getAttribute("data-name");
          return cells.flatMap((cell, index) => (cell.textContent === label ? [`${name} ${weeks[index + 1]}`] : []));
        });
    // The starters of Bo Girds whose NFL team has its bye in the weeks of the grid, from the NFL schedules.
    expect(marked("Starter on a bye").sort()).toEqual(["Kyren Williams 11", "Matthew Golden 11", "Trey McBride 14", "Zay Flowers 13"]);
    // The bench on a bye gets a quiet dot, never the red one.
    expect(marked("Bench on a bye").sort()).toEqual(["Blake Corum 11", "Lamar Jackson 13", "Mike Washington Jr. 13", "Terrance Ferguson 11"]);
    expect(within(grid).getAllByRole("rowheader")).toHaveLength(15);
  });
});
