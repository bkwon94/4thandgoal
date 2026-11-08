/**
 * Tests for the motion of the hero scene: the scatter, the settle of about 1.9 s, the dust that stops at rest, and the drift.
 * They need no canvas, so they check the places that the canvas draws at each time after entry.
 */
import { describe, expect, it } from "vitest";
import { type HeroScene, placeLights } from "./scene-math";
import { REST_MS, SETTLE_MS, driftAt, dustAt, dustOf, linesAt, phaseAt, scatterOf, settleAt } from "./scene-motion";

/* A scene of twelve lights on a rising line, as the twelve scores of a week sorted low to high. */
const twelve: HeroScene = {
  lights: Array.from({ length: 12 }, (_, x) => ({ x, y: 80 + 4 * x, label: `Team ${x}`, tone: "bright" })),
  guides: [],
  margin: null,
  restIndex: 11,
  mode: "settle",
};

const box = { width: 343, height: 200, padding: 16 };
const chart = placeLights(twelve, box);
const start = scatterOf(chart.length, box, 1);

/* The mean distance in pixels from each place to its place in the chart. */
function offChart(points: { x: number; y: number }[]): number {
  return points.reduce((sum, point, index) => sum + Math.hypot(point.x - chart[index].x, point.y - chart[index].y), 0) / points.length;
}

const insideBox = (point: { x: number; y: number }) =>
  point.x >= 0 && point.x <= box.width && point.y >= 0 && point.y <= box.height;

describe("the scatter", () => {
  it("starts each light inside the box and away from its place in the chart", () => {
    expect(start).toHaveLength(12);
    expect(start.every(insideBox)).toBe(true);
    expect(offChart(start)).toBeGreaterThan(40);
  });

  it("is the same for the same seed, so a replay of one scene starts from a known place", () => {
    expect(scatterOf(12, box, 1)).toEqual(start);
    expect(scatterOf(12, box, 2)).not.toEqual(start);
  });
});

describe("the settle", () => {
  it("draws the scatter at entry", () => {
    expect(settleAt(start, chart, 0)).toEqual(start);
  });

  it("is not in the chart at 0.5 s, and is in the chart at 1.9 s (AT-16)", () => {
    expect(offChart(settleAt(start, chart, 500))).toBeGreaterThan(10);
    expect(SETTLE_MS).toBe(1900);
    expect(settleAt(start, chart, SETTLE_MS)).toEqual(chart);
    expect(settleAt(start, chart, SETTLE_MS + 5000)).toEqual(chart);
  });

  it("eases out: the lights cover most of the way in the first half", () => {
    const half = offChart(settleAt(start, chart, SETTLE_MS / 2));
    expect(half).toBeLessThan(offChart(start) / 4);
  });

  it("draws the lines after the lights settle, and comes to rest by 2.2 s", () => {
    expect(linesAt(SETTLE_MS)).toBe(0);
    expect(linesAt(REST_MS)).toBe(1);
    expect(REST_MS).toBeLessThanOrEqual(2200);
    expect(phaseAt(SETTLE_MS)).toBe("settle");
    expect(phaseAt(REST_MS)).toBe("rest");
  });
});

describe("the dust", () => {
  const dust = dustOf(60, box, 1);

  it("holds 40 to 80 points inside the box", () => {
    expect(dust.length).toBeGreaterThanOrEqual(40);
    expect(dust.length).toBeLessThanOrEqual(80);
    expect(dustAt(dust, box, 0).every(insideBox)).toBe(true);
  });

  it("moves during the settle and stops at rest", () => {
    expect(dustAt(dust, box, 1000)).not.toEqual(dustAt(dust, box, 0));
    expect(dustAt(dust, box, REST_MS + 3000)).toEqual(dustAt(dust, box, REST_MS));
  });

  it("keeps moving when the scene has no rest, as a drift", () => {
    expect(dustAt(dust, box, 6000, Infinity)).not.toEqual(dustAt(dust, box, 2000, Infinity));
    expect(dustAt(dust, box, 6000, Infinity).every(insideBox)).toBe(true);
  });
});

describe("the drift", () => {
  it("moves the lights the whole time and keeps them inside the box (AT-20, AT-23)", () => {
    const at2 = driftAt(start, box, 2000);
    const at6 = driftAt(start, box, 6000);
    expect(at6).not.toEqual(at2);
    expect([...at2, ...at6].every(insideBox)).toBe(true);
  });
});
