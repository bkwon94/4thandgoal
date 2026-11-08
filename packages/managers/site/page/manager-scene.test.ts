/**
 * Tests for the data of the manager scene, built from the real managers file of CPC.
 * They check one light per played week, the tone of a win and a loss, the median of each week, and the label at rest.
 */
import { describe, expect, it } from "vitest";
import type { ManagerEntry } from "../schema/manager-types";
import { managers } from "../fixtures/managers";
import { managerScene } from "./manager-scene";

/* Roster 7 of the fixture, "To Infinity and Bijan", through week 6: a win in weeks 3 and 4, a loss in the others. */
const roster7 = managers.managers.find((entry) => entry.roster_id === 7)!;

describe("managerScene", () => {
  const scene = managerScene(roster7);

  it("has one light per played week, with x the week and y the points", () => {
    expect(scene.lights.map((light) => light.x)).toEqual([1, 2, 3, 4, 5, 6]);
    expect(scene.lights.map((light) => light.y)).toEqual([109.21, 96.1, 107.39, 118.28, 66.82, 46.08]);
    expect(scene.mode).toBe("settle");
    expect(scene.margin).toBeNull();
  });

  it("draws a win bright and a loss dim, with no flare", () => {
    expect(scene.lights.map((light) => light.tone)).toEqual(["dim", "dim", "bright", "bright", "dim", "dim"]);
  });

  it("labels each light with the week, the points, and the result, and shows the latest week at rest", () => {
    expect(scene.lights.map((light) => light.label)).toEqual([
      "Week 1 · 109.21 · L",
      "Week 2 · 96.1 · L",
      "Week 3 · 107.39 · W",
      "Week 4 · 118.28 · W",
      "Week 5 · 66.82 · L",
      "Week 6 · 46.08 · L",
    ]);
    expect(scene.restIndex).toBe(5);
  });

  it("draws the median of each week as its one guide, with one point per week", () => {
    expect(scene.guides).toHaveLength(1);
    expect(scene.guides[0].label).toBe("WEEK MEDIAN");
    expect(scene.guides[0].points).toEqual([
      { x: 1, y: 111.36 },
      { x: 2, y: 96.34 },
      { x: 3, y: 107.14 },
      { x: 4, y: 104.58 },
      { x: 5, y: 107.35 },
      { x: 6, y: 106.83 },
    ]);
  });

  it("draws no guide for a league with no median game", () => {
    const noMedian: ManagerEntry = { ...roster7, weeks: roster7.weeks.map((week) => ({ ...week, median: null })) };
    expect(managerScene(noMedian).guides).toEqual([]);
  });

  it("draws a week with no result, such as a tie, dim with a dash for its result", () => {
    const tie: ManagerEntry = { ...roster7, weeks: [{ week: 1, points: 100, median: 99, won: null }] };
    const [light] = managerScene(tie).lights;
    expect(light).toEqual({ x: 1, y: 100, label: "Week 1 · 100 · —", tone: "dim" });
  });

  it("has no light and no label at rest before the first played week", () => {
    const scene = managerScene({ ...roster7, weeks: [] });
    expect(scene.lights).toEqual([]);
    expect(scene.restIndex).toBeNull();
  });
});
