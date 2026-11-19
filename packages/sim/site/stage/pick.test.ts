/**
 * Tests for the pick of the stored run that the replay of the sim page plays: a run comes up with a chance in
 * proportion to its weight, and a run of weight 0 never comes up. The random number is a port, so each test sets it.
 */
import { describe, expect, it } from "vitest";
import { pickRun } from "./pick";

describe("the pick of a stored run", () => {
  it("cuts the line from 0 to 1 into one piece per run, as long as its weight", () => {
    // The weights 1, 0, and 3 cut the line at 0.25 and at 1: run 0 holds [0, 0.25), run 2 holds [0.25, 1).
    const weights = [1, 0, 3];
    expect(pickRun(weights, () => 0)).toBe(0);
    expect(pickRun(weights, () => 0.2)).toBe(0);
    expect(pickRun(weights, () => 0.25)).toBe(2);
    expect(pickRun(weights, () => 0.9999)).toBe(2);
  });

  it("never picks a run of weight 0", () => {
    const weights = [0, 2, 0, 2, 0];
    const picks = new Set(Array.from({ length: 100 }, (_, i) => pickRun(weights, () => i / 100)));
    expect([...picks].sort()).toEqual([1, 3]);
  });

  it("gives each run of equal weight the same share", () => {
    const weights = [1, 1, 1, 1];
    const counts = [0, 0, 0, 0];
    for (let i = 0; i < 400; i += 1) counts[pickRun(weights, () => i / 400)] += 1;
    expect(counts).toEqual([100, 100, 100, 100]);
  });
});
