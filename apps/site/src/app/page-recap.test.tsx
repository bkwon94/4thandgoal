/**
 * Tests for the recap card of Week recap on the front door. Each test renders the page over a temp public/ folder with the
 * real page.json of week 9 and the topics.json at version 2 that the weekly build writes from it, in cpc and in norcal.
 */
import { cpSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

/* Bo Girds, the team of the acceptance tests of the recap card, in each league. */
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
  const root = mkdtempSync(join(tmpdir(), "front-door-recap-"));
  roots.push(root);
  // The path comes from this file and not from the working folder, because the test points the working folder at root.
  cpSync(join(__dirname, "..", "fixtures", "recap", league, "public"), join(root, "public"), { recursive: true });
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them.
  vi.resetModules();
  localStorage.setItem("cpc.your-team", String(BO_GIRDS[league]));
  return (await import("./front-door/door-page")).default;
}

/* Open "More", tap Week recap, and return the recap card of its Answer. */
async function openRecap() {
  fireEvent.click(await screen.findByRole("button", { name: "More" }));
  const list = await screen.findByRole("list", { name: "All Topics" });
  fireEvent.click(within(list).getByRole("button", { name: /^Week recap:/ }));
  const answer = await screen.findByRole("article", { name: "Week recap" });
  await waitFor(() => expect(answer.querySelector('[data-block="recap"]')).not.toBeNull());
  return answer.querySelector<HTMLElement>('[data-block="recap"]')!;
}

describe("the recap card", () => {
  it("shows the score, the place, a mark for each team, and the median tick in cpc (AT-22)", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    const card = await openRecap();
    expect(within(card).getByText("114.07")).toBeTruthy();
    expect(within(card).getByText("3rd of 12")).toBeTruthy();
    const strip = within(card).getByRole("img", { name: /scores/ });
    expect(strip.querySelectorAll("[data-mark]")).toHaveLength(12);
    expect(strip.querySelectorAll('[data-mark="you"]')).toHaveLength(1);
    expect(strip.querySelector("[data-median]")).not.toBeNull();
    expect(card.textContent).toContain("Median 103.51");
    expect(strip.getAttribute("aria-label")).toContain("median 103.51");
  });

  it("shows the top scorer of Your team against his projection, and the first sentence of the recap", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    const card = await openRecap();
    expect(card.textContent).toContain("Kenneth Walker III");
    expect(card.textContent).toContain("34.3");
    expect(card.textContent).toContain("Proj 20.07");
    expect(card.textContent).toContain("Bo Girds held the lead over Teehee from Thursday all the way to Monday");
  });

  it("shows the score against kaiedmonds and no median tick in norcal (AT-23)", async () => {
    const Door = await doorOf("norcal");
    render(<Door />);
    const card = await openRecap();
    expect(within(card).getByText("155.38")).toBeTruthy();
    expect(card.textContent).toContain("kaiedmonds");
    const strip = within(card).getByRole("img", { name: /scores/ });
    expect(strip.querySelectorAll("[data-mark]")).toHaveLength(12);
    expect(strip.querySelector("[data-median]")).toBeNull();
    expect(card.textContent).not.toContain("Median");
  });

  it("takes the place of the stats and the rows, and keeps the text of the week under it", async () => {
    const Door = await doorOf("cpc");
    render(<Door />);
    await openRecap();
    const answer = screen.getByRole("article", { name: "Week recap" });
    // The awards rows of version 1 leave, because the card says the week at a glance.
    expect(answer.textContent).not.toContain("MVB");
    expect(answer.textContent).toContain("Read the full report");
  });
});
