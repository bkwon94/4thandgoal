/**
 * Tests for the pure math of the hero scene: the place of each light, the nearest light, the side of a label, and
 * the place of the margin mark. They need no canvas, so they check the numbers that the canvas draws.
 */
import { describe, expect, it } from "vitest";
import {
  type HeroScene,
  nearestLight,
  placeGuides,
  placeLabel,
  placeLights,
  placeMarginMark,
} from "./scene-math";

/* A small scene of three lights. Each test that needs real data reads the week 8 fixture in the week package. */
const three: HeroScene = {
  lights: [
    { x: 0, y: 10, label: "Low", tone: "dim" },
    { x: 1, y: 20, label: "Mid", tone: "bright" },
    { x: 2, y: 30, label: "High", tone: "flare" },
  ],
  guides: [],
  margin: null,
  restIndex: 2,
  mode: "settle",
};

const box = { width: 300, height: 200, padding: 20 };

describe("placeLights", () => {
  it("spreads the lights across the box inside the padding, with the high value at the top", () => {
    const points = placeLights(three, box);
    expect(points).toEqual([
      { x: 20, y: 180 },
      { x: 150, y: 100 },
      { x: 280, y: 20 },
    ]);
  });
});

describe("placeGuides", () => {
  it("places a guide on the same scale as the lights, so a median line runs at its value", () => {
    const withMedian: HeroScene = {
      ...three,
      guides: [{ label: "MEDIAN 20", points: [{ x: 0, y: 20 }, { x: 2, y: 20 }] }],
    };
    expect(placeGuides(withMedian, box)).toEqual([
      { label: "MEDIAN 20", points: [{ x: 20, y: 100 }, { x: 280, y: 100 }] },
    ]);
  });

  it("widens the scale to hold a guide outside the range of the lights", () => {
    const withHigh: HeroScene = { ...three, guides: [{ label: "TOP", points: [{ x: 0, y: 50 }, { x: 2, y: 50 }] }] };
    expect(placeGuides(withHigh, box)[0].points[0].y).toBe(20);
    expect(placeLights(withHigh, box)[2].y).toBeGreaterThan(20);
  });
});

describe("nearestLight", () => {
  const points = placeLights(three, box);

  it("selects the closest light for a tap in empty space, so no tap misses", () => {
    // The tap sits far from each light, nearest to the middle light at (150, 100).
    expect(nearestLight(points, { x: 170, y: 160 })).toBe(1);
    // A tap at the left edge or in the top right corner still selects a light.
    expect(nearestLight(points, { x: 0, y: 120 })).toBe(0);
    expect(nearestLight(points, { x: 299, y: 0 })).toBe(2);
  });

  it("selects no light in a scene with no light", () => {
    expect(nearestLight([], { x: 10, y: 10 })).toBeNull();
  });
});

describe("placeLabel", () => {
  const size = { width: 120, height: 16 };

  it("puts a label on the right side of its light when it fits", () => {
    const label = placeLabel({ x: 40, y: 100 }, size, box);
    expect(label.side).toBe("right");
    expect(label.x).toBeGreaterThan(40);
  });

  it("flips a label near the right edge to the inner side, and keeps it inside the box", () => {
    const label = placeLabel({ x: 280, y: 100 }, size, box);
    expect(label.side).toBe("left");
    expect(label.x + label.width).toBeLessThan(280);
    expect(label.x).toBeGreaterThanOrEqual(0);
    expect(label.x + label.width).toBeLessThanOrEqual(box.width);
  });

  it("keeps a label at the top or the bottom edge inside the box", () => {
    expect(placeLabel({ x: 40, y: 2 }, size, box).y).toBeGreaterThanOrEqual(0);
    const low = placeLabel({ x: 40, y: 198 }, size, box);
    expect(low.y + low.height).toBeLessThanOrEqual(box.height);
  });
});

describe("placeMarginMark", () => {
  const points = placeLights(three, box);
  const margin = { from: 2, to: 1, text: "+10" };
  const size = { width: 30, height: 16 };

  it("moves the mark off a label that covers its first place", () => {
    const free = placeMarginMark(points, margin, size, [], box)!;
    const cover = { x: free.x - 5, y: free.y - 5, width: free.width + 10, height: free.height + 10 };
    const moved = placeMarginMark(points, margin, size, [cover], box)!;
    expect(moved).not.toEqual(free);
    const clear = moved.x >= cover.x + cover.width || moved.x + moved.width <= cover.x ||
      moved.y >= cover.y + cover.height || moved.y + moved.height <= cover.y;
    expect(clear).toBe(true);
  });

  it("gives no mark when a label covers the whole box", () => {
    expect(placeMarginMark(points, margin, size, [{ x: 0, y: 0, width: 300, height: 200 }], box)).toBeNull();
  });
});
