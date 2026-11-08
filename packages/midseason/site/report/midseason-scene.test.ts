/**
 * Tests for the data of the midseason scene, built from the real midseason file of CPC 2026 week 8.
 * They check the order of the lights, the height of each at its season total, the flare, and the label at rest.
 */
import { describe, expect, it } from "vitest";
import { midseason } from "../fixtures/midseason";
import { midseasonScene } from "./midseason-scene";

describe("midseasonScene", () => {
  const scene = midseasonScene(midseason)!;

  it("has 12 lights in the order of the standings, from the leader on the left", () => {
    expect(scene.lights).toHaveLength(12);
    expect(scene.lights.map((light) => light.x)).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    expect(scene.lights[0].label).toBe("All You Need Is Love · 850.17");
    expect(scene.lights[11].label).toBe("NFC Least · 700.97");
    expect(scene.mode).toBe("settle");
  });

  it("puts each light at the height of the season total points of its team", () => {
    expect(scene.lights.map((light) => light.y)).toEqual([
      850.17, 909.55, 921.62, 918.99, 900.65, 871.19, 832.55, 885.98, 769.09, 793.58, 765.42, 700.97,
    ]);
  });

  it("flares the leader of the standings only, and shows its label at rest", () => {
    expect(scene.lights.map((light) => light.tone)).toEqual(["flare", ...Array(11).fill("bright")]);
    expect(scene.restIndex).toBe(0);
    expect(scene.guides).toEqual([]);
    expect(scene.margin).toBeNull();
  });

  it("has no scene for a report with no state chapter, as it has no standings", () => {
    const acts = midseason.acts.map((act) => ({ ...act, chapters: act.chapters.filter((chapter) => chapter.key !== "state") }));
    expect(midseasonScene({ ...midseason, acts })).toBeUndefined();
  });
});
