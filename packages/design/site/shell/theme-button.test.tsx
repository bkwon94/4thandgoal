/**
 * Tests for the theme button, through the top band render. They press the button by its name.
 * They read the class on the root element and the stored choice, not the class names of the button.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { TopBand } from "./top-band";

const TO_DARK = "Switch to dark theme";
const TO_LIGHT = "Switch to light theme";

/* The top band of the week 7 report. Every brand has both sets, so every top band shows the theme button. */
function renderWeekBand() {
  render(
    <TopBand
      title="Cornerstone Fantasy Football League"
      brand={{ home: "/", logo: "/images/logo.png" }}
      menu={{
        items: [
          { kind: "home", label: "Home", short: "Home", href: "/" },
          { kind: "week", label: "Week 7", short: "Week 7", href: "/2026/week-07/" },
          { kind: "rankings", label: "Power Rankings", short: "Rankings", href: "/rankings/" },
          { kind: "analyzer", label: "Trade Analyzer", short: "Trade", href: "/analyze/" },
        ],
        weeks: [{ number: 7, href: "/2026/week-07/" }],
      }}
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

function bandButton(name: string) {
  return within(screen.getByRole("banner")).getByRole("button", { name });
}

function rootIsDark() {
  return document.documentElement.classList.contains("dark");
}

/* The export ships the dark class on <html> for every client (ADR 0024), so each test starts there. */
function shipDark() {
  document.documentElement.classList.add("dark");
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
  it("sits in the top band and offers the light theme on the shipped dark page", () => {
    shipDark();
    renderWeekBand();
    expect(bandButton(TO_LIGHT)).toBeTruthy();
  });

  it("stores no choice before a press", () => {
    shipDark();
    renderWeekBand();
    expect(localStorage.getItem("cpc.theme")).toBeNull();
  });

  it("switches to the light theme on a press and stores the choice", () => {
    shipDark();
    renderWeekBand();
    fireEvent.click(bandButton(TO_LIGHT));
    expect(rootIsDark()).toBe(false);
    expect(localStorage.getItem("cpc.theme")).toBe("light");
    expect(bandButton(TO_DARK)).toBeTruthy();
  });

  it("switches back to the dark theme on a second press and stores the choice", () => {
    shipDark();
    renderWeekBand();
    fireEvent.click(bandButton(TO_LIGHT));
    fireEvent.click(bandButton(TO_DARK));
    expect(rootIsDark()).toBe(true);
    expect(localStorage.getItem("cpc.theme")).toBe("dark");
    expect(bandButton(TO_LIGHT)).toBeTruthy();
  });

  it("counts each press as an event named for the theme it gives", () => {
    const count = vi.fn();
    window.goatcounter = { count };
    shipDark();
    renderWeekBand();
    fireEvent.click(bandButton(TO_LIGHT));
    expect(count).toHaveBeenLastCalledWith({ path: "theme-light", event: true });
    fireEvent.click(bandButton(TO_DARK));
    expect(count).toHaveBeenLastCalledWith({ path: "theme-dark", event: true });
    delete window.goatcounter;
  });

  it("is the one theme button of the page, outside the pill bar and the dock", () => {
    shipDark();
    renderWeekBand();
    expect(screen.getAllByRole("button", { name: TO_LIGHT })).toHaveLength(1);
    expect(within(screen.getByRole("navigation", { name: "Site menu" })).queryByRole("button")).toBeNull();
    expect(within(screen.getByRole("navigation", { name: "Bottom menu" })).queryByRole("button")).toBeNull();
  });

  it("names the dark theme on mount when the boot script removed the dark class for a stored light choice", () => {
    localStorage.setItem("cpc.theme", "light");
    renderWeekBand();
    expect(bandButton(TO_DARK)).toBeTruthy();
  });

  it("still switches the theme with blocked storage", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    shipDark();
    renderWeekBand();
    fireEvent.click(bandButton(TO_LIGHT));
    expect(rootIsDark()).toBe(false);
    expect(bandButton(TO_DARK)).toBeTruthy();
  });
});
