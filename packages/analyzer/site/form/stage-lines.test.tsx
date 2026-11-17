/**
 * Tests for the stage lines part: one line shows, the line changes every 2.5 s, the list loops from line 2, and a screen reader hears none of it.
 * Fake timers drive the clock, and each test reads the screen.
 */
import { act, cleanup, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { StageLines } from "./stage-lines";

const LINES = ["Line one", "Line two", "Line three", "Line four"];

/* The text of the live line, which is the last line in the part. An outgoing line is still in the part for a moment. */
function shown(container: HTMLElement): string {
  const texts = container.querySelectorAll(".t-think-text");
  return texts[texts.length - 1].textContent ?? "";
}

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

describe("StageLines", () => {
  it("shows the first line, and the next line after each 2.5 s", () => {
    const { container } = render(<StageLines lines={LINES} />);
    expect(shown(container)).toBe("Line one");
    act(() => void vi.advanceTimersByTime(2500));
    expect(shown(container)).toBe("Line two");
    act(() => void vi.advanceTimersByTime(2500));
    expect(shown(container)).toBe("Line three");
  });

  it("shows 4 different lines in 10 s", () => {
    const { container } = render(<StageLines lines={LINES} />);
    const seen = new Set([shown(container)]);
    for (let i = 0; i < 4; i++) {
      act(() => void vi.advanceTimersByTime(2500));
      seen.add(shown(container));
    }
    expect(seen.size).toBe(4);
  });

  it("starts again at line 2 after the last line", () => {
    const { container } = render(<StageLines lines={LINES} />);
    const order: string[] = [];
    for (let i = 0; i < 6; i++) {
      act(() => void vi.advanceTimersByTime(2500));
      order.push(shown(container));
    }
    expect(order).toEqual(["Line two", "Line three", "Line four", "Line two", "Line three", "Line four"]);
  });

  it("hides every line from a screen reader", () => {
    const { container } = render(<StageLines lines={LINES} />);
    expect(container.firstElementChild?.getAttribute("aria-hidden")).toBe("true");
    act(() => void vi.advanceTimersByTime(2500));
    expect(container.firstElementChild?.getAttribute("aria-hidden")).toBe("true");
  });

  it("shimmers the line with motion on", () => {
    const { container } = render(<StageLines lines={LINES} />);
    expect(container.querySelector(".t-think-text.is-still")).toBeNull();
  });
});
