/**
 * Tests for the one step pattern of every wait: the braille spinner on the live step, the check on a done step, the
 * static dot under reduced motion, the one first line, and the one "…" of a live line.
 */
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { act, cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, jest, mock } from "bun:test";
import { spinners } from "unicode-animations";

/* The test sets the reduced-motion switch for each case, and each test sets it back to off at its end. */
const motion = { off: false };
mock.module("@cpc/design/hooks/use-motion-off", () => ({ useMotionOff: () => motion.off }));

const { FIRST_LINE, Steps } = await import("./steps");

const BRAILLE = spinners.braille.frames;

beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  motion.off = false;
  cleanup();
  jest.useRealTimers();
});

const items = () => within(screen.getByRole("list", { name: "Steps" })).getAllByRole("listitem");
const lineOf = (item: HTMLElement) => item.querySelector("[data-line]")?.textContent;
const markOf = (item: HTMLElement) => item.querySelector("[data-mark]");

describe("Steps", () => {
  it("shows the braille spinner on the live step, one frame each 80 ms", () => {
    render(<Steps steps={[{ line: "Reading the standings", done: false }]} live />);
    const [step] = items();
    expect(step.getAttribute("data-state")).toBe("live");
    expect(markOf(step)?.textContent).toBe(BRAILLE[0]);
    act(() => jest.advanceTimersByTime(80));
    expect(markOf(step)?.textContent).toBe(BRAILLE[1]);
    act(() => jest.advanceTimersByTime(80 * 9));
    expect(markOf(step)?.textContent).toBe(BRAILLE[0]);
  });

  it("shows a check on a done step, with no spinner and no timer", () => {
    render(<Steps steps={[{ line: "Reading the standings", done: true }]} live />);
    const [step] = items();
    expect(step.getAttribute("data-state")).toBe("done");
    expect(markOf(step)?.textContent).toBe("✔");
    // Framer Motion runs its frames on timers, so the check lets them end first. A spinner timer would still run.
    act(() => jest.advanceTimersByTime(1000));
    expect(jest.getTimerCount()).toBe(0);
  });

  it("shows a static dot on the live step under reduced motion, and runs no frame timer", () => {
    motion.off = true;
    render(<Steps steps={[{ line: "Reading the standings", done: false }]} live />);
    const [step] = items();
    expect(markOf(step)?.textContent).toBe("");
    expect(markOf(step)?.getAttribute("data-dot")).toBe("");
    act(() => jest.advanceTimersByTime(1000));
    expect(jest.getTimerCount()).toBe(0);
  });

  it("ends each live line in one ellipsis, and a done line in none", () => {
    render(
      <Steps
        steps={[
          { line: "Reading the standings", done: true },
          { line: "Reading week 1", done: false },
        ]}
        live
      />,
    );
    expect(items().map(lineOf)).toEqual(["Reading the standings", "Reading week 1…"]);
  });

  it("shows the one first line while no step has come", () => {
    render(<Steps steps={[]} live />);
    expect(FIRST_LINE).toBe("Reading the league");
    expect(items().map(lineOf)).toEqual(["Reading the league…"]);
  });

  it("shows no live mark and no first line once the wait ends", () => {
    const { container } = render(<Steps steps={[]} live={false} />);
    expect(container.textContent).toBe("");
    cleanup();
    render(<Steps steps={[{ line: "Reading the standings", done: false }]} live={false} />);
    expect(items()[0].getAttribute("data-state")).toBe("done");
    expect(lineOf(items()[0])).toBe("Reading the standings");
  });
});

describe("the front door code", () => {
  it("holds one Shimmer at most", () => {
    const folder = __dirname;
    const sources = readdirSync(folder)
      .filter((name) => name.endsWith(".tsx") && !name.endsWith(".test.tsx"))
      .map((name) => readFileSync(join(folder, name), "utf8"));
    // A copy of the sweep is the gradient text, whether in a named component or inline.
    expect(sources.join("\n").match(/bg-clip-text text-transparent/g) ?? []).toHaveLength(1);
    expect(sources.join("\n").match(/function Shimmer\b/g) ?? []).toHaveLength(1);
  });
});
