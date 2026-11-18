/**
 * Tests for the pages of the Site answer: the real Menu and the real menu links of the cpc build, with no Home, plus the
 * midseason report and the sim. A Menu link of the sim wins over the sim section of the report (AT-19).
 */
import { cleanup, render, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
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

  it("drops the midseason report and the sim for a client with no midseason package", () => {
    const pages = sitePages(items, menuLinks, siteLines, clientValues.packages.filter((name) => name !== "midseason"));
    expect(pages.map((page) => page.key)).toEqual(["week", "rankings", "managers", "analyzer"]);
  });
});
