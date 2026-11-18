/**
 * Tests for the pages of the Site answer: the real Menu and the real menu links of the cpc build, with no Home, plus the
 * midseason report and the sim. A Menu link of the sim wins over the sim section of the report (AT-19). NorCal reads its own client.toml.
 */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "smol-toml";
import { cleanup, render, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fixturePublished, readFixtureSite } from "@/fixtures/sites";
import type { MenuItem, PackageName } from "@/lib/client-values";
import { clientValues } from "@/generated/client-values";
import { menuLinks, siteLines } from "@/generated/registry";
import { SiteAnswer } from "./front-door/site-answer";
import { sitePages } from "./site-pages";

await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));
afterEach(() => cleanup());

const { items } = clientValues.menu;

describe("the pages of the Site answer", () => {
  it("marks the analyzer and the sim as Tools, and each other page as a page to read", () => {
    const pages = sitePages(items, menuLinks, siteLines, clientValues.packages);
    expect(pages.filter((page) => page.tool).map((page) => page.label)).toEqual(["Trade Analyzer", "Playoff Sim"]);
    expect(pages.filter((page) => !page.tool).map((page) => page.label)).toEqual(["Week 8", "Power Rankings", "Managers", "Midseason Report"]);
  });

  it("gives the sim its own Menu link over the sim section of the midseason report (AT-19)", () => {
    const links = { ...menuLinks, sim: () => ({ label: "Playoff Sim", href: "/sim/2026/" }) };
    const pages = sitePages(items, links, siteLines, clientValues.packages);
    expect(pages.find((page) => page.key === "sim")?.href).toBe("/sim/2026/");
    const { container } = render(<SiteAnswer question="how do I use the sim" page="sim" pages={pages} />);
    expect(within(container).getByRole("link", { name: "Open the Playoff Sim" }).getAttribute("href")).toBe("/sim/2026/");
  });

  it("shows the sim with no Menu link only when the client has both the sim and the midseason packages", () => {
    const keys = (packages: PackageName[]) => sitePages(items, menuLinks, siteLines, packages).map((page) => page.key);
    expect(keys(clientValues.packages)).toContain("sim");
    expect(keys(clientValues.packages.filter((name) => name !== "midseason"))).not.toContain("sim");
    expect(keys(clientValues.packages.filter((name) => name !== "sim"))).not.toContain("sim");
  });

  it("shows the sim with its Menu link for a client with the sim package and no midseason package", () => {
    const links = { ...menuLinks, sim: () => ({ label: "Playoff Sim", href: "/sim/2026/" }) };
    const pages = sitePages(items, links, siteLines, clientValues.packages.filter((name) => name !== "midseason"));
    expect(pages.map((page) => [page.key, page.href])).toContainEqual(["sim", "/sim/2026/"]);
    expect(pages.map((page) => page.key)).not.toContain("midseason");
  });

  it("drops the midseason report and the sim for a client with no midseason package", () => {
    const pages = sitePages(items, menuLinks, siteLines, clientValues.packages.filter((name) => name !== "midseason"));
    expect(pages.map((page) => page.key)).toEqual(["week", "rankings", "managers", "analyzer"]);
  });
});

/* The repo root, four folders above this file. */
const REPO = join(__dirname, "..", "..", "..", "..");

/* The package list and the Menu of the real client.toml of NorCal. With the front door on, the Menu is front_door_items. */
function norcalMenu(): { packages: PackageName[]; items: MenuItem[] } {
  const values = parse(readFileSync(join(REPO, "clients", "norcal", "client.toml"), "utf8")) as {
    packages: PackageName[];
    front_door: boolean;
    menu: { items?: MenuItem[]; front_door_items?: MenuItem[] };
  };
  const items = values.front_door ? (values.menu.front_door_items ?? values.menu.items) : values.menu.items;
  return { packages: values.packages, items: items ?? [] };
}

describe("the list view of NorCal (AT-13)", () => {
  it("holds only the pages of the NorCal Menu, plus its report and its sim, and each link opens a NorCal page", async () => {
    readFixtureSite("norcal");
    // The readers of public/ read the working folder when they load, so reset them to read the NorCal data.
    vi.resetModules();
    const { sitePages: pagesOf } = await import("./site-pages");
    const { menuLinks: links, siteLines: lines } = await import("@/generated/registry");
    const { SiteAnswer: Answer } = await import("./front-door/site-answer");
    const { packages, items: menu } = norcalMenu();
    const pages = pagesOf(menu, links, lines, packages);
    const { container } = render(<Answer question="what tools are there" page="all" pages={pages} />);
    const hrefs = (group: string) => within(within(container).getByRole("list", { name: group })).getAllByRole("link").map((tile) => tile.getAttribute("href"));
    expect(container.textContent).toContain("The site has 2 tools and 4 pages to read.");
    expect(hrefs("Tools")).toEqual(["/analyze/", "/midseason/2026/#sim"]);
    expect(hrefs("Pages to read")).toEqual(["/2026/week-08/", "/rankings/", "/2026/managers/", "/midseason/2026/"]);
    // Each link opens a page that the NorCal export holds: a published file of NorCal, or a route of the site.
    const proof: Record<string, string> = {
      "/2026/week-08/": fixturePublished("norcal", "2026", "week-08", "page.json"),
      "/rankings/": fixturePublished("norcal", "2026", "rankings.json"),
      "/2026/managers/": fixturePublished("norcal", "2026", "managers.json"),
      "/analyze/": join(__dirname, "(client)", "analyze", "page.tsx"),
      "/midseason/2026/": fixturePublished("norcal", "2026", "midseason.json"),
      "/midseason/2026/#sim": fixturePublished("norcal", "2026", "sim.json"),
    };
    for (const href of [...hrefs("Tools"), ...hrefs("Pages to read")]) expect(existsSync(proof[href!]), href!).toBe(true);
    // The week label comes from the NorCal data, and no page of a package outside NorCal shows.
    expect(container.textContent).toContain("Week 8");
    expect(container.textContent).not.toMatch(/Egg/);
  });
});
