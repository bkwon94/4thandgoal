/**
 * Tests for the stage lines with the reduced-motion media query on: the line still changes every 2.5 s, with no shimmer and no outgoing copy,
 * and a long line wraps in full and does not scroll.
 * matchMedia is a stub, and it must exist before Framer Motion first reads it, so the stub runs at the top of the file.
 */
import { act, cleanup, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { StageLines } from "./stage-lines";

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

const LINES = ["Line one", "Line two", "Line three"];

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

describe("StageLines with motion off", () => {
  it("changes the line every 2.5 s with no shimmer and no outgoing copy", () => {
    const { container } = render(<StageLines lines={LINES} />);
    for (const expected of ["Line one", "Line two", "Line three", "Line two"]) {
      const texts = container.querySelectorAll(".t-think-text");
      // One line only, and it is the still kind: the CSS gives a still line no shimmer.
      expect(texts).toHaveLength(1);
      expect(texts[0].classList.contains("is-still")).toBe(true);
      expect(texts[0].textContent).toBe(expected);
      act(() => void vi.advanceTimersByTime(2500));
    }
  });

  it("wraps a line wider than its box to a second line, and does not scroll it", () => {
    // jsdom lays out nothing, so the test gives the widths a browser would measure: a 300 px box and a 470 px line.
    const client = Object.getOwnPropertyDescriptor(Element.prototype, "clientWidth")!;
    const scroll = Object.getOwnPropertyDescriptor(Element.prototype, "scrollWidth")!;
    Object.defineProperty(Element.prototype, "clientWidth", {
      configurable: true,
      get(this: HTMLElement) {
        return this.classList.contains("t-think") ? 300 : 0;
      },
    });
    Object.defineProperty(Element.prototype, "scrollWidth", {
      configurable: true,
      get(this: HTMLElement) {
        return this.classList.contains("t-think-text") ? 470 : 0;
      },
    });
    try {
      const { container } = render(<StageLines lines={["Checking Bhayshul Tuten's depth at running back", "Line two"]} />);
      const line = container.querySelector<HTMLElement>(".t-think-text")!;
      expect(line.classList.contains("is-scroll")).toBe(false);
      expect(line.style.getPropertyValue("--think-scroll")).toBe("");
      // The sizer holds one line of height. With motion off it is gone, so the still line sits in the flow and wraps.
      expect(container.querySelector(".t-think-sizer")).toBeNull();
    } finally {
      Object.defineProperty(Element.prototype, "clientWidth", client);
      Object.defineProperty(Element.prototype, "scrollWidth", scroll);
    }
  });
});
