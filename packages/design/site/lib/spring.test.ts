/**
 * Tests for the spring sampler of the Open card. It turns a damped spring into a CSS linear() curve.
 * They check the curve that a browser reads: its start, its end, and its small overshoot.
 */
import { describe, expect, it } from "vitest";
import { springCurve } from "./spring";

/* The stops of a linear() curve, as numbers. */
function stops(curve: string): number[] {
  const inner = /^linear\((.*)\)$/.exec(curve)?.[1];
  if (inner === undefined) throw new Error(`not a linear() curve: ${curve}`);
  return inner.split(",").map((stop) => Number(stop.trim()));
}

describe("springCurve", () => {
  it("returns a linear() curve that starts at 0 and ends at 1", () => {
    const values = stops(springCurve());
    expect(values[0]).toBe(0);
    expect(values.at(-1)).toBe(1);
    expect(values.every(Number.isFinite)).toBe(true);
  });

  it("overshoots a little past 1 and settles, so the card lands on a spring", () => {
    const peak = Math.max(...stops(springCurve()));
    expect(peak).toBeGreaterThan(1);
    expect(peak).toBeLessThan(1.1);
  });

  it("has no overshoot with no bounce", () => {
    expect(Math.max(...stops(springCurve({ bounce: 0 })))).toBe(1);
  });

  it("takes one stop more than the count of steps", () => {
    expect(stops(springCurve({ steps: 24 }))).toHaveLength(25);
  });
});
