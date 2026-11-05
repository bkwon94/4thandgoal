/**
 * Tests for the 404 page, on the real generated client values of cpc and the real published weeks.
 * They read what a reader sees: the hero, the big 404, the line, the two buttons, and the shell with no item marked.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import NotFound from "./not-found";

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
    expect(within(hero).getByText("ERROR // PAGE NOT FOUND")).toBeTruthy();
    expect(within(hero).getByRole("heading", { level: 1, name: "404" })).toBeTruthy();
    expect(within(hero).getByText("This page does not exist. The link may be old, or the week is not out yet.")).toBeTruthy();
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
