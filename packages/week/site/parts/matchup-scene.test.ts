/**
 * Tests for the data of the Matchup scene, built from the real week 8 page of CPC.
 * They check the lights, the median guide, the flare, the label at rest, and the margin mark that the hero draws.
 */
import { describe, expect, it } from "vitest";
import {
  type SceneRect,
  HINT_TEXT,
  estimateTextSize,
  layoutScene,
  placeLabel,
  placeLightLabel,
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
    expect(scene.lights[top].label).toBe("Teehee · 134.1");
    const label = placeLabel(placeLights(scene, box)[top], estimateTextSize(scene.lights[top].label), box);
    expect(label.side).toBe("left");
    expect(label.x).toBeGreaterThanOrEqual(0);
    expect(label.x + label.width).toBeLessThanOrEqual(box.width);
  });
});

describe("the labels of the Matchup of week 8", () => {
  const scene = matchupScene(week8);
  const margin = scene.margin!;

  // The band of the scene on a phone of 375px, inside the gutter and the side space of the hero, then a wider phone,
  // the open middle at the tablet width, and a box of 1100px, where the label of London Cooking once covered the
  // light of The Blue Tent. The labels take the width of the mono font, about 0.6 of 12px per character.
  it.each([
    { width: 293, height: 200, padding: 16 },
    { width: 343, height: 200, padding: 16 },
    { width: 590, height: 240, padding: 16 },
    { width: 1100, height: 320, padding: 24 },
  ])("cover no light of the scene in a box of $width by $height", (box) => {
    const points = placeLights(scene, box);
    for (const index of [margin.from, margin.to]) {
      const label = placeLightLabel(points, index, estimateTextSize(scene.lights[index].label), box);
      const covered = points.filter((point, other) => other !== index && overlaps(label, around(point)));
      expect(covered, scene.lights[index].label).toEqual([]);
      expect(label.x).toBeGreaterThanOrEqual(0);
      expect(label.y).toBeGreaterThanOrEqual(0);
      expect(label.x + label.width).toBeLessThanOrEqual(box.width);
      expect(label.y + label.height).toBeLessThanOrEqual(box.height);
    }
  });
});

/* The square that a light takes, as the margin mark keeps clear of it: 6px on each side of its center. */
function around(point: { x: number; y: number }): SceneRect {
  return { x: point.x - 6, y: point.y - 6, width: 12, height: 12 };
}

describe("the margin mark of week 8", () => {
  const scene = matchupScene(week8);
  const margin = scene.margin!;

  // The band of the scene on a phone of 375px, and the open middle of the hero at the laptop width.
  it.each([
    { width: 293, height: 200, padding: 16 },
    { width: 343, height: 200, padding: 16 },
    { width: 590, height: 240, padding: 16 },
    { width: 1100, height: 320, padding: 24 },
  ])("overlaps no label of the two teams in a box of $width by $height, also while the winner is selected", (box) => {
    const points = placeLights(scene, box);
    // The label at rest is the label of the winner. A tap on the winner or on the loser shows that label too.
    // The canvas places each label clear of the other lights, so the test takes the same place.
    const labels = [margin.from, margin.to].map((index) =>
      placeLightLabel(points, index, estimateTextSize(scene.lights[index].label), box),
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

describe("the layout of the scene of week 8", () => {
  const scene = matchupScene(week8);
  const boxes = [
    { width: 293, height: 200, padding: 16 },
    { width: 343, height: 200, padding: 16 },
    { width: 590, height: 240, padding: 16 },
  ];

  it.each(boxes)("keeps one margin mark, from the labels of its two ends, in a box of $width", (box) => {
    const layout = layoutScene(scene, box);
    const margin = scene.margin!;
    const ends = [margin.from, margin.to].map((index) => layout.labels[index]);
    expect(layout.mark).not.toBeNull();
    for (const label of ends) expect(overlaps(layout.mark!, label)).toBe(false);
  });

  it.each(boxes)("puts the hint in a corner with no light, no label at rest, no mark, and no guide label, in a box of $width", (box) => {
    const layout = layoutScene(scene, box);
    const hint = layout.hint!;
    expect(hint).not.toBeNull();
    expect(hint.width).toBe(estimateTextSize(HINT_TEXT).width);
    const blocked = [
      ...layout.points.map(around),
      layout.labels[scene.restIndex!],
      layout.mark!,
      ...layout.guideLabels,
    ];
    expect(blocked.filter((rect) => overlaps(hint, rect))).toEqual([]);
    expect(hint.x).toBeGreaterThanOrEqual(0);
    expect(hint.y).toBeGreaterThanOrEqual(0);
    expect(hint.x + hint.width).toBeLessThanOrEqual(box.width);
    expect(hint.y + hint.height).toBeLessThanOrEqual(box.height);
  });

  it.each(boxes)("labels the median line at one end, clear of every light, the label at rest, and the mark, in a box of $width", (box) => {
    const layout = layoutScene(scene, box);
    expect(layout.guideLabels).toHaveLength(1);
    const [label] = layout.guideLabels;
    const blocked = [...layout.points.map(around), layout.labels[scene.restIndex!], layout.labels[scene.margin!.to], layout.mark!];
    expect(blocked.filter((rect) => overlaps(label, rect))).toEqual([]);
    expect(label.x).toBeGreaterThanOrEqual(0);
    expect(label.x + label.width).toBeLessThanOrEqual(box.width);
    // The label sits directly over or under the line, so it reads as the name of the line.
    const line = layout.guides[0].points[0].y;
    expect(Math.min(Math.abs(label.y + label.height - line), Math.abs(label.y - line))).toBeLessThanOrEqual(4);
  });
});
