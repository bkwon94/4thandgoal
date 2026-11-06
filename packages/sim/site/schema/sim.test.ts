/**
 * Tests for the Zod schema of the sim file, on the real fixture from the sim of CPC 2026 week 8.
 * A change to the shape that the pipeline writes fails here first.
 */
import { describe, expect, it } from "vitest";
import json from "../fixtures/sim.json";
import { simSchema } from "./sim";

describe("the sim schema", () => {
  it("parses the real sim file of CPC week 8 with its 200 runs and the odds of 10,000 runs", () => {
    const sim = simSchema.parse(json);
    expect(sim.runs).toBe(10000);
    expect(sim.sample).toHaveLength(200);
    expect(sim.bracket_weeks).toEqual([15, 16, 17]);
    expect(sim.names[3]).toBe("Lil Fridge");
    expect(sim.teams[3].title).toBe(14.4);
    // A bracket week of a team with no game holds null.
    expect(sim.sample[0].scores[2].slice(-3)).toEqual([null, null, null]);
  });

  it("fails on a run with no champion", () => {
    const bad = structuredClone(json) as { sample: Record<string, unknown>[] };
    delete bad.sample[0].champion;
    expect(simSchema.safeParse(bad).success).toBe(false);
  });
});
