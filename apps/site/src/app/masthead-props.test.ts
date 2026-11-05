/**
 * Tests for the masthead props: the menu items of client.toml become the destinations of the menu, in order.
 * One test reads the real generated client values of cpc and the real published weeks.
 */
import { describe, expect, it } from "vitest";
import type { MenuLinks } from "@/lib/client-values";
import { mastheadProps, menuPages, pageTitle } from "./masthead-props";

/* The menu links of a client that takes each package, as the registry gives them. */
const LINKS: MenuLinks = {
  week: () => ({ label: "Week 7", href: "/2026/week-07/" }),
  rankings: () => ({ label: "Power Rankings", href: "/rankings/" }),
  managers: () => ({ label: "Managers", href: "/2026/managers/" }),
  analyzer: () => ({ label: "Trade Analyzer", href: "/analyze/" }),
  waiver: () => ({ label: "Waiver Wire", href: "/2026/week-07/waiver/" }),
};

describe("menuPages", () => {
  it("gives one destination per item, in the order of the items", () => {
    const pages = menuPages([{ package: "analyzer" }, { page: "home" }, { package: "week" }], LINKS, "/");
    expect(pages).toEqual([
      { label: "Trade Analyzer", href: "/analyze/" },
      { label: "Home", href: "/" },
      { label: "Week 7", href: "/2026/week-07/" },
    ]);
  });

  it("takes the label of an item in place of the label of the package", () => {
    const pages = menuPages([{ page: "home", label: "Start" }, { package: "rankings", label: "Rankings" }], LINKS, "/");
    expect(pages.map((page) => page.label)).toEqual(["Start", "Rankings"]);
  });

  it("lists the waiver page after the trade analyzer when the items put it there", () => {
    const pages = menuPages([{ package: "analyzer" }, { package: "waiver" }], LINKS, "/");
    expect(pages).toEqual([
      { label: "Trade Analyzer", href: "/analyze/" },
      { label: "Waiver Wire", href: "/2026/week-07/waiver/" },
    ]);
  });

  it("lists no page of a package that the registry omits", () => {
    const { rankings: _rankings, analyzer: _analyzer, ...rest } = LINKS;
    const pages = menuPages([{ package: "week" }, { package: "rankings" }, { package: "analyzer" }], rest, "/");
    expect(pages.map((page) => page.label)).toEqual(["Week 7"]);
  });

  it("lists no page of a package with no page to link yet, such as managers with no managers file", () => {
    const pages = menuPages([{ package: "rankings" }, { package: "managers" }], { ...LINKS, managers: () => null }, "/");
    expect(pages.map((page) => page.label)).toEqual(["Power Rankings"]);
  });
});

describe("mastheadProps of cpc", () => {
  it("keeps the hamburger, the items, and the labels of the CPC menu", () => {
    const { menu } = mastheadProps();
    expect(menu.layout).toBe("hamburger");
    expect(menu.pages.map((page) => page.label)).toEqual([
      "Home",
      "Week 8",
      "Power Rankings",
      "Managers",
      "Trade Analyzer",
    ]);
    expect(menu.pastWeeks.map((page) => page.label)).toEqual(["Week 7", "Week 6"]);
  });

  it("takes the masthead text of copy.toml, the CPC logo, and the theme button of a two-set brand (AT-5)", () => {
    const { title, brand } = mastheadProps();
    expect(title).toBe("Cornerstone Fantasy Football League");
    expect(brand).toEqual({ home: "/", logo: "/brand/logo.png", themeButton: true });
  });
});

describe("pageTitle", () => {
  const NORCAL = { siteName: "NorCal Apex 6", masthead: "NorCal Apex 6", tagline: "League Weekly" };

  it("gives the site name of copy.toml alone for the home page", () => {
    expect(pageTitle(NORCAL)).toBe("NorCal Apex 6");
  });

  it("puts the page name before the site name of copy.toml", () => {
    expect(pageTitle(NORCAL, "Trade Analyzer")).toBe("Trade Analyzer · NorCal Apex 6");
  });

  it("reads the CPC site name from the generated client values by default", () => {
    expect(pageTitle(undefined, "Week 8")).toBe("Week 8 · Cornerstone Fantasy Football League");
  });
});
