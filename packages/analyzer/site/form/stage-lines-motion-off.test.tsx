/**
 * Tests for the stage lines with the reduced-motion media query on: the line still changes every 2.5 s, with no shimmer and no outgoing copy.
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
});
