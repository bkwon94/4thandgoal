/**
 * Tests for the egg word slider with the reduced-motion media query on: a tap on a tab changes the slide at once, with no
 * roll, no blur, and no letter swap. matchMedia is a stub, and it must exist before Framer Motion first reads it.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { boardWith } from "../lib/fixtures/eggs-api";
import { EggBoard } from "./egg-board";

vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      // Framer Motion asks for "(prefers-reduced-motion)" with no value, so the stub matches the feature name.
      matches: query.includes("prefers-reduced-motion"),
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList,
);

afterEach(cleanup);
afterAll(() => vi.unstubAllGlobals());

// One hour after the claim of the fixture.
const NOW = new Date("2026-10-19T13:00:00-04:00");

/* The board of AT-22: Lil Fridge holds five letters of EAGLES and two of CORNERSTONE, and no manager holds a letter of LANSDALE. */
const close = boardWith({ EAGLES: { 3: ["E", "A", "G", "L", "S"] }, CORNERSTONE: { 3: ["C", "O"] } });

describe("The egg word slider with reduced motion", () => {
  it("changes the slide at once on a tap of a tab, with no roll, no blur, and no letter swap", () => {
    render(<EggBoard board={close} now={NOW} />);
    fireEvent.click(screen.getByRole("tab", { name: "LANSDALE 0/8" }));
    // No wait: the slide of LANSDALE shows in the same render as the tap.
    const panel = screen.getByRole("tabpanel");
    expect(within(panel).getByRole("heading", { level: 2, name: "LANSDALE" })).toBeTruthy();
    expect(panel.textContent).toContain("No letters yet. The race is open.");
    // Every duration and every delay of the slider is 0, so the roll, the blur, and the letter swap end at once.
    const slider = panel.closest<HTMLElement>("[data-slider]")!;
    expect(slider.style.getPropertyValue("--es-dur")).toBe("0s");
    expect(slider.style.getPropertyValue("--es-on")).toBe("0");
  });
});
