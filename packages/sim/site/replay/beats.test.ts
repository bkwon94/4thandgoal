/**
 * Tests for the beats of a replay: the order of the Broadcast motion and the length of a full run.
 * They read the real sim file of CPC 2026 week 8.
 */
import { describe, expect, it } from "vitest";
import { sim } from "../fixtures/sim";
import { beatsOf, runLength } from "./beats";
import { replaySeason } from "./season";

describe("the beats of a replay", () => {
  const beats = beatsOf(replaySeason(sim, 0));

  it("plays each regular week, the split, the final standings, each round, then the champion", () => {
    expect(beats.map((beat) => beat.kind)).toEqual([
      ...Array(6).fill("week"),
      "split",
      "final",
      "draw",
      "result",
      "draw",
      "result",
      "draw",
      "result",
      "champion",
    ]);
    expect(beats.filter((beat) => beat.kind === "week").map((beat) => beat.index)).toEqual([0, 1, 2, 3, 4, 5]);
    expect(beats.filter((beat) => beat.kind === "draw").map((beat) => beat.index)).toEqual([0, 1, 2]);
  });

  it("runs a full replay in about 20 seconds", () => {
    expect(runLength(beats)).toBeGreaterThanOrEqual(18_000);
    expect(runLength(beats)).toBeLessThanOrEqual(22_000);
  });
});
