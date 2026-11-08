/**
 * Tests for the data of the Matchup scene, built from the real week 8 page of CPC.
 * They check the lights, the median guide, the flare, the label at rest, and the margin mark that the hero draws.
 */
import { describe, expect, it } from "vitest";
import {
  type SceneRect,
  estimateTextSize,
  placeLabel,
  placeLights,
  placeMarginMark,
} from "@cpc/design/parts/scene-math";
import { week8 } from "../fixtures/week-page";
import { matchupScene } from "./matchup-scene";

describe("matchupScene", () => {
  const scene = matchupScene(week8);

  it("has one light per team of the week, sorted from low to high by the points of the week", () => {
    expect(scene.lights).toHaveLength(12);
    const ys = scene.lights.map((light) => light.y);
    expect(ys).toEqual([...ys].sort((a, b) => a - b));
    expect(scene.lights.map((light) => light.x)).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    expect(scene.mode).toBe("settle");
  });

  it("draws the league median of 99.60 as its one guide", () => {
    expect(scene.guides).toHaveLength(1);
    expect(scene.guides[0].label).toBe("MEDIAN 99.60");
    expect(scene.guides[0].points.map((point) => point.y)).toEqual([99.6, 99.6]);
  });

  it("draws no guide for a week with no median, as a league with no median game publishes", () => {
    expect(matchupScene({ ...week8, median: null }).guides).toEqual([]);
  });

  it("flares the two teams of the Matchup, The Blue Tent and London Cooking, and no other team", () => {
    const flares = scene.lights.filter((light) => light.tone === "flare").map((light) => light.label);
    expect(flares.sort()).toEqual(["London Cooking · 98.88", "The Blue Tent · 100.31"]);
  });

  it("shows the label of the winner at rest, and marks the margin of +1.43 between the two teams", () => {
    expect(scene.restIndex).not.toBeNull();
    expect(scene.lights[scene.restIndex!].label).toBe("The Blue Tent · 100.31");
    expect(scene.margin?.text).toBe("+1.43");
    const ends = [scene.margin!.from, scene.margin!.to].map((index) => scene.lights[index].label);
    expect(ends).toEqual(["The Blue Tent · 100.31", "London Cooking · 98.88"]);
  });
});

/* True when two rectangles share any area. Rectangles that only touch at an edge do not overlap. */
function overlaps(a: SceneRect, b: SceneRect): boolean {
  return a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
}

describe("the labels of week 8", () => {
  it("flips the label of the top score, at the right edge, to the inner side and keeps it inside the box", () => {
    const scene = matchupScene(week8);
    const box = { width: 343, height: 200, padding: 16 };
    const top = scene.lights.length - 1;
    expect(scene.lights[top].label).toBe("Teehee · 134.10");
    const label = placeLabel(placeLights(scene, box)[top], estimateTextSize(scene.lights[top].label), box);
    expect(label.side).toBe("left");
    expect(label.x).toBeGreaterThanOrEqual(0);
    expect(label.x + label.width).toBeLessThanOrEqual(box.width);
  });
});

describe("the margin mark of week 8", () => {
  const scene = matchupScene(week8);
  const margin = scene.margin!;

  // The band of the scene on a phone of 375px, and the open middle of the hero at the laptop width.
  it.each([
    { width: 343, height: 200, padding: 16 },
    { width: 1100, height: 320, padding: 24 },
  ])("overlaps no label of the two teams in a box of $width by $height, also while the winner is selected", (box) => {
    const points = placeLights(scene, box);
    // The label at rest is the label of the winner. A tap on the winner or on the loser shows that label too.
    const labels = [margin.from, margin.to].map((index) =>
      placeLabel(points[index], estimateTextSize(scene.lights[index].label), box),
    );
    const mark = placeMarginMark(points, margin, estimateTextSize(margin.text), labels, box);
    expect(mark).not.toBeNull();
    for (const label of labels) expect(overlaps(mark!, label)).toBe(false);
    expect(mark!.x).toBeGreaterThanOrEqual(0);
    expect(mark!.y).toBeGreaterThanOrEqual(0);
    expect(mark!.x + mark!.width).toBeLessThanOrEqual(box.width);
    expect(mark!.y + mark!.height).toBeLessThanOrEqual(box.height);
  });
});
