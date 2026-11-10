/**
 * Tests for the 404 page, on the real generated client values of cpc and the fixed copy of the published weeks.
 * They read what a reader sees: the hero, the big 404, the line, the two buttons, and the shell with no item marked.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { readFixtureSite } from "@/fixtures/sites";
import NotFound from "./not-found";

/* The readers of public/ read the fixed copy of the cpc data, so a weekly publish never changes these tests. The spy
   runs before the imports, because the week reader takes its folder when it loads. Each test sets it again, because a
   restore of the mocks removes it. */
await vi.hoisted(async () => (await import("@/fixtures/sites")).readFixtureSite("cpc"));
beforeEach(() => readFixtureSite("cpc"));

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

describe("The 404 page (AT-32)", () => {
  it("shows the hero with the label, the big 404, and the line of the spec", () => {
    render(<NotFound />);
    const hero = screen.getByRole("region", { name: "Page not found" });
    expect(within(hero).getByText("404")).toBeTruthy();
    expect(within(hero).getByText("This page does not exist. The link may be old, or the week is not out yet.")).toBeTruthy();
  });

  /* AT-12: the title takes the one title style of every hero, and the big "404" is art, not the heading. */
  it("titles the hero Page not found, with the big 404 as art in the feature slot", () => {
    render(<NotFound />);
    const hero = screen.getByRole("region", { name: "Page not found" });
    expect(within(hero).getByRole("heading", { level: 1 }).textContent).toBe("Page not found");
    expect(within(hero).queryByRole("heading", { name: "404" })).toBeNull();
    expect(within(hero).getByText("404").closest("[data-hero-slot]")?.getAttribute("data-hero-slot")).toBe("feature");
  });

  it("fills the slots in the slot order, with no eyebrow and no stats", () => {
    render(<NotFound />);
    const hero = screen.getByRole("region", { name: "Page not found" });
    const slots = [...hero.querySelectorAll("[data-hero-slot]")].map((slot) => slot.getAttribute("data-hero-slot"));
    expect(slots).toEqual(["title", "meta", "feature", "action"]);
    const action = hero.querySelector("[data-hero-slot=action]") as HTMLElement;
    expect(within(action).getByRole("link", { name: "Go Home" })).toBeTruthy();
  });

  it("draws one scene in the hero, a drift that never settles (AT-23)", () => {
    render(<NotFound />);
    const hero = screen.getByRole("region", { name: "Page not found" });
    expect(hero.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(1);
    expect(document.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(1);
  });

  it("gives the buttons Go to Week 8, to the latest week, and Go Home", () => {
    render(<NotFound />);
    const main = screen.getByRole("main");
    expect(within(main).getByRole("link", { name: "Go to Week 8" }).getAttribute("href")).toBe("/2026/week-08/");
    expect(within(main).getByRole("link", { name: "Go Home" }).getAttribute("href")).toBe("/");
  });

  it("shows the top band and the dock with no item marked", () => {
    render(<NotFound />);
    expect(screen.getByRole("banner")).toBeTruthy();
    const dock = screen.getByRole("navigation", { name: "Bottom menu" });
    expect(within(dock).getAllByRole("link")).toHaveLength(5);
    expect(document.querySelector("[aria-current=page]")).toBeNull();
  });
});
