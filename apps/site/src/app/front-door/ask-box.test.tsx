/**
 * Tests for the ask box and the dock of the shell: while the ask box has the focus, the on-screen keyboard is open, so
 * the dock tucks away, and it comes back on blur. jsdom has no keyboard, so a real phone run checks the place above it.
 */
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { TopBand } from "@cpc/design/shell/top-band";
import { AskBox } from "./ask-box";

/* jsdom has no matchMedia, and the theme button reads it. The stub matches no query. */
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

function renderDoor() {
  render(
    <>
      <TopBand
        title="Cornerstone Fantasy Football League"
        brand={{ home: "/", logo: null }}
        menu={{ items: [{ kind: "home", label: "Home", short: "Home", href: "/" }], weeks: [] }}
        pageHref="/"
      />
      <AskBox />
    </>,
  );
}

/* The tucked dock leaves the tab order and the accessibility tree, so the query reads it with hidden: true. */
const dock = () => screen.getByRole("navigation", { name: "Bottom menu", hidden: true });
const field = () => screen.getByRole("textbox", { name: "Ask a question" });

describe("AskBox and the dock", () => {
  it("shows the dock while the ask box has no focus", () => {
    renderDoor();
    expect(dock().hasAttribute("data-tucked")).toBe(false);
    expect(dock().hasAttribute("inert")).toBe(false);
  });

  it("tucks the dock away while the ask box has the focus", () => {
    renderDoor();
    act(() => field().focus());
    expect(dock().hasAttribute("data-tucked")).toBe(true);
    expect(dock().hasAttribute("inert")).toBe(true);
    expect(document.documentElement.hasAttribute("data-keyboard")).toBe(true);
  });

  it("brings the dock back when the ask box loses the focus", () => {
    renderDoor();
    act(() => field().focus());
    act(() => field().blur());
    expect(dock().hasAttribute("data-tucked")).toBe(false);
    expect(dock().hasAttribute("inert")).toBe(false);
    expect(document.documentElement.hasAttribute("data-keyboard")).toBe(false);
  });

  it("brings the dock back when the ask box leaves the page with the focus", () => {
    renderDoor();
    act(() => field().focus());
    cleanup();
    expect(document.documentElement.hasAttribute("data-keyboard")).toBe(false);
  });

  it("keeps the focus in the ask box when a question goes", () => {
    renderDoor();
    act(() => field().focus());
    fireEvent.change(field(), { target: { value: "Who should I start?" } });
    fireEvent.submit(screen.getByRole("form", { name: "Ask" }));
    expect(dock().hasAttribute("data-tucked")).toBe(true);
  });
});
