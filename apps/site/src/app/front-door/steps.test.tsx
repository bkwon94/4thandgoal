/**
 * Tests for the one step pattern of every wait: the braille spinner on the live step, the check on a done step, the
 * static dot under reduced motion, the one first line, and the one "…" of a live line.
 */
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { act, cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { spinners } from "unicode-animations";

/* The test sets the reduced-motion switch for each case. */
const motion = vi.hoisted(() => ({ off: false }));
vi.mock("@cpc/design/hooks/use-motion-off", () => ({ useMotionOff: () => motion.off }));

const { FIRST_LINE, Steps } = await import("./steps");

const BRAILLE = spinners.braille.frames;

beforeEach(() => {
  motion.off = false;
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
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
    act(() => vi.advanceTimersByTime(80));
    expect(markOf(step)?.textContent).toBe(BRAILLE[1]);
    act(() => vi.advanceTimersByTime(80 * 9));
    expect(markOf(step)?.textContent).toBe(BRAILLE[0]);
  });

  it("shows a check on a done step, with no spinner and no timer", () => {
    render(<Steps steps={[{ line: "Reading the standings", done: true }]} live />);
    const [step] = items();
    expect(step.getAttribute("data-state")).toBe("done");
    expect(markOf(step)?.textContent).toBe("✔");
    expect(vi.getTimerCount()).toBe(0);
  });

  it("shows a static dot on the live step under reduced motion, and runs no frame timer", () => {
    motion.off = true;
    render(<Steps steps={[{ line: "Reading the standings", done: false }]} live />);
    const [step] = items();
    expect(markOf(step)?.textContent).toBe("");
    expect(markOf(step)?.getAttribute("data-dot")).toBe("");
    expect(vi.getTimerCount()).toBe(0);
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
