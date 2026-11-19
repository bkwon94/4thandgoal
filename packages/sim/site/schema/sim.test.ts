/**
 * Tests for the Zod schemas of the sim files, on the real season file of CPC 2026 week 8 and the real week file of
 * CPC 2026 week 10. A change to the shape that the pipeline writes fails here first.
 */
import { describe, expect, it } from "vitest";
import json from "../fixtures/sim.json";
import weekJson from "../fixtures/week-sim.json";
import { simSchema, weekSimSchema } from "./sim";

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

describe("the week sim schema", () => {
  it("parses the real week-10/sim.json of CPC with a page for each team", () => {
    const sim = weekSimSchema.parse(weekJson);
    expect([sim.week, sim.runs, sim.effective_runs]).toEqual([10, 10000, 10000]);
    expect(sim.sample).toHaveLength(200);
    expect(sim.sample_weights).toHaveLength(200);
    expect(Object.keys(sim.pages)).toHaveLength(12);
    // Bo Girds, roster 6, plays Maye d'force B with U, roster 9, in week 11, with four results.
    const week = sim.pages[6].weeks[0];
    expect(sim.names[week.opponent]).toBe("Maye d'force B with U");
    expect(week.results.map((r) => r.wins_added)).toEqual([2, 1, 1, 0]);
    expect(sim.pages[6].ladder).toHaveLength(9);
    expect(sim.fact).toMatch(/managers fight for the last/);
  });

  it("fails on a root-for row with a reason that is not one of the five", () => {
    const bad = structuredClone(weekJson) as { pages: Record<string, { weeks: { root_for: { reason: string }[] }[] }> };
    bad.pages["6"].weeks[0].root_for[0].reason = "Out of nowhere";
    expect(weekSimSchema.safeParse(bad).success).toBe(false);
  });
});
