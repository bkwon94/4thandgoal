/**
 * Tests for the standings ladder of Playoff race and the schedule strip of Your season, on the front door.
 * Each test renders the page over the real page.json of week 9 and the topics.json that the build writes.
 */
import { cpSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

/* Bo Girds, the team of the acceptance tests, in each league. */
const BO_GIRDS = { cpc: 6, norcal: 7 } as const;
type League = keyof typeof BO_GIRDS;

const roots: string[] = [];

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(async () => new Response("", { status: 404 })));
});
/* Each action of the front door needs the league passphrase, so each test keeps one, as a manager does after the first
   action. */
beforeEach(() => localStorage.setItem("cpc.passphrase", "cornerstone-test"));

afterEach(() => {
  cleanup();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
  localStorage.clear();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

/* The front door over week 9 of one league, with Bo Girds as Your team. */
async function doorOf(league: League) {
  const root = mkdtempSync(join(tmpdir(), "front-door-season-"));
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

describe("the standings ladder", () => {
  it("shows 12 rows with the rank, the name, an odds bar, and the record, a rule under the 6th row, and Your row in red (AT-27)", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    const ladder = await openBlock("Playoff race", "ladder");
    const rows = within(within(ladder).getByRole("list", { name: "Standings" })).getAllByRole("listitem");
    expect(rows).toHaveLength(12);
    expect(rows[0].textContent).toContain("1");
    expect(rows[0].textContent).toContain("All You Need Is Love");
    expect(rows[0].textContent).toContain("12-6");
    // Each row has one bar of its playoff odds, and its label reads the odds in words.
    for (const row of rows) expect(row.querySelectorAll("[data-odds]")).toHaveLength(1);
    expect(rows[0].getAttribute("aria-label")).toMatch(/\d+% playoff odds/);
    // The rule of the playoff line sits under the 6th row and nowhere else.
    expect(rows.map((row) => row.hasAttribute("data-cut"))).toEqual(rows.map((_, index) => index === 5));
    expect(ladder.textContent).toContain("Playoff line");
    const you = rows.filter((row) => row.hasAttribute("data-you"));
    expect(you).toHaveLength(1);
    expect(you[0].textContent).toContain("Bo Girds");
    expect(you[0].querySelector("[data-odds]")!.getAttribute("data-odds")).toBe("you");
  });
});

describe("the schedule strip", () => {
  it("shows a step path over weeks 10 to 14 against the playoff line, and one row per week (AT-28)", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    const strip = await openBlock("Your season", "schedule");
    const path = strip.querySelector("[data-path]")!;
    expect(path).not.toBeNull();
    // The path is dashed, and it steps once per week left.
    expect(path.getAttribute("stroke-dasharray")).toBeTruthy();
    expect(strip.querySelectorAll("[data-step]")).toHaveLength(5);
    expect(strip.querySelector("[data-cut]")).not.toBeNull();
    const rows = within(within(strip).getByRole("list", { name: "Weeks left" })).getAllByRole("listitem");
    expect(rows.map((row) => row.getAttribute("data-week"))).toEqual(["10", "11", "12", "13", "14"]);
    expect(rows[0].textContent).toContain("The Blue Tent");
    expect(rows[0].textContent).toContain("5th");
    expect(rows[0].textContent).toContain("11-7");
    expect(rows[3].textContent).toContain("NFC Least");
    expect(rows[3].textContent).toContain("3-15");
  });

  it("shows weeks 10 to 14 in norcal too", async () => {
    const Door = await doorOf("norcal");
    render(<Door />);
    const strip = await openBlock("Your season", "schedule");
    const rows = within(within(strip).getByRole("list", { name: "Weeks left" })).getAllByRole("listitem");
    expect(rows).toHaveLength(5);
    expect(rows[0].textContent).toContain("Davlionman");
  });
});
