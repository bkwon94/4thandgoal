/**
 * Tests for the shell: the top band, the pill bar, the dock, the week chip with the strip of weeks, the theme button, and the
 * header sheet of the front door.
 * They read what a reader sees by role and name, not the class names.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import type { Brand, SiteMenu } from "./nav";
import { TopBand } from "./top-band";

/* The brand of a build with no base path. */
const BRAND: Brand = { home: "/", logo: "/brand/logo.png" };

const TITLE = "Cornerstone Fantasy Football League";

/* The menu of CPC in week 8: five destinations, and the three published weeks, newest first. */
const MENU: SiteMenu = {
  items: [
    { kind: "home", label: "Home", short: "Home", href: "/" },
    { kind: "week", label: "Week 8", short: "Week 8", href: "/2026/week-08/" },
    { kind: "rankings", label: "Power Rankings", short: "Rankings", href: "/rankings/" },
    { kind: "managers", label: "Managers", short: "Managers", href: "/2026/managers/" },
    { kind: "analyzer", label: "Trade Analyzer", short: "Trade", href: "/analyze/" },
  ],
  weeks: [
    { number: 8, href: "/2026/week-08/" },
    { number: 7, href: "/2026/week-07/" },
    { number: 6, href: "/2026/week-06/" },
  ],
};

function renderBand(pageHref?: string, menu: SiteMenu = MENU) {
  render(<TopBand title={TITLE} brand={BRAND} menu={menu} pageHref={pageHref} />);
}

/* The label and the href of each link in a part of the page, in order. */
function linksIn(element: HTMLElement) {
  return within(element)
    .getAllByRole("link")
    .map((link) => [link.textContent, link.getAttribute("href")]);
}

function current(element: HTMLElement) {
  return within(element)
    .getAllByRole("link")
    .filter((link) => link.getAttribute("aria-current") === "page")
    .map((link) => link.textContent);
}

/* The week chip. The closed strip still holds a link with the same text, so the query names the summary of the chip. */
const chip = (label: string) => screen.getByText(label, { selector: "summary" });
const stripOpen = (label: string) => (chip(label).closest("details") as HTMLDetailsElement).open;

const pillBar = () => screen.getByRole("navigation", { name: "Site menu" });
const dock = () => screen.getByRole("navigation", { name: "Bottom menu" });

/* jsdom has no matchMedia, and Framer Motion reads it. The stub matches no query. */
vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList,
);

afterEach(() => cleanup());
afterAll(() => vi.unstubAllGlobals());

describe("TopBand", () => {
  it("shows the brand mark as the home link, named by the title", () => {
    renderBand("/");
    const home = within(screen.getByRole("banner")).getByRole("link", { name: TITLE });
    expect(home.getAttribute("href")).toBe("/");
    expect(within(home).getByRole("presentation", { hidden: true }).getAttribute("src")).toBe("/brand/logo.png");
  });

  it("shows the title as the brand mark when the brand has no logo", () => {
    render(<TopBand title="NorCal Apex 6" brand={{ home: "/", logo: null }} menu={MENU} />);
    const home = screen.getByRole("link", { name: "NorCal Apex 6" });
    expect(within(home).queryByRole("presentation", { hidden: true })).toBeNull();
  });

  it("holds the theme button in the banner", () => {
    renderBand("/");
    expect(within(screen.getByRole("banner")).getByRole("button", { name: /Switch to (light|dark) theme/ })).toBeTruthy();
  });

  it("holds the actions of the app just before the theme button, and the dock keeps its five items", () => {
    render(<TopBand title={TITLE} brand={BRAND} menu={MENU} pageHref="/" actions={<a href="/eggs/">Egg board</a>} />);
    const band = screen.getByRole("banner");
    const action = within(band).getByRole("link", { name: "Egg board" });
    const theme = within(band).getByRole("button", { name: /Switch to (light|dark) theme/ });
    expect(action.compareDocumentPosition(theme) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(action.parentElement).toBe(theme.parentElement);
    expect(within(screen.getByRole("navigation", { name: "Bottom menu" })).getAllByRole("link")).toHaveLength(5);
  });
});

describe("The pill bar (AT-10)", () => {
  it("lists every destination with its full label, in the order of the menu", () => {
    renderBand("/");
    expect(linksIn(pillBar())).toEqual([
      ["Home", "/"],
      ["Week 8", "/2026/week-08/"],
      ["Power Rankings", "/rankings/"],
      ["Managers", "/2026/managers/"],
      ["Trade Analyzer", "/analyze/"],
    ]);
  });

  it("sits in the top band", () => {
    renderBand("/");
    expect(screen.getByRole("banner").contains(pillBar())).toBe(true);
  });

  it("marks the open destination as the current page", () => {
    renderBand("/rankings/");
    expect(current(pillBar())).toEqual(["Power Rankings"]);
  });
});

describe("The dock (AT-9)", () => {
  it("lists Home, Week N, Rankings, Managers, and Trade, each with an icon", () => {
    renderBand("/");
    const links = within(dock()).getAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual(["Home", "Week 8", "Rankings", "Managers", "Trade"]);
    for (const link of links) expect(link.querySelector("svg")).not.toBeNull();
  });

  it("leaves out the midseason report, so five items share the width of a phone", () => {
    const items: SiteMenu["items"] = [
      ...MENU.items,
      { kind: "midseason", label: "Midseason Report", short: "Report", href: "/midseason/2026/" },
    ];
    renderBand("/", { ...MENU, items });
    expect(within(pillBar()).getAllByRole("link").map((link) => link.textContent)).toContain("Midseason Report");
    expect(within(dock()).getAllByRole("link").map((link) => link.textContent)).toEqual(["Home", "Week 8", "Rankings", "Managers", "Trade"]);
  });

  it("sits outside the top band, so it stays at the bottom of the viewport", () => {
    renderBand("/");
    expect(screen.getByRole("banner").contains(dock())).toBe(false);
  });

  it("marks the week of the open week page", () => {
    renderBand("/2026/week-08/");
    expect(current(dock())).toEqual(["Week 8"]);
  });

  it("marks the week item on the page of an older week too", () => {
    renderBand("/2026/week-07/");
    expect(current(dock())).toEqual(["Week 8"]);
  });

  it("marks Managers on the page of one manager", () => {
    renderBand("/2026/managers/6/");
    expect(current(dock())).toEqual(["Managers"]);
  });

  it("marks no item on a page that is no destination, such as the 404 page", () => {
    renderBand(undefined);
    expect(current(dock())).toEqual([]);
  });
});

describe("The week chip (AT-11)", () => {
  it("reads WK 08 on a page that is not a week page, the latest week", () => {
    renderBand("/");
    expect(chip("WK 08")).toBeTruthy();
  });

  it("reads the week of the open week page", () => {
    renderBand("/2026/week-07/");
    expect(chip("WK 07")).toBeTruthy();
  });

  it("opens the strip of weeks on a tap, oldest first, with the chip week marked", () => {
    renderBand("/");
    expect(stripOpen("WK 08")).toBe(false);
    fireEvent.click(chip("WK 08"));
    expect(stripOpen("WK 08")).toBe(true);
    const strip = screen.getByRole("navigation", { name: "Weeks of the season" });
    expect(linksIn(strip)).toEqual([
      ["WK 06", "/2026/week-06/"],
      ["WK 07", "/2026/week-07/"],
      ["WK 08", "/2026/week-08/"],
    ]);
    expect(within(strip).getByRole("link", { name: "WK 08" }).getAttribute("aria-current")).toBe("true");
  });

  it("closes the strip on Escape", () => {
    renderBand("/");
    fireEvent.click(chip("WK 08"));
    fireEvent.keyDown(document, { key: "Escape" });
    expect(stripOpen("WK 08")).toBe(false);
  });

  it("closes the strip on a tap outside it", () => {
    renderBand("/");
    fireEvent.click(chip("WK 08"));
    fireEvent.pointerDown(document.body);
    expect(stripOpen("WK 08")).toBe(false);
  });

  it("shows no chip for a client with no published week", () => {
    renderBand("/", { ...MENU, weeks: [] });
    expect(screen.queryByText(/^WK /)).toBeNull();
  });
});

/* The top band of the front door: the header sheet in place of the dock and the week chip (decision 10). */
function renderDoorBand(pageHref = "/", menu: SiteMenu = MENU) {
  render(<TopBand title={TITLE} brand={BRAND} menu={menu} pageHref={pageHref} nav="sheet" />);
}

const menuButton = () => within(screen.getByRole("banner")).getByRole("button", { name: /^(Open|Close) the menu$/ });
const sheet = () => screen.getByRole("navigation", { name: "Pages" });

describe("The header sheet of the front door (AT-45, AT-47)", () => {
  it("shows no dock and no week chip, and holds the menu button in the banner", () => {
    renderDoorBand();
    expect(screen.queryByRole("navigation", { name: "Bottom menu", hidden: true })).toBeNull();
    expect(screen.queryByText(/^WK /, { selector: "summary" })).toBeNull();
    expect(menuButton().getAttribute("aria-expanded")).toBe("false");
  });

  it("keeps the sheet closed and out of the accessibility tree until the button opens it", () => {
    renderDoorBand();
    expect(screen.queryByRole("navigation", { name: "Pages" })).toBeNull();
  });

  it("opens the sheet with one row per page, each with an icon, its name, and its note, and a check on the open page", () => {
    renderDoorBand("/");
    fireEvent.click(menuButton());
    const rows = within(sheet()).getAllByRole("link").filter((link) => !/^WK /.test(link.textContent ?? ""));
    expect(rows.map((row) => [row.textContent, row.getAttribute("href")])).toEqual([
      ["HomeAsk about your team", "/"],
      ["Week 8Scores and recaps", "/2026/week-08/"],
      ["Power RankingsThe league, ranked", "/rankings/"],
      ["ManagersGrades and records", "/2026/managers/"],
      ["Trade AnalyzerCheck a trade", "/analyze/"],
    ]);
    for (const row of rows) expect(row.querySelector("svg")).not.toBeNull();
    expect(current(sheet())).toEqual(["HomeAsk about your team"]);
    expect(within(sheet()).getByRole("link", { current: "page" }).querySelector("[data-check]")).not.toBeNull();
    expect(within(sheet()).getAllByRole("link").filter((link) => link.querySelector("[data-check]"))).toHaveLength(1);
  });

  it("turns the button into the close button while the sheet is open", () => {
    renderDoorBand();
    fireEvent.click(menuButton());
    expect(menuButton().getAttribute("aria-expanded")).toBe("true");
    expect(menuButton().getAttribute("aria-label")).toBe("Close the menu");
  });

  it("moves the focus to the sheet on open", () => {
    renderDoorBand();
    fireEvent.click(menuButton());
    expect(sheet().contains(document.activeElement)).toBe(true);
  });

  it("marks no row on a page that is no destination, such as /ask/", () => {
    renderDoorBand("/ask/");
    fireEvent.click(menuButton());
    expect(current(sheet())).toEqual([]);
    expect(sheet().querySelector("[data-check]")).toBeNull();
  });

  it("opens the latest report from the week row, and lists every week under Past weeks", () => {
    renderDoorBand("/");
    fireEvent.click(menuButton());
    expect(within(sheet()).getByRole("link", { name: /^Week 8/ }).getAttribute("href")).toBe("/2026/week-08/");
    const past = within(sheet()).getByRole("button", { name: "Past weeks" });
    expect(past.getAttribute("aria-expanded")).toBe("false");
    expect(within(sheet()).queryByRole("link", { name: "WK 07" })).toBeNull();
    fireEvent.click(past);
    expect(past.getAttribute("aria-expanded")).toBe("true");
    const weeks = screen.getByRole("list", { name: "Past weeks" });
    expect(linksIn(weeks)).toEqual([
      ["WK 08", "/2026/week-08/"],
      ["WK 07", "/2026/week-07/"],
      ["WK 06", "/2026/week-06/"],
    ]);
  });

  it("shows no Past weeks for a client with no published week", () => {
    renderDoorBand("/", { items: MENU.items.filter((item) => item.kind !== "week"), weeks: [] });
    fireEvent.click(menuButton());
    expect(within(sheet()).queryByRole("button", { name: "Past weeks" })).toBeNull();
  });

  it("keeps the pill bar in the banner, so the desktop shows the pages inline (AT-50)", () => {
    renderDoorBand("/");
    expect(screen.getByRole("banner").contains(pillBar())).toBe(true);
    expect(linksIn(pillBar())).toHaveLength(5);
  });
});

describe("The header sheet closes four ways (AT-46)", () => {
  function openSheet() {
    renderDoorBand();
    fireEvent.click(menuButton());
    expect(sheet()).toBeTruthy();
  }

  function expectClosed() {
    expect(screen.queryByRole("navigation", { name: "Pages" })).toBeNull();
    expect(menuButton().getAttribute("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(menuButton());
  }

  it("closes by the X", () => {
    openSheet();
    fireEvent.click(menuButton());
    expectClosed();
  });

  it("closes by a tap on the dimmed page", () => {
    openSheet();
    fireEvent.click(screen.getByTestId("menu-scrim"));
    expectClosed();
  });

  it("closes by Escape", () => {
    openSheet();
    fireEvent.keyDown(document, { key: "Escape" });
    expectClosed();
  });

  it("closes by a swipe up", () => {
    openSheet();
    const panel = sheet();
    fireEvent.pointerDown(panel, { pointerId: 1, clientY: 300, pointerType: "touch", isPrimary: true });
    fireEvent.pointerMove(panel, { pointerId: 1, clientY: 240, pointerType: "touch", isPrimary: true });
    fireEvent.pointerMove(panel, { pointerId: 1, clientY: 180, pointerType: "touch", isPrimary: true });
    fireEvent.pointerUp(panel, { pointerId: 1, clientY: 180, pointerType: "touch", isPrimary: true });
    expectClosed();
  });

  it("closes when a Tab moves the focus out of the sheet, and leaves the focus where it went", () => {
    render(
      <>
        <TopBand title={TITLE} brand={BRAND} menu={MENU} pageHref="/" nav="sheet" />
        <button type="button">After</button>
      </>,
    );
    fireEvent.click(menuButton());
    const after = screen.getByRole("button", { name: "After" });
    fireEvent.blur(sheet(), { relatedTarget: after });
    expect(screen.queryByRole("navigation", { name: "Pages" })).toBeNull();
  });

  it("stays open after a short drag that does not reach the line of a close", () => {
    openSheet();
    const panel = sheet();
    fireEvent.pointerDown(panel, { pointerId: 1, clientY: 300, pointerType: "touch", isPrimary: true, timeStamp: 0 });
    fireEvent.pointerMove(panel, { pointerId: 1, clientY: 296, pointerType: "touch", isPrimary: true });
    fireEvent.pointerUp(panel, { pointerId: 1, clientY: 296, pointerType: "touch", isPrimary: true });
    expect(sheet()).toBeTruthy();
  });
});
