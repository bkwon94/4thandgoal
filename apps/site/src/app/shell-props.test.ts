/**
 * Tests for the shell props: the menu items of client.toml become the destinations of the menu, in order.
 * One test reads the real generated client values of cpc and the real published weeks.
 */
import { describe, expect, it } from "vitest";
import type { MenuLinks } from "@/lib/client-values";
import { shellProps, menuPages, pageTitle } from "./shell-props";

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
      { kind: "analyzer", label: "Trade Analyzer", short: "Trade", href: "/analyze/" },
      { kind: "home", label: "Home", short: "Home", href: "/" },
      { kind: "week", label: "Week 7", short: "Week 7", href: "/2026/week-07/" },
    ]);
  });

  it("gives no destination for the sim, so the menu keeps its items", () => {
    const links = { ...LINKS, sim: () => ({ label: "Sim", href: "/sim/" }) };
    const pages = menuPages([{ page: "home" }, { package: "sim" }], links, "/");
    expect(pages.map((page) => page.kind)).toEqual(["home"]);
  });

  it("lists the midseason report with the label of its item and the short label Report (AT-46)", () => {
    const links = { ...LINKS, midseason: () => ({ label: "Midseason Report", href: "/midseason/2026/" }) };
    const pages = menuPages([{ package: "rankings" }, { package: "midseason", label: "Midseason Report" }], links, "/");
    expect(pages.at(-1)).toEqual({ kind: "midseason", label: "Midseason Report", short: "Report", href: "/midseason/2026/" });
  });

  it("lists no report when the season has no report", () => {
    const links = { ...LINKS, midseason: () => null };
    expect(menuPages([{ package: "midseason" }], links, "/")).toEqual([]);
  });

  it("takes the label of an item in place of the label of the package, in the pill bar only", () => {
    const pages = menuPages([{ page: "home", label: "Start" }, { package: "analyzer", label: "Trades" }], LINKS, "/");
    expect(pages.map((page) => page.label)).toEqual(["Start", "Trades"]);
    // The dock keeps the short label of the look, so five items fit the width of a phone.
    expect(pages.map((page) => page.short)).toEqual(["Home", "Trade"]);
  });

  it("lists the waiver page after the trade analyzer when the items put it there", () => {
    const pages = menuPages([{ package: "analyzer" }, { package: "waiver" }], LINKS, "/");
    expect(pages).toEqual([
      { kind: "analyzer", label: "Trade Analyzer", short: "Trade", href: "/analyze/" },
      { kind: "waiver", label: "Waiver Wire", short: "Waiver", href: "/2026/week-07/waiver/" },
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

describe("shellProps of cpc", () => {
  it("keeps the items and the labels of the CPC menu, with the short labels of the dock (AT-9, AT-10)", () => {
    const { menu } = shellProps();
    expect(menu.items.map((item) => item.label)).toEqual(["Home", "Week 8", "Power Rankings", "Managers", "Trade Analyzer"]);
    expect(menu.items.map((item) => item.short)).toEqual(["Home", "Week 8", "Rankings", "Managers", "Trade"]);
  });

  it("lists every published week, newest first, for the week chip and the strip (AT-11)", () => {
    expect(shellProps().menu.weeks).toEqual([
      { number: 8, href: "/2026/week-08/" },
      { number: 7, href: "/2026/week-07/" },
      { number: 6, href: "/2026/week-06/" },
    ]);
  });

  it("takes the top band text of copy.toml and the CPC logo", () => {
    const { title, brand } = shellProps();
    expect(title).toBe("Cornerstone Fantasy Football League");
    expect(brand).toEqual({ home: "/", logo: "/brand/logo.png" });
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
