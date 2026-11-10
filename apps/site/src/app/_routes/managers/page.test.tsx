/**
 * Tests for the managers index route. Each test builds a temp public/ folder with a week page, the managers file, and the rankings file.
 * They read the static params, the title, and the Index list of the real week 8 files of CPC and NorCal: the order, the chips, and an open row.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { cpSync, mkdtempSync, mkdirSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent } from "@testing-library/react";
import { type FixtureClient, fixturePublished } from "@/fixtures/sites";
import { weekPageJson } from "@/fixtures/week-page-json";
import { managers as fixture } from "@cpc/managers/fixtures/managers";
import { rankings as rankingsFixture } from "@cpc/rankings/fixtures/rankings";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

/* A temp public/ folder with the week 6 page, the rankings file, and the managers file when one is given. */
async function routeOver(managers?: unknown) {
  const root = mkdtempSync(join(tmpdir(), "managers-index-"));
  mkdirSync(join(root, "public", "2026", "week-06"), { recursive: true });
  writeFileSync(join(root, "public", "2026", "week-06", "page.json"), weekPageJson({ avatars: {} }));
  writeFileSync(join(root, "public", "2026", "rankings.json"), JSON.stringify(rankingsFixture));
  if (managers !== undefined) writeFileSync(join(root, "public", "2026", "managers.json"), JSON.stringify(managers));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  // The readers read the working folder when they load, so reset them.
  vi.resetModules();
  return import("./page");
}

/* A temp public/ folder with the fixed copy of the published JSON files of one client, as its client build copies them.
   The images stay out, because the route reads only the JSON files and the copy stays fast. */
async function routeOfClient(slug: FixtureClient) {
  const root = mkdtempSync(join(tmpdir(), "managers-index-"));
  cpSync(fixturePublished(slug), join(root, "public"), {
    recursive: true,
    filter: (source) => statSync(source).isDirectory() || source.endsWith(".json"),
  });
  vi.spyOn(process, "cwd").mockReturnValue(root);
  vi.resetModules();
  return import("./page");
}

/* Renders the managers index of one client and gives the rows of the ledger and the chips of the race. */
async function indexOfClient(slug: FixtureClient) {
  const { default: ManagersPage } = await routeOfClient(slug);
  render(await ManagersPage({ params: Promise.resolve({ season: "2026" }) }));
  const main = within(screen.getByRole("main"));
  const rows = () => within(main.getByRole("list", { name: "Index List" })).getAllByRole("listitem");
  const chips = within(main.getByRole("group", { name: "Playoff Race" }));
  return { main, rows, chips };
}

/* The visible text of a row head: the place, the team name, and the playoff odds. */
const headOf = (row: HTMLElement) => within(row).getAllByRole("button")[0];

describe("generateStaticParams", () => {
  it("lists the latest season when the managers file exists", async () => {
    const { generateStaticParams } = await routeOver(fixture);
    expect(generateStaticParams()).toEqual([{ season: "2026" }]);
  });

  it("lists no season when the managers file is missing", async () => {
    const { generateStaticParams } = await routeOver();
    expect(generateStaticParams()).toEqual([]);
  });
});

describe("ManagersIndex", () => {
  it("names the race groups with the id that the playoff race Answer of the front door links to", async () => {
    const { main } = await indexOfClient("cpc");
    expect(main.getByRole("group", { name: "Playoff Race" }).id).toBe("race");
  });

  it("has the managers title", async () => {
    const { metadata } = await routeOver(fixture);
    expect(metadata.title).toBe("Managers · Cornerstone Fantasy Football League");
  });

  it("lists the twelve teams of CPC week 8 in power-ranking order, each with its place, avatar, name, and odds", async () => {
    const { rows } = await indexOfClient("cpc");
    expect(rows().map((row) => headOf(row).textContent)).toEqual([
      "1All You Need Is Love81%",
      "2Teehee61%",
      "3Maye d'force B with U77%",
      "4Return of T Mac42%",
      "5The Blue Tent75%",
      "6Lil Fridge86%",
      "7Bo Girds76%",
      "8London Cooking83%",
      "9To Infinity and Bijan7%",
      "10Unsolicited Dak Picks8%",
      "11behold the lamb4%",
      "12NFC Least1%",
    ]);
    // Each row shows the small avatar of its team, and the row adds nothing more: no letter, no record, no link.
    const blueTent = rows()[4];
    // The avatar is decorative, with an empty alt, because the name sits next to it.
    expect(headOf(blueTent).querySelector("img")?.getAttribute("src")).toMatch(/avatars\/1\./);
    expect(within(blueTent).queryByRole("link")).toBeNull();
  });

  it("shows the chips All 12, In 6, Bubble 2, and Out 4 for CPC week 8, with All pressed", async () => {
    const { chips } = await indexOfClient("cpc");
    expect(chips.getAllByRole("button").map((chip) => [chip.textContent, chip.getAttribute("aria-pressed")])).toEqual([
      ["All12", "true"],
      ["In6", "false"],
      ["Bubble2", "false"],
      ["Out4", "false"],
    ]);
  });

  it("shows only Teehee and Return of T Mac after a tap on Bubble, and all twelve after a second tap", async () => {
    const { rows, chips } = await indexOfClient("cpc");
    const bubble = chips.getByRole("button", { name: /Bubble/ });
    fireEvent.click(bubble);
    expect(bubble.getAttribute("aria-pressed")).toBe("true");
    expect(rows().map((row) => headOf(row).textContent)).toEqual(["2Teehee61%", "4Return of T Mac42%"]);
    // A tap on the pressed chip clears the filter, so All is pressed again.
    fireEvent.click(bubble);
    expect(chips.getByRole("button", { name: /All/ }).getAttribute("aria-pressed")).toBe("true");
    expect(rows()).toHaveLength(12);
  });

  it("opens The Blue Tent in place with A, the grade read, four arcs, and its link, then a tap on Lil Fridge swaps the open row", async () => {
    const { rows } = await indexOfClient("cpc");
    const blueTent = headOf(rows()[4]);
    const lilFridge = headOf(rows()[5]);
    fireEvent.click(blueTent);
    expect(blueTent.getAttribute("aria-expanded")).toBe("true");
    const panel = within(document.getElementById(blueTent.getAttribute("aria-controls")!)!);
    expect(panel.getByLabelText("Grade A").textContent).toBe("A");
    expect(panel.getByText("Strong at QB and TE. Soft at RB.")).toBeTruthy();
    expect(panel.getByText("9-7 · Power #5 · 75% playoff")).toBeTruthy();
    const arcs = within(panel.getByRole("list", { name: "Grade Dial" })).getAllByRole("img");
    expect(arcs.map((arc) => arc.getAttribute("aria-label"))).toEqual([
      "Projection Ahead: 4th of 12, 45% of the grade",
      "Season Production: 6th of 12, 30% of the grade",
      "Trade Value: 7th of 12, 10% of the grade",
      "Depth And Holes: 7th of 12, 15% of the grade",
    ]);
    const link = panel.getByRole("link");
    expect(link.textContent).toBe("Manager page of The Blue Tent");
    expect(link.getAttribute("href")).toBe("/2026/managers/1/");
    // One row is open at a time, so the tap on Lil Fridge closes The Blue Tent.
    fireEvent.click(lilFridge);
    expect(lilFridge.getAttribute("aria-expanded")).toBe("true");
    expect(blueTent.getAttribute("aria-expanded")).toBe("false");
    expect(rows().filter((row) => row.getAttribute("data-open") === "true")).toHaveLength(1);
  });

  it("shows the first row in the stage, then The Blue Tent on a hover and Lil Fridge on a focus, in the six hero slots", async () => {
    const { main, rows } = await indexOfClient("cpc");
    const stage = () => main.getByRole("region", { name: /^Stage: / });
    const slot = (name: string) => stage().querySelector(`[data-hero-slot="${name}"]`);
    expect(stage().getAttribute("aria-label")).toBe("Stage: All You Need Is Love");
    fireEvent.pointerEnter(rows()[4]);
    expect(stage().getAttribute("aria-label")).toBe("Stage: The Blue Tent");
    expect(slot("eyebrow")?.textContent).toBe("In");
    expect(slot("title")?.textContent).toBe("The Blue Tent");
    expect(slot("meta")?.textContent).toBe("9-7 · Power #5 · 75% playoff");
    const arcs = within(within(slot("feature") as HTMLElement).getByRole("list", { name: "Grade Dial" })).getAllByRole("img");
    expect(arcs).toHaveLength(4);
    expect(within(slot("stats") as HTMLElement).getByText("A")).toBeTruthy();
    const link = within(slot("action") as HTMLElement).getByRole("link");
    expect(link.textContent).toBe("Manager page of The Blue Tent");
    expect(link.getAttribute("href")).toBe("/2026/managers/1/");
    fireEvent.focus(headOf(rows()[5]));
    expect(stage().getAttribute("aria-label")).toBe("Stage: Lil Fridge");
    expect(stage().querySelector('[data-hero-slot="title"]')?.textContent).toBe("Lil Fridge");
  });

  it("hides the stage under the desktop tier, so a phone and a tablet show only the ledger", async () => {
    const { main } = await indexOfClient("cpc");
    const stage = main.getByRole("region", { name: /^Stage: / });
    // The stage box is display none under the desktop tier. jsdom reads no media query, so the check reads the classes.
    const box = stage.closest("[data-ix-stage]")!;
    expect(box.className).toMatch(/(^|\s)hidden(\s|$)/);
    expect(box.className).toMatch(/(^|\s)desktop:block(\s|$)/);
  });

  it("shows the chips All 12, In 4, Bubble 5, and Out 3 for NorCal week 8, with Mitseeker5000 first", async () => {
    const { rows, chips } = await indexOfClient("norcal");
    expect(chips.getAllByRole("button").map((chip) => chip.textContent)).toEqual(["All12", "In4", "Bubble5", "Out3"]);
    expect(headOf(rows()[0]).textContent).toBe("1Mitseeker500097%");
  });

  it("marks the managers entry of the menu as the open page", async () => {
    const { default: ManagersPage } = await routeOver(fixture);
    render(await ManagersPage({ params: Promise.resolve({ season: "2026" }) }));
    const row = screen.getByRole("navigation", { name: "Site menu" });
    expect(within(row).getByRole("link", { name: "Managers" }).getAttribute("aria-current")).toBe("page");
  });
});
