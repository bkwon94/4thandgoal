/**
 * Tests for the theme button, through the masthead render. They press the button by its name.
 * They read the class on the root element and the stored choice, not the class names of the button.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import type { WeekSummary } from "@/lib/week-types";
import { Masthead } from "./masthead";

/* One published week, as listWeekSummaries returns it. */
const WEEKS: WeekSummary[] = [{ number: 7, dates: "Oct 22 – Oct 26, 2026", href: "/2026/week-07/" }];

const TO_DARK = "Switch to dark theme";
const TO_LIGHT = "Switch to light theme";

/* The masthead of the week 7 report, with the waiver flag off. */
function renderWeekMasthead() {
  render(
    <Masthead
      subtitle="League Weekly"
      weeks={WEEKS}
      links={{ home: "/", rankings: "/rankings/", analyze: "/analyze/", logo: "/images/logo.png", managers: null, waiver: null }}
      pageHref="/2026/week-07/"
    />,
  );
}

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

/* jsdom has no IntersectionObserver. The stub keeps each observer, so a test reports the masthead out of view. */
const observers = new Set<ObserverStub>();

class ObserverStub {
  target: Element | undefined;
  constructor(public callback: IntersectionObserverCallback) {
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

/* Reports to each observer that the masthead is out of view, as a scroll does. The compact bar then renders. */
function scrollMastheadOut() {
  act(() => {
    for (const observer of observers) {
      const entry = { isIntersecting: false, target: observer.target } as IntersectionObserverEntry;
      observer.callback([entry], observer as unknown as IntersectionObserver);
    }
  });
}

/* The theme button of the masthead row. jsdom runs no media query, so the desktop row renders a second one inside its landmark. */
function buttonOutsideNav(container: HTMLElement, name: string) {
  const button = within(container)
    .getAllByRole("button", { name })
    .find((candidate) => !candidate.closest("nav"));
  if (!button) throw new Error(`No theme button named "${name}" outside the navigation`);
  return button;
}

function mastheadButton(name: string) {
  return buttonOutsideNav(screen.getByRole("banner"), name);
}

function rootIsDark() {
  return document.documentElement.classList.contains("dark");
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  document.documentElement.classList.remove("dark");
  localStorage.clear();
});

afterAll(() => {
  vi.unstubAllGlobals();
});

describe("Theme button", () => {
  it("sits in the masthead row and offers the dark theme", () => {
    renderWeekMasthead();
    expect(mastheadButton(TO_DARK)).toBeTruthy();
  });

  it("stores no choice before a press", () => {
    renderWeekMasthead();
    expect(localStorage.getItem("cpc.theme")).toBeNull();
  });

  it("switches to the dark theme on a press and stores the choice", () => {
    renderWeekMasthead();
    fireEvent.click(mastheadButton(TO_DARK));
    expect(rootIsDark()).toBe(true);
    expect(localStorage.getItem("cpc.theme")).toBe("dark");
    expect(mastheadButton(TO_LIGHT)).toBeTruthy();
  });

  it("switches back to the light theme on a second press and stores the choice", () => {
    renderWeekMasthead();
    fireEvent.click(mastheadButton(TO_DARK));
    fireEvent.click(mastheadButton(TO_LIGHT));
    expect(rootIsDark()).toBe(false);
    expect(localStorage.getItem("cpc.theme")).toBe("light");
    expect(mastheadButton(TO_DARK)).toBeTruthy();
  });

  it("counts each press as an event named for the theme it gives", () => {
    const count = vi.fn();
    window.goatcounter = { count };
    renderWeekMasthead();
    fireEvent.click(mastheadButton(TO_DARK));
    expect(count).toHaveBeenLastCalledWith({ path: "theme-dark", event: true });
    fireEvent.click(mastheadButton(TO_LIGHT));
    expect(count).toHaveBeenLastCalledWith({ path: "theme-light", event: true });
    delete window.goatcounter;
  });

  it("sits in the compact bar once the masthead is out of view", () => {
    renderWeekMasthead();
    scrollMastheadOut();
    const bar = screen.getByRole("region", { name: "Top bar" });
    fireEvent.click(buttonOutsideNav(bar, TO_DARK));
    expect(rootIsDark()).toBe(true);
    // Every copy follows the press, so the masthead button names the light theme too.
    expect(mastheadButton(TO_LIGHT)).toBeTruthy();
  });

  it("leaves the masthead row to the links, so the masthead has one theme button", () => {
    renderWeekMasthead();
    const row = screen.getByRole("navigation", { name: "Site menu" });
    expect(within(row).queryByRole("button", { name: TO_DARK })).toBeNull();
    expect(within(screen.getByRole("banner")).getAllByRole("button", { name: TO_DARK })).toHaveLength(1);
  });

  it("ends the row of the compact bar", () => {
    renderWeekMasthead();
    scrollMastheadOut();
    const row = screen.getByRole("navigation", { name: "Top bar menu" });
    const button = within(row).getByRole("button", { name: TO_DARK });
    fireEvent.click(button);
    expect(rootIsDark()).toBe(true);
  });

  it("names the light theme on mount when the root already has the dark class", () => {
    // The boot script adds the class from a stored dark choice before React runs.
    localStorage.setItem("cpc.theme", "dark");
    document.documentElement.classList.add("dark");
    renderWeekMasthead();
    expect(mastheadButton(TO_LIGHT)).toBeTruthy();
  });

  it("still switches the theme with blocked storage", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    renderWeekMasthead();
    fireEvent.click(mastheadButton(TO_DARK));
    expect(rootIsDark()).toBe(true);
    expect(mastheadButton(TO_LIGHT)).toBeTruthy();
  });
});
