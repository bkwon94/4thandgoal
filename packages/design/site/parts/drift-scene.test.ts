/**
 * Tests for the data of the drift scene, the scatter of lights that never settles, as on the 404 page.
 * They check the mode, the count of lights, and that the scene shows no label, no guide, and no margin mark.
 */
import { describe, expect, it } from "vitest";
import { driftScene } from "./drift-scene";
import { layoutScene } from "./scene-math";

describe("driftScene", () => {
  const scene = driftScene;

  it("never settles, so the lights drift the whole time (AT-23)", () => {
    expect(scene.mode).toBe("drift");
  });

  it("has 12 lights with no label, and no guide, no margin mark, and no label at rest", () => {
    expect(scene.lights).toHaveLength(12);
    expect(scene.lights.every((light) => light.label === "")).toBe(true);
    expect(scene.guides).toEqual([]);
    expect(scene.margin).toBeNull();
    expect(scene.restIndex).toBeNull();
  });

  it("has no flare, and mixes bright and dim lights, so the scatter has depth", () => {
    const tones = new Set(scene.lights.map((light) => light.tone));
    expect(tones).toEqual(new Set(["bright", "dim"]));
  });

  it("lays out inside a phone box with no error", () => {
    const layout = layoutScene(scene, { width: 343, height: 200, padding: 16 });
    expect(layout.points).toHaveLength(12);
    expect(layout.mark).toBeNull();
  });
});
