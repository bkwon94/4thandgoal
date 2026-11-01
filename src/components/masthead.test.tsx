/**
 * Tests for the masthead. They read the title, the subtitle, and the week line from the screen.
 * They check what a reader sees, not the class names.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import type { WeekSummary } from "@/lib/data/week-data";
import { Masthead } from "./masthead";

/* Three published weeks, newest first, as listWeekSummaries returns them. */
const WEEKS: WeekSummary[] = [
  { number: 7, dates: "Oct 22 – Oct 26, 2026", href: "/2026/week-07/" },
  { number: 6, dates: "Oct 15 – Oct 19, 2026", href: "/2026/week-06/" },
  { number: 5, dates: "Oct 8 – Oct 12, 2026", href: "/2026/week-05/" },
];

/* The masthead of the week 7 report, with the waiver flag off and no managers file. A test overrides a prop to change one value. */
function renderWeekMasthead(props: Partial<Parameters<typeof Masthead>[0]> = {}) {
  render(
    <Masthead
      subtitle="League Weekly"
      weeks={WEEKS}
      pageHref="/2026/week-07/"
      waiverHref={null}
      managersHref={null}
      {...props}
    />,
  );
}

/* The list of the open sheet. The row shares its name, so the query stays inside the dialog. */
async function findSheetMenu() {
  const dialog = await screen.findByRole("dialog", { name: "Menu" });
  return within(dialog).getByRole("navigation", { name: "Site menu" });
}

/* Taps the menu button and returns the open menu. */
async function openMenu() {
  fireEvent.click(menuButton());
  return findSheetMenu();
}

/* The label and the href of each link in a part of the page, in order. */
function linksIn(element: HTMLElement) {
  return within(element)
    .getAllByRole("link")
    .map((link) => [link.textContent, link.getAttribute("href")]);
}

/* The brand link of the masthead. The row has links too, so a test finds the brand link by its title. */
function brandLink(title: RegExp) {
  return screen.getByRole("link", { name: title });
}

function menuButton() {
  return screen.getByRole("button", { name: "Menu" });
}

/* The reduced-motion setting of the system. A test turns it on, and the stub tells Framer Motion of the change. */
let reduceMotion = false;
let motionChange: (() => void) | undefined;

function setReducedMotion(on: boolean) {
  reduceMotion = on;
  motionChange?.();
}

/* jsdom has no matchMedia. Framer Motion reads it once per file and then listens for a change, so the stub runs at the top. */
vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      // Framer Motion asks for "(prefers-reduced-motion)" with no value, so the stub matches the feature name.
      get matches() {
        return reduceMotion && query.includes("prefers-reduced-motion");
      },
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: (_type: string, listener: () => void) => {
        motionChange = listener;
      },
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList,
);

/* jsdom has no IntersectionObserver. The stub keeps each observer, so a test reports the masthead in or out of view. */
const observers = new Set<ObserverStub>();

class ObserverStub {
  target: Element | undefined;
  constructor(private callback: IntersectionObserverCallback) {
    observers.add(this);
  }
  observe(target: Element) {
    this.target = target;
  }
  unobserve() {}
  disconnect() {
    observers.delete(this);
  }
  takeRecords() {
    return [];
  }
}

vi.stubGlobal("IntersectionObserver", ObserverStub);

/* Reports to each observer that the masthead is in view or out of view, as a scroll does. */
function reportMasthead(inView: boolean) {
  act(() => {
    for (const observer of observers) {
      const entry = { isIntersecting: inView, target: observer.target } as IntersectionObserverEntry;
      observer["callback"]([entry], observer as unknown as IntersectionObserver);
    }
  });
}

afterEach(() => {
  cleanup();
  setReducedMotion(false);
});

afterAll(() => {
  vi.unstubAllGlobals();
});

describe("Masthead", () => {
  it("shows the title and the subtitle in the home link", () => {
    render(<Masthead subtitle="Trade Analyzer" />);
    const home = brandLink(/Cornerstone Fantasy Football League/);
    expect(home.textContent).toContain("Cornerstone Fantasy Football League");
    expect(home.textContent).toContain("Trade Analyzer");
    expect(home.getAttribute("href")).toBe("/");
  });

  it("shows the week line children under the brand", () => {
    render(
      <Masthead subtitle="League Weekly">
        <p>Week 6</p>
      </Masthead>,
    );
    expect(screen.getByText("Week 6")).toBeTruthy();
    expect(screen.getByText("League Weekly")).toBeTruthy();
  });

  it("shows a custom title in place of the default brand", () => {
    render(<Masthead title="Custom Brand" subtitle="League Weekly" />);
    const home = brandLink(/Custom Brand/);
    expect(home.textContent).toContain("Custom Brand");
    expect(home.textContent).not.toContain("Cornerstone Fantasy Football League");
  });

  it("shows no week line when there are no children", () => {
    render(<Masthead subtitle="Trade Analyzer" />);
    expect(screen.queryByText("Week 6")).toBeNull();
  });

  it("shows no subtitle when none is given", () => {
    render(<Masthead />);
    expect(brandLink(/Cornerstone Fantasy Football League/).textContent).toBe("Cornerstone Fantasy Football League");
  });

  it("shows no waiver link in the masthead, because the waiver page lives in the menu", () => {
    renderWeekMasthead({ waiverHref: "/2026/week-06/waiver/" });
    // The desktop row renders the menu, so the one waiver link on the page is the item of the row.
    expect(screen.getAllByRole("link", { name: "Waiver Wire" })).toEqual([
      within(row()).getByRole("link", { name: "Waiver Wire" }),
    ]);
  });
});

describe("Masthead menu", () => {
  it("shows a closed menu button", () => {
    renderWeekMasthead();
    expect(menuButton().getAttribute("aria-expanded")).toBe("false");
  });

  it("opens the menu on a tap and names the list it controls", async () => {
    renderWeekMasthead();
    // The open menu is modal, so it hides the page and the button from the screen reader. The test keeps the button it found first.
    const button = menuButton();
    expect(button.getAttribute("aria-controls")).toBeNull();
    fireEvent.click(button);
    const menu = await findSheetMenu();
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(button.getAttribute("aria-controls")).toBe(menu.id);
  });

  it("lists the pages, then the past weeks newest first", async () => {
    renderWeekMasthead();
    const menu = await openMenu();
    expect(linksIn(menu)).toEqual([
      ["Home", "/"],
      ["Week 7", "/2026/week-07/"],
      ["Power Rankings", "/rankings/"],
      ["Trade Analyzer", "/analyze/"],
      ["Week 6", "/2026/week-06/"],
      ["Week 5", "/2026/week-05/"],
    ]);
  });

  it("puts the past weeks under a Past Weeks heading", async () => {
    renderWeekMasthead();
    const menu = await openMenu();
    const past = within(menu).getByRole("list", { name: "Past Weeks" });
    expect(within(menu).getByRole("heading", { name: "Past Weeks" })).toBeTruthy();
    expect(linksIn(past)).toEqual([
      ["Week 6", "/2026/week-06/"],
      ["Week 5", "/2026/week-05/"],
    ]);
  });

  it("marks the item of the open page as the current page", async () => {
    renderWeekMasthead({ pageHref: "/rankings/" });
    const menu = await openMenu();
    const current = within(menu)
      .getAllByRole("link")
      .filter((link) => link.getAttribute("aria-current") === "page");
    expect(current.map((link) => link.textContent)).toEqual(["Power Rankings"]);
  });

  it("marks a past week as the current page on its report", async () => {
    renderWeekMasthead({ pageHref: "/2026/week-05/" });
    const menu = await openMenu();
    expect(within(menu).getByRole("link", { name: "Week 5" }).getAttribute("aria-current")).toBe("page");
    expect(within(menu).getByRole("link", { name: "Week 7" }).getAttribute("aria-current")).toBeNull();
  });

  it("closes on Escape and returns focus to the button", async () => {
    renderWeekMasthead();
    const button = menuButton();
    const menu = await openMenu();
    fireEvent.keyDown(menu, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Menu" })).toBeNull());
    expect(button.getAttribute("aria-expanded")).toBe("false");
    await waitFor(() => expect(document.activeElement).toBe(button));
  });

  it("closes on a tap outside the menu", async () => {
    renderWeekMasthead();
    await openMenu();
    fireEvent.pointerDown(document.body);
    fireEvent.mouseDown(document.body);
    fireEvent.click(document.body);
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Menu" })).toBeNull());
  });

  it("closes on a second tap of the button", async () => {
    renderWeekMasthead();
    const button = menuButton();
    await openMenu();
    fireEvent.click(button);
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Menu" })).toBeNull());
    expect(button.getAttribute("aria-expanded")).toBe("false");
  });

  it("lists the waiver page after the trade analyzer when the flag is on", async () => {
    renderWeekMasthead({ waiverHref: "/2026/week-06/waiver/" });
    const menu = await openMenu();
    expect(linksIn(menu).slice(3, 5)).toEqual([
      ["Trade Analyzer", "/analyze/"],
      ["Waiver Wire", "/2026/week-06/waiver/"],
    ]);
  });

  it("lists no waiver page when the flag is off", async () => {
    renderWeekMasthead({ waiverHref: null });
    const menu = await openMenu();
    expect(within(menu).queryByRole("link", { name: "Waiver Wire" })).toBeNull();
  });

  it("lists the managers index after the power rankings only when the managers file exists", async () => {
    renderWeekMasthead({ managersHref: "/2026/managers/" });
    const menu = await openMenu();
    expect(linksIn(menu).slice(2, 4)).toEqual([
      ["Power Rankings", "/rankings/"],
      ["Managers", "/2026/managers/"],
    ]);
    cleanup();
    renderWeekMasthead({ managersHref: null });
    const bare = await openMenu();
    expect(within(bare).queryByRole("link", { name: "Managers" })).toBeNull();
  });

  it("opens the menu at rest and closes it with motion off", async () => {
    setReducedMotion(true);
    renderWeekMasthead();
    const button = menuButton();
    const menu = await openMenu();
    // With motion off the items take no drop and no stagger, so each one is in place on the tap.
    expect(linksIn(menu)).toHaveLength(6);
    fireEvent.keyDown(menu, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Menu" })).toBeNull());
    await waitFor(() => expect(document.activeElement).toBe(button));
  });
});

/* The desktop row of the menu. jsdom runs no media query, so the row renders next to the menu button, and a test scopes to its landmark. */
function row() {
  return screen.getByRole("navigation", { name: "Site menu" });
}

/* Taps the Past Weeks trigger of the row and returns the open popover. */
async function openPastWeeks() {
  fireEvent.click(within(row()).getByRole("button", { name: "Past Weeks" }));
  return screen.findByRole("dialog", { name: "Past Weeks" });
}

describe("Masthead row", () => {
  it("lists the pages in order with their hrefs", () => {
    renderWeekMasthead();
    expect(linksIn(row())).toEqual([
      ["Home", "/"],
      ["Week 7", "/2026/week-07/"],
      ["Power Rankings", "/rankings/"],
      ["Trade Analyzer", "/analyze/"],
    ]);
  });

  it("ends with a closed Past Weeks trigger", () => {
    renderWeekMasthead();
    const trigger = within(row()).getByRole("button", { name: "Past Weeks" });
    expect(trigger.getAttribute("aria-expanded")).toBe("false");
  });

  it("opens the past weeks newest first on a tap of the trigger", async () => {
    renderWeekMasthead();
    const trigger = within(row()).getByRole("button", { name: "Past Weeks" });
    const popover = await openPastWeeks();
    expect(trigger.getAttribute("aria-expanded")).toBe("true");
    expect(linksIn(popover)).toEqual([
      ["Week 6", "/2026/week-06/"],
      ["Week 5", "/2026/week-05/"],
    ]);
  });

  it("closes the popover on Escape", async () => {
    renderWeekMasthead();
    const trigger = within(row()).getByRole("button", { name: "Past Weeks" });
    const popover = await openPastWeeks();
    fireEvent.keyDown(popover, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Past Weeks" })).toBeNull());
    expect(trigger.getAttribute("aria-expanded")).toBe("false");
  });

  it("returns focus to the Past Weeks trigger when the popover closes on Escape", async () => {
    renderWeekMasthead();
    const trigger = within(row()).getByRole("button", { name: "Past Weeks" });
    const popover = await openPastWeeks();
    fireEvent.keyDown(popover, { key: "Escape" });
    await waitFor(() => expect(document.activeElement).toBe(trigger));
  });

  it("gives a screen reader a close button in the popover", async () => {
    renderWeekMasthead();
    const popover = await openPastWeeks();
    // The popover keeps focus inside, so a touch screen reader needs a control to leave it.
    fireEvent.click(within(popover).getByRole("button", { name: "Close Past Weeks" }));
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Past Weeks" })).toBeNull());
  });

  it("closes the popover on a click outside", async () => {
    renderWeekMasthead();
    await openPastWeeks();
    fireEvent.pointerDown(document.body);
    fireEvent.mouseDown(document.body);
    fireEvent.click(document.body);
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Past Weeks" })).toBeNull());
  });

  it("marks the row link of the open page as the current page", () => {
    renderWeekMasthead({ pageHref: "/rankings/" });
    const current = within(row())
      .getAllByRole("link")
      .filter((link) => link.getAttribute("aria-current") === "page");
    expect(current.map((link) => link.textContent)).toEqual(["Power Rankings"]);
  });

  it("marks a past week in the popover as the current page on its report", async () => {
    renderWeekMasthead({ pageHref: "/2026/week-05/" });
    const popover = await openPastWeeks();
    expect(within(popover).getByRole("link", { name: "Week 5" }).getAttribute("aria-current")).toBe("page");
    expect(within(popover).getByRole("link", { name: "Week 6" }).getAttribute("aria-current")).toBeNull();
  });

  it("opens the popover at rest and closes it with motion off", async () => {
    setReducedMotion(true);
    renderWeekMasthead();
    const popover = await openPastWeeks();
    // With motion off the popover takes no scale and no fade, so each week is in place on the tap.
    expect(linksIn(popover)).toHaveLength(2);
    fireEvent.keyDown(popover, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Past Weeks" })).toBeNull());
  });
});

/* The compact bar. It shows once the masthead scrolls out of view. */
function bar() {
  return screen.getByRole("region", { name: "Top bar" });
}

function queryBar() {
  return screen.queryByRole("region", { name: "Top bar" });
}

describe("Masthead compact bar", () => {
  it("shows no bar while the masthead is in view", () => {
    renderWeekMasthead();
    expect(queryBar()).toBeNull();
  });

  it("shows the bar with a home link and a menu button once the masthead scrolls out", () => {
    renderWeekMasthead();
    reportMasthead(false);
    const home = within(bar()).getByRole("link", { name: "Cornerstone Fantasy Football League" });
    expect(home.getAttribute("href")).toBe("/");
    expect(within(bar()).getByRole("button", { name: "Menu" }).getAttribute("aria-expanded")).toBe("false");
  });

  it("opens the same menu from the bar button and returns focus to it on Escape", async () => {
    renderWeekMasthead();
    reportMasthead(false);
    // The open menu is modal, so the test keeps the bar button it found first.
    const button = within(bar()).getByRole("button", { name: "Menu" });
    expect(button.getAttribute("aria-controls")).toBeNull();
    fireEvent.click(button);
    const menu = await findSheetMenu();
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(button.getAttribute("aria-controls")).toBe(menu.id);
    expect(linksIn(menu).map(([label]) => label)).toEqual([
      "Home",
      "Week 7",
      "Power Rankings",
      "Trade Analyzer",
      "Week 6",
      "Week 5",
    ]);
    fireEvent.keyDown(menu, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "Menu" })).toBeNull());
    await waitFor(() => expect(document.activeElement).toBe(button));
  });

  it("hides the bar once the masthead scrolls back into view", async () => {
    renderWeekMasthead();
    reportMasthead(false);
    expect(bar()).toBeTruthy();
    reportMasthead(true);
    await waitFor(() => expect(queryBar()).toBeNull());
  });

  it("shows the bar at rest and hides it with motion off", async () => {
    setReducedMotion(true);
    renderWeekMasthead();
    reportMasthead(false);
    // With motion off the bar takes no slide, so its home link and its button are in place at once.
    expect(within(bar()).getByRole("link", { name: "Cornerstone Fantasy Football League" })).toBeTruthy();
    expect(within(bar()).getByRole("button", { name: "Menu" })).toBeTruthy();
    reportMasthead(true);
    await waitFor(() => expect(queryBar()).toBeNull());
  });

  it("names the row of the bar apart from the row of the masthead", () => {
    renderWeekMasthead();
    reportMasthead(false);
    // A screen reader lists both rows while the bar shows, so each landmark takes its own name.
    const names = screen.getAllByRole("navigation").map((landmark) => landmark.getAttribute("aria-label"));
    expect(names).toEqual(["Site menu", "Top bar menu"]);
  });

  it("shows the same row in the bar for the desktop tier", () => {
    renderWeekMasthead();
    reportMasthead(false);
    expect(linksIn(within(bar()).getByRole("navigation", { name: "Top bar menu" }))).toEqual([
      ["Home", "/"],
      ["Week 7", "/2026/week-07/"],
      ["Power Rankings", "/rankings/"],
      ["Trade Analyzer", "/analyze/"],
    ]);
  });
});
