/**
 * Tests for the stage lines part: one line shows, the line changes every 2.5 s, the list loops from line 2, a screen reader hears none of it,
 * and a line wider than its box scrolls once to its end. Fake timers drive the clock, and each test reads the screen.
 */
import { act, cleanup, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { StageLines } from "./stage-lines";

const LINES = ["Line one", "Line two", "Line three", "Line four"];

// The width of the box in px, and the width of one character of a line. jsdom lays out nothing, so the test gives the
// geometry that a browser would measure: a line of 30 characters is 300 px wide and fills the box exactly.
const BOX_PX = 300;
const CHAR_PX = 10;
const FITS = "A line that fits in the box";
const LONG = "Checking Bhayshul Tuten's depth at running back";

/* Gives the box and each line the widths of a real layout, and puts back the jsdom values after the test. */
function layOut() {
  const client = Object.getOwnPropertyDescriptor(Element.prototype, "clientWidth")!;
  const scroll = Object.getOwnPropertyDescriptor(Element.prototype, "scrollWidth")!;
  Object.defineProperty(Element.prototype, "clientWidth", {
    configurable: true,
    get(this: HTMLElement) {
      return this.classList.contains("t-think") ? BOX_PX : 0;
    },
  });
  Object.defineProperty(Element.prototype, "scrollWidth", {
    configurable: true,
    get(this: HTMLElement) {
      return this.classList.contains("t-think-text") ? (this.textContent ?? "").length * CHAR_PX : 0;
    },
  });
  return () => {
    Object.defineProperty(Element.prototype, "clientWidth", client);
    Object.defineProperty(Element.prototype, "scrollWidth", scroll);
  };
}

/* The live line, which is the last line in the part. */
function live(container: HTMLElement): HTMLElement {
  const texts = container.querySelectorAll<HTMLElement>(".t-think-text");
  return texts[texts.length - 1];
}

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

  it("sets each line at text-body, one step smaller than text-lead", () => {
    const { container } = render(<StageLines lines={LINES} />);
    const box = container.firstElementChild!;
    expect(box.classList.contains("text-body")).toBe(true);
    expect(box.classList.contains("text-lead")).toBe(false);
  });

  describe("in a box of 300 px", () => {
    let putBack: () => void;
    beforeEach(() => {
      putBack = layOut();
    });
    afterEach(() => putBack());

    it("scrolls a line wider than the box from right to left until its end is in view", () => {
      const { container } = render(<StageLines lines={[LONG, FITS]} />);
      const line = live(container);
      expect(line.classList.contains("is-scroll")).toBe(true);
      // The line is 470 px wide, so it moves 170 px to the left, and its last character rests at the right edge.
      expect(line.style.getPropertyValue("--think-scroll")).toBe("-170px");
    });

    it("ends the scroll inside the 2.5 s of the line, with time to read the end", () => {
      const { container } = render(<StageLines lines={[LONG, FITS]} />);
      const line = live(container);
      const delay = parseInt(line.style.getPropertyValue("--think-scroll-delay"), 10);
      const time = parseInt(line.style.getPropertyValue("--think-scroll-time"), 10);
      // The start shows first, so the reader sees where the line begins. The end then rests for at least 0.5 s.
      expect(delay).toBeGreaterThanOrEqual(400);
      expect(delay + time).toBeLessThanOrEqual(2500 - 500);
    });

    it("does not move a line that fits", () => {
      const { container } = render(<StageLines lines={[FITS, LONG]} />);
      const line = live(container);
      expect(line.classList.contains("is-scroll")).toBe(false);
      expect(line.style.getPropertyValue("--think-scroll")).toBe("");
    });

    it("measures each new line, so a long line scrolls and the next line that fits stays still", () => {
      const { container } = render(<StageLines lines={[LONG, FITS]} />);
      expect(live(container).classList.contains("is-scroll")).toBe(true);
      act(() => void vi.advanceTimersByTime(2500));
      expect(live(container).textContent).toBe(FITS);
      expect(live(container).classList.contains("is-scroll")).toBe(false);
    });

    it("keeps the outgoing long line at its end, so it leaves from where the reader saw it", () => {
      const { container } = render(<StageLines lines={[LONG, FITS]} />);
      act(() => void vi.advanceTimersByTime(2500));
      const leaving = container.querySelector<HTMLElement>(".t-think-text.is-exit")!;
      expect(leaving.textContent).toBe(LONG);
      expect(leaving.style.getPropertyValue("translate")).toBe("-170px 0");
    });
  });

  describe("with a list of one line", () => {
    it("holds the line past 2.5 s until the caller sends the next line", () => {
      const { container } = render(<StageLines lines={["1 of 5 · Reading every team"]} />);
      act(() => void vi.advanceTimersByTime(20_000));
      expect(shown(container)).toBe("1 of 5 · Reading every team");
      expect(container.querySelector(".t-think-text.is-exit")).toBeNull();
    });

    it("swaps to the next line with the same motion as a timed line", () => {
      const { container, rerender } = render(<StageLines lines={["1 of 5 · Reading every team"]} />);
      rerender(<StageLines lines={["2 of 5 · Looking for players who fit"]} />);
      // The old line leaves and the new line starts in its enter state, as a timed swap does.
      expect(container.querySelector(".t-think-text.is-exit")?.textContent).toBe("1 of 5 · Reading every team");
      expect(live(container).textContent).toBe("2 of 5 · Looking for players who fit");
      expect(live(container).classList.contains("is-enter-start")).toBe(true);
      act(() => void vi.advanceTimersByTime(250));
      expect(container.querySelector(".t-think-text.is-exit")).toBeNull();
      expect(live(container).classList.contains("is-enter-start")).toBe(false);
    });

    it("does not swap when the caller sends the same line again", () => {
      const { container, rerender } = render(<StageLines lines={["1 of 5 · Reading every team"]} />);
      rerender(<StageLines lines={["1 of 5 · Reading every team"]} />);
      expect(container.querySelector(".t-think-text.is-exit")).toBeNull();
    });
  });

  it("shimmers the line with motion on", () => {
    const { container } = render(<StageLines lines={LINES} />);
    expect(container.querySelector(".t-think-text.is-still")).toBeNull();
  });
});
