/**
 * Tests for the shell: the top band, the pill bar, the theme button, and the
 * menu sheet of every page.
 * They read what a reader sees by role and name, not the class names.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, spyOn } from "bun:test";
import type { Brand, SiteMenu } from "./nav";
import { TopBand } from "./top-band";
// The jsdom stand-ins that the Drawer of the menu sheet needs.
import "../ui/sheet-jsdom";

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

const pillBar = () => screen.getByRole("navigation", { name: "Site menu" });

/* Framer Motion reads matchMedia. The stub matches no query, so each test sees a phone with motion on. The preload
   restores each spy after each test, so each test sets the stub again. */
const noMatch = (query: string) =>
  ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }) as unknown as MediaQueryList;

beforeEach(() => {
  spyOn(window, "matchMedia").mockImplementation(noMatch);
});

afterEach(() => cleanup());

describe("TopBand", () => {
  it("shows the brand mark as the home link, named by the title", () => {
    renderBand("/");
    const home = within(screen.getByRole("banner")).getByRole("link", { name: TITLE });
    expect(home.getAttribute("href")).toBe("/");
    expect(within(home).getByRole("presentation", { hidden: true }).getAttribute("src")).toBe(
      "/brand/logo.png",
    );
  });

  it("shows the title as the brand mark when the brand has no logo", () => {
    render(<TopBand title="NorCal Apex 6" brand={{ home: "/", logo: null }} menu={MENU} />);
    const home = screen.getByRole("link", { name: "NorCal Apex 6" });
    expect(within(home).queryByRole("presentation", { hidden: true })).toBeNull();
  });

  it("holds the strip of the app under the row of the band, inside the banner, so it stays on screen too", () => {
    render(
      <TopBand
        title={TITLE}
        brand={BRAND}
        menu={MENU}
        pageHref="/"
        strip={<button type="button">Open the Trade Wire</button>}
      />,
    );
    const band = screen.getByRole("banner");
    const strip = within(band).getByRole("button", { name: "Open the Trade Wire" });
    const theme = within(band).getByRole("button", { name: /Switch to (light|dark) theme/ });
    expect(theme.compareDocumentPosition(strip) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(strip.parentElement).toBe(band);
  });

  it("holds the theme button in the banner", () => {
    renderBand("/");
    expect(
      within(screen.getByRole("banner")).getByRole("button", {
        name: /Switch to (light|dark) theme/,
      }),
    ).toBeTruthy();
  });

  it("holds the actions of the app just before the theme button, and the sheet keeps its five items", () => {
    render(
      <TopBand
        title={TITLE}
        brand={BRAND}
        menu={MENU}
        pageHref="/"
        actions={<a href="/eggs/">Egg board</a>}
      />,
    );
    const band = screen.getByRole("banner");
    const action = within(band).getByRole("link", { name: "Egg board" });
    const theme = within(band).getByRole("button", { name: /Switch to (light|dark) theme/ });
    expect(action.compareDocumentPosition(theme) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(action.parentElement).toBe(theme.parentElement);
    fireEvent.click(menuButton());
    expect(
      within(sheet())
        .getAllByRole("link")
        .filter((link) => !/^WK /.test(link.textContent ?? "")),
    ).toHaveLength(5);
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

describe("The menu sheet of every page (AT-9)", () => {
  it("leaves out the midseason report, so the sheet lists the five destinations of the dock", () => {
    const items: SiteMenu["items"] = [
      ...MENU.items,
      { kind: "midseason", label: "Midseason Report", short: "Report", href: "/midseason/2026/" },
    ];
    renderBand("/", { ...MENU, items });
    expect(
      within(pillBar())
        .getAllByRole("link")
        .map((link) => link.textContent),
    ).toContain("Midseason Report");
    fireEvent.click(menuButton());
    const rows = within(sheet())
      .getAllByRole("link")
      .filter((link) => !/^WK /.test(link.textContent ?? ""));
    expect(rows).toHaveLength(5);
    expect(rows.map((row) => row.textContent).join()).not.toContain("Midseason");
  });

  it("marks the week of the open week page", () => {
    renderBand("/2026/week-08/");
    fireEvent.click(menuButton());
    expect(current(sheet())).toEqual(["Week 8Scores and recaps"]);
  });

  it("marks the week item on the page of an older week too", () => {
    renderBand("/2026/week-07/");
    fireEvent.click(menuButton());
    expect(current(sheet())).toEqual(["Week 8Scores and recaps"]);
  });

  it("marks Managers on the page of one manager", () => {
    renderBand("/2026/managers/6/");
    fireEvent.click(menuButton());
    expect(current(sheet())).toEqual(["ManagersGrades and records"]);
  });

  it("marks no item on a page that is no destination, such as the 404 page", () => {
    renderBand(undefined);
    fireEvent.click(menuButton());
    expect(current(sheet())).toEqual([]);
  });
});

describe("The top band has no week chip (AT-11)", () => {
  it("shows no week chip and no strip of weeks, on a page that is not a week page", () => {
    renderBand("/");
    expect(screen.queryByText(/^WK /, { selector: "summary" })).toBeNull();
    expect(screen.queryByRole("navigation", { name: "Weeks of the season" })).toBeNull();
    expect(within(screen.getByRole("banner")).queryByText(/^WK /)).toBeNull();
  });

  it("shows no week chip and no strip of weeks, on the page of a week", () => {
    renderBand("/2026/week-07/");
    expect(screen.queryByText(/^WK /, { selector: "summary" })).toBeNull();
    expect(screen.queryByRole("navigation", { name: "Weeks of the season" })).toBeNull();
    expect(within(screen.getByRole("banner")).queryByText(/^WK /)).toBeNull();
  });

  it("keeps the week row and Past weeks in the menu sheet", () => {
    renderBand("/2026/week-07/");
    fireEvent.click(menuButton());
    expect(within(sheet()).getByRole("link", { name: /^Week 8/ })).toBeTruthy();
    fireEvent.click(within(sheet()).getByRole("button", { name: "Past weeks" }));
    expect(linksIn(screen.getByRole("list", { name: "Past weeks" }))).toEqual([
      ["WK 07", "/2026/week-07/"],
      ["WK 06", "/2026/week-06/"],
    ]);
  });
});

/* The top band of the front door. */
function doorBand(pageHref = "/", menu: SiteMenu = MENU) {
  return <TopBand title={TITLE} brand={BRAND} menu={menu} pageHref={pageHref} />;
}

function renderDoorBand(pageHref = "/", menu: SiteMenu = MENU) {
  render(doorBand(pageHref, menu));
}

const menuButton = () =>
  within(screen.getByRole("banner")).getByRole("button", { name: /^(Open|Close) the menu$/ });
const sheet = () => screen.getByRole("navigation", { name: "Pages" });

describe("The menu sheet and the top band of the front door (AT-45, AT-47)", () => {
  it("shows the menu button, and no dock, on a page that passes no sheet", () => {
    renderBand("/rankings/");
    expect(
      within(screen.getByRole("banner")).getByRole("button", { name: "Open the menu" }),
    ).toBeTruthy();
    expect(screen.queryByRole("navigation", { name: "Bottom menu", hidden: true })).toBeNull();
  });

  it("shows no dock, and holds the menu button in the banner", () => {
    renderDoorBand();
    expect(screen.queryByRole("navigation", { name: "Bottom menu", hidden: true })).toBeNull();
    expect(screen.queryByText(/^WK /, { selector: "summary" })).toBeNull();
    expect(menuButton().getAttribute("aria-expanded")).toBe("false");
  });

  it("keeps the sheet closed and out of the accessibility tree until the button opens it", () => {
    renderDoorBand();
    expect(screen.queryByRole("dialog", { name: "Pages" })).toBeNull();
    expect(screen.queryByRole("navigation", { name: "Pages" })).toBeNull();
  });

  it("opens the sheet as a modal dialog named Pages, so the page under the dim takes no focus", () => {
    renderDoorBand();
    fireEvent.click(menuButton());
    const dialog = screen.getByRole("dialog", { name: "Pages" });
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(dialog.contains(sheet())).toBe(true);
  });

  it("opens the sheet with one row per page, each with an icon, its name, and its note, and a check on the open page", () => {
    renderDoorBand("/");
    fireEvent.click(menuButton());
    const rows = within(sheet())
      .getAllByRole("link")
      .filter((link) => !/^WK /.test(link.textContent ?? ""));
    expect(rows.map((row) => [row.textContent, row.getAttribute("href")])).toEqual([
      ["HomeAsk about your team", "/"],
      ["Week 8Scores and recaps", "/2026/week-08/"],
      ["Power RankingsThe league, ranked", "/rankings/"],
      ["ManagersGrades and records", "/2026/managers/"],
      ["Trade AnalyzerCheck a trade", "/analyze/"],
    ]);
    for (const row of rows) expect(row.querySelector("svg")).not.toBeNull();
    expect(current(sheet())).toEqual(["HomeAsk about your team"]);
    expect(
      within(sheet()).getByRole("link", { current: "page" }).querySelector("[data-check]"),
    ).not.toBeNull();
    expect(
      within(sheet())
        .getAllByRole("link")
        .filter((link) => link.querySelector("[data-check]")),
    ).toHaveLength(1);
  });

  it("turns the button into the close button while the sheet is open", () => {
    renderDoorBand();
    fireEvent.click(menuButton());
    expect(menuButton().getAttribute("aria-expanded")).toBe("true");
    expect(menuButton().getAttribute("aria-label")).toBe("Close the menu");
  });

  it("moves the focus to the sheet on open", async () => {
    renderDoorBand();
    fireEvent.click(menuButton());
    const dialog = screen.getByRole("dialog", { name: "Pages" });
    await waitFor(() => expect(dialog.contains(document.activeElement)).toBe(true));
  });

  it("marks no row on a page that is no destination, such as /ask/", () => {
    renderDoorBand("/ask/");
    fireEvent.click(menuButton());
    expect(current(sheet())).toEqual([]);
    expect(sheet().querySelector("[data-check]")).toBeNull();
  });

  it("opens the latest report from the week row, and lists each older week under Past weeks", () => {
    renderDoorBand("/");
    fireEvent.click(menuButton());
    expect(
      within(sheet())
        .getByRole("link", { name: /^Week 8/ })
        .getAttribute("href"),
    ).toBe("/2026/week-08/");
    const past = within(sheet()).getByRole("button", { name: "Past weeks" });
    expect(past.getAttribute("aria-expanded")).toBe("false");
    expect(within(sheet()).queryByRole("link", { name: "WK 07" })).toBeNull();
    fireEvent.click(past);
    expect(past.getAttribute("aria-expanded")).toBe("true");
    const weeks = screen.getByRole("list", { name: "Past weeks" });
    expect(linksIn(weeks)).toEqual([
      ["WK 07", "/2026/week-07/"],
      ["WK 06", "/2026/week-06/"],
    ]);
  });

  it("shows no Past weeks when the newest week is the one published week", () => {
    renderDoorBand("/", { items: MENU.items, weeks: MENU.weeks.slice(0, 1) });
    fireEvent.click(menuButton());
    expect(within(sheet()).getByRole("link", { name: /^Week 8/ })).toBeTruthy();
    expect(within(sheet()).queryByRole("button", { name: "Past weeks" })).toBeNull();
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

describe("The menu sheet closes three ways and keeps the focus in (AT-46)", () => {
  async function openSheet() {
    renderDoorBand();
    // A full tap, as a finger gives: the press, the release, then the click.
    fireEvent.pointerDown(menuButton());
    fireEvent.pointerUp(menuButton());
    fireEvent.click(menuButton());
    const dialog = screen.getByRole("dialog", { name: "Pages" });
    await waitFor(() => expect(dialog.contains(document.activeElement)).toBe(true));
  }

  async function expectClosed() {
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Pages" })).toBeNull());
    expect(screen.queryByRole("navigation", { name: "Pages" })).toBeNull();
    expect(menuButton().getAttribute("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(menuButton());
  }

  it("closes by the X", async () => {
    await openSheet();
    fireEvent.click(menuButton());
    await expectClosed();
  });

  it("closes by a tap on the dimmed page", async () => {
    await openSheet();
    const scrim = screen.getByTestId("menu-scrim");
    fireEvent.pointerDown(scrim);
    fireEvent.pointerUp(scrim);
    await expectClosed();
  });

  it("closes by Escape", async () => {
    await openSheet();
    fireEvent.keyDown(document.activeElement ?? document, { key: "Escape" });
    await expectClosed();
  });

  it("keeps the focus in the sheet when a Tab leaves its last row", async () => {
    render(
      <>
        {doorBand()}
        <button type="button">After</button>
      </>,
    );
    fireEvent.click(menuButton());
    const dialog = screen.getByRole("dialog", { name: "Pages" });
    await waitFor(() => expect(dialog.contains(document.activeElement)).toBe(true));
    const rows = within(dialog)
      .getAllByRole("link")
      .filter((link) => !/^WK /.test(link.textContent ?? ""));
    const last = rows[rows.length - 1];
    last.focus();
    fireEvent.keyDown(last, { key: "Tab" });
    // The trap takes the Tab and wraps the focus inside the sheet, so it never reaches the page under the dim.
    await waitFor(() => expect(document.activeElement).not.toBe(last));
    expect(dialog.contains(document.activeElement)).toBe(true);
    expect(document.activeElement).not.toBe(screen.getByRole("button", { name: "After" }));
    expect(screen.getByRole("dialog", { name: "Pages" })).toBe(dialog);
  });
});

describe("The menu sheet closes at the desktop tier", () => {
  it("closes when the window widens to the desktop tier, so the page does not stay inert under a hidden sheet", async () => {
    // A query list for the desktop tier that the test can flip, as a browser does when the window widens.
    const listeners = new Set<() => void>();
    const desktop = {
      matches: false,
      addEventListener: (_type: string, listener: () => void) => listeners.add(listener),
      removeEventListener: (_type: string, listener: () => void) => listeners.delete(listener),
    };
    // The same breakpoint as the desktop variant, --breakpoint-desktop in globals.css.
    spyOn(window, "matchMedia").mockImplementation((query: string) =>
      query === "(min-width: 64rem)" ? (desktop as unknown as MediaQueryList) : noMatch(query),
    );
    try {
      renderDoorBand();
      fireEvent.click(menuButton());
      expect(screen.getByRole("dialog", { name: "Pages" })).toBeTruthy();
      act(() => {
        desktop.matches = true;
        for (const listener of listeners) listener();
      });
      await waitFor(() => expect(screen.queryByRole("dialog", { name: "Pages" })).toBeNull());
      expect(menuButton().getAttribute("aria-expanded")).toBe("false");
    } finally {
      spyOn(window, "matchMedia").mockImplementation(noMatch);
    }
  });
});
