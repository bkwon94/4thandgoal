/**
 * Tests for the art of the sim Announcement with the reduced-motion media query on (AT-61): the rows and the odds show at
 * once, and the chip does not turn on by itself. matchMedia is a stub that must exist before Framer Motion first reads it.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { weekSim } from "../fixtures/sim";
import { previewOf } from "./preview";
import { AUTO_WHAT_IF_MS, SimPreview } from "./sim-preview";

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

beforeEach(() => {
  vi.useFakeTimers();
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
});
afterAll(() => {
  vi.unstubAllGlobals();
});

const BO_GIRDS = 6;
const chip = () => screen.getByRole("button", { name: /^What-if:/ });

describe("the art of the sim Announcement with reduced motion (AT-61)", () => {
  it("shows each row and the odds at rest on the first frame, with no count", () => {
    render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS} settled={false} />);
    const list = screen.getByRole("list", { name: "Standings near your team" });
    // The odds of Bo Girds show 58 on the first frame, in the row and in the header.
    expect(within(list).getAllByRole("listitem")[1].textContent).toBe("6Bo Girds58%Playoff line");
    for (const element of list.querySelectorAll<HTMLElement>("*")) {
      expect(element.style.opacity === "" || element.style.opacity === "1").toBe(true);
      expect(element.style.transform ?? "").not.toMatch(/translate/);
    }
  });

  it("does not turn the chip on by itself after the sheet settles", () => {
    render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS} settled />);
    act(() => vi.advanceTimersByTime(AUTO_WHAT_IF_MS * 10));
    expect(chip().getAttribute("aria-pressed")).toBe("false");
  });

  it("still turns the chip on with a tap, and shows the new odds at once", () => {
    render(<SimPreview data={previewOf(weekSim)} you={BO_GIRDS} settled />);
    fireEvent.click(chip());
    const list = screen.getByRole("list", { name: "Standings near your team" });
    expect(within(list).getAllByRole("listitem")[1].textContent).toBe("6Bo Girds86%Playoff line");
    expect(screen.getByRole("status").textContent).toBe("Playoff odds 86%");
  });
});
