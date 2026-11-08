/**
 * Tests for the data of the rankings scene, built from the real rankings file of CPC at week 6.
 * They check the order of the lights, the height of each at its playoff odds, the flare, and the label at rest.
 */
import { describe, expect, it } from "vitest";
import { layoutScene } from "@cpc/design/parts/scene-math";
import { rankings } from "../fixtures/rankings";
import { rankingsScene } from "./rankings-scene";

const week = rankings.weeks.at(-1)!;

describe("rankingsScene", () => {
  const scene = rankingsScene(week)!;

  it("has 12 lights in the order of the power rank, from rank 1 on the left", () => {
    expect(scene.lights).toHaveLength(12);
    expect(scene.lights.map((light) => light.x)).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    expect(scene.lights[0].label).toBe("London Cooking · 97%");
    expect(scene.lights[11].label).toBe("Pukancun on 3 · Out");
    expect(scene.mode).toBe("settle");
  });

  it("puts each light at the height of its playoff odds, a clinched team at 100 and a team that is out at 0", () => {
    expect(scene.lights.map((light) => light.y)).toEqual([97, 100, 89, 71, 66, 48, 41, 37, 11, 8, 3, 0]);
    expect(scene.lights[1].label).toBe("Lil Fridge · In");
  });

  it("flares the rank-1 team only, and shows its label at rest", () => {
    expect(scene.lights.map((light) => light.tone)).toEqual(["flare", ...Array(11).fill("bright")]);
    expect(scene.restIndex).toBe(0);
    expect(scene.guides).toEqual([]);
    expect(scene.margin).toBeNull();
  });

  it("keeps the label at rest inside the scene on a phone", () => {
    const box = { width: 343, height: 200, padding: 16 };
    const label = layoutScene(scene, box).labels[0];
    expect(label.x).toBeGreaterThanOrEqual(0);
    expect(label.x + label.width).toBeLessThanOrEqual(box.width);
  });

  it("has no scene for a week from before the odds engine ran, as no light has a height", () => {
    const rows = week.rows.map(({ odds: _odds, ...row }) => row);
    expect(rankingsScene({ ...week, rows })).toBeUndefined();
  });
});
