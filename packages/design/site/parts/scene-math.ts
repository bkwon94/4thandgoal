/**
 * The data shape of the hero scene and the pure math that the canvas draws from it (ADR 0027).
 * Each function takes plain numbers and returns plain numbers, so a test checks it with no canvas.
 */

/* Two decimals on every score, as "99.60", so the labels of every scene line up as a set. */
export function sceneScore(points: number): string {
  return points.toFixed(2);
}

/* The tone of a light. `flare` draws in the accent color, `bright` in `on-dark`, and `dim` in `on-dark-muted`. */
export type SceneTone = "flare" | "bright" | "dim";

/* One light of the scene. The x and y values are in the units of the data, such as a rank and the points. */
export type SceneLight = { x: number; y: number; label: string; tone: SceneTone };

/* A point in the units of the data, or in the pixels of the box after `placeLights`. */
export type ScenePoint = { x: number; y: number };

/* A guide line through two or more points in the units of the data, such as the league median, with its label. */
export type SceneGuide = { label: string; points: ScenePoint[] };

/* The margin mark between two lights, such as "+1.43". Each end is the index of a light. */
export type SceneMargin = { from: number; to: number; text: string };

/* `settle` draws the chart after the lights drift in. `drift` never settles, as on the 404 page. */
export type SceneMode = "settle" | "drift";

/* The plain data of one scene. The page builds it from the published files and passes it to the hero (ADR 0012). */
export type HeroScene = {
  lights: SceneLight[];
  guides: SceneGuide[];
  margin: SceneMargin | null;
  // The index of the light that shows its label at rest, or null for a scene with no label at rest.
  restIndex: number | null;
  mode: SceneMode;
};

/* The box of the scene in CSS pixels. No light sits closer to an edge than the padding. */
export type SceneBox = { width: number; height: number; padding: number };

/* The padding of the box of the canvas: 16px, so a light and the ring of a selected light stay inside the scene. */
export const SCENE_PADDING = 16;

/* The low and the high value of a list. A list of one value gets a span of one, so the scale never divides by zero. */
function rangeOf(values: number[]): { low: number; span: number } {
  const low = Math.min(...values);
  const high = Math.max(...values);
  return { low, span: high - low || 1 };
}

/*
 * The one scale of a scene, from the units of the data to the pixels of the box. The x value runs left to right and
 * the y value runs bottom to top. The ranges hold the lights and the guides, so a guide line never leaves the box.
 */
function scaleOf(scene: HeroScene, box: SceneBox): (point: ScenePoint) => ScenePoint {
  const all = [...scene.lights, ...scene.guides.flatMap((guide) => guide.points)];
  const xs = rangeOf(all.map((point) => point.x));
  const ys = rangeOf(all.map((point) => point.y));
  const inner = { width: box.width - 2 * box.padding, height: box.height - 2 * box.padding };
  return (point) => ({
    x: box.padding + ((point.x - xs.low) / xs.span) * inner.width,
    y: box.padding + (1 - (point.y - ys.low) / ys.span) * inner.height,
  });
}

/* The place in pixels of each light in the box, in the order of `scene.lights`. */
export function placeLights(scene: HeroScene, box: SceneBox): ScenePoint[] {
  const scale = scaleOf(scene, box);
  return scene.lights.map((light) => scale(light));
}

/* Each guide of the scene with its points in the pixels of the box, on the same scale as the lights. */
export function placeGuides(scene: HeroScene, box: SceneBox): SceneGuide[] {
  const scale = scaleOf(scene, box);
  return scene.guides.map((guide) => ({ label: guide.label, points: guide.points.map(scale) }));
}

/*
 * The index of the light closest to a point, such as a tap or the finger of a slide, or null with no light.
 * Any point in the scene selects a light, so no tap misses (story 30).
 */
export function nearestLight(points: ScenePoint[], at: ScenePoint): number | null {
  let best: number | null = null;
  let bestDistance = Infinity;
  points.forEach((point, index) => {
    const distance = Math.hypot(point.x - at.x, point.y - at.y);
    if (distance < bestDistance) {
      best = index;
      bestDistance = distance;
    }
  });
  return best;
}

/* The width and the height of a text or a mark in CSS pixels. The canvas gets it from `measureText`. */
export type SceneSize = { width: number; height: number };

/* A rectangle in the pixels of the box, from its top left corner. */
export type SceneRect = { x: number; y: number; width: number; height: number };

/* The side of its light that a label takes. */
export type LabelSide = "right" | "left";

/* The space in pixels between a light and its label. */
export const LABEL_GAP = 8;

/* A value held between a low and a high bound. A high bound under the low bound gives the low bound. */
function clamp(value: number, low: number, high: number): number {
  return Math.max(low, Math.min(value, high));
}

/*
 * The rectangle of the label of a light. The label sits on the right side of its light, centered on its height.
 * A label that runs past the right edge flips to the left side, and the box holds each label in full (story 35).
 */
export function placeLabel(
  point: ScenePoint,
  size: SceneSize,
  box: Pick<SceneBox, "width" | "height">,
): SceneRect & { side: LabelSide } {
  const side: LabelSide = point.x + LABEL_GAP + size.width > box.width ? "left" : "right";
  const x = side === "right" ? point.x + LABEL_GAP : point.x - LABEL_GAP - size.width;
  return {
    side,
    x: clamp(x, 0, box.width - size.width),
    y: clamp(point.y - size.height / 2, 0, box.height - size.height),
    width: size.width,
    height: size.height,
  };
}

/* The square that a light takes, with the space that a label or a mark keeps around it, so no text sits on a dot. */
function lightRect(point: ScenePoint): SceneRect {
  return {
    x: point.x - LIGHT_CLEARANCE,
    y: point.y - LIGHT_CLEARANCE,
    width: 2 * LIGHT_CLEARANCE,
    height: 2 * LIGHT_CLEARANCE,
  };
}

/*
 * The rectangle of the label of the light at `index`, clear of every other light. The label first takes the side of
 * `placeLabel`, then the other side, each level with its light, then under it, then over it. A label too long for
 * either side on a narrow phone then sits under or over its light, held inside the box, and slides along the row
 * until it is clear. Two close lights, such as
 * the two teams of a close Matchup, then never hide a dot under a label. The label takes the place of `placeLabel`
 * only when no place is clear.
 */
export function placeLightLabel(
  points: ScenePoint[],
  index: number,
  size: SceneSize,
  box: Pick<SceneBox, "width" | "height">,
): SceneRect & { side: LabelSide } {
  const point = points[index];
  const first = placeLabel(point, size, box);
  const others = points.filter((_, other) => other !== index).map(lightRect);
  const sides: LabelSide[] = first.side === "right" ? ["right", "left"] : ["left", "right"];
  const level = -size.height / 2;
  const under = LIGHT_CLEARANCE;
  const over = -LIGHT_CLEARANCE - size.height;
  const beside = sides.flatMap((side) =>
    [level, under, over].map((rise) => ({
      side,
      x: side === "right" ? point.x + LABEL_GAP : point.x - LABEL_GAP - size.width,
      y: point.y + rise,
    })),
  );
  // Under or over its light, the label never covers its own dot, so it may slide along the row. It starts centered on
  // the light and slides out by the gap in each step, then tries one row farther from the light.
  const centered = clamp(point.x - size.width / 2, 0, box.width - size.width);
  const slides: number[] = [];
  for (let x = 0; x <= box.width - size.width; x += LABEL_GAP) slides.push(x);
  slides.sort((a, b) => Math.abs(a - centered) - Math.abs(b - centered));
  const rows = [under, over, under + size.height, over - size.height];
  const around = rows.flatMap((rise) =>
    [centered, ...slides].map((x) => ({ side: first.side, x, y: point.y + rise })),
  );
  for (const place of [...beside, ...around]) {
    const label = { ...place, width: size.width, height: size.height };
    const inside = label.x >= 0 && label.y >= 0 && label.x + label.width <= box.width && label.y + label.height <= box.height;
    if (inside && !others.some((rect) => overlaps(label, rect))) return label;
  }
  return first;
}

/* The font of a label and of the margin mark: the mono meta size of 12px. */
export const LABEL_FONT_PX = 12;

/*
 * The size of a text in the mono font, from the count of its characters. A mono glyph is about 0.6 of the font size
 * wide. A test and the first frame before the font loads use it. The canvas uses `measureText` once it can.
 */
export function estimateTextSize(text: string, fontPx: number = LABEL_FONT_PX): SceneSize {
  return { width: Math.ceil(text.length * fontPx * 0.6), height: Math.ceil(fontPx * 1.4) };
}

/* True when two rectangles share any area. Rectangles that only touch at an edge do not overlap. */
function overlaps(a: SceneRect, b: SceneRect): boolean {
  return a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
}

/* The space in pixels that the mark keeps around each light, so the mark never sits on a dot. */
const LIGHT_CLEARANCE = 6;

/*
 * The rectangle of the margin mark, such as "+1.43", near the middle of its two lights and clear of every label in
 * `labels`. Pass the label at rest and the labels of the two ends, so the mark stays put when either end is selected.
 * The mark tries each place above, below, and beside the pair, from near to far, and takes the first that is clear.
 * It returns null only when no place in the box is clear.
 */
export function placeMarginMark(
  points: ScenePoint[],
  margin: SceneMargin,
  size: SceneSize,
  labels: SceneRect[],
  box: Pick<SceneBox, "width" | "height">,
): SceneRect | null {
  const a = points[margin.from];
  const b = points[margin.to];
  const middle = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  const top = Math.min(a.y, b.y);
  const bottom = Math.max(a.y, b.y);
  const left = Math.min(a.x, b.x);
  const right = Math.max(a.x, b.x);
  const blocked = [...labels, ...points.map(lightRect)];

  const step = size.height;
  const farthest = Math.max(box.width, box.height);
  for (let away = LABEL_GAP; away <= farthest; away += step) {
    const places: ScenePoint[] = [
      { x: middle.x - size.width / 2, y: top - away - size.height },
      { x: middle.x - size.width / 2, y: bottom + away },
      { x: left - away - size.width, y: middle.y - size.height / 2 },
      { x: right + away, y: middle.y - size.height / 2 },
    ];
    for (const place of places) {
      const mark = { ...place, width: size.width, height: size.height };
      const inside = mark.x >= 0 && mark.y >= 0 && mark.x + mark.width <= box.width && mark.y + mark.height <= box.height;
      if (inside && !blocked.some((rect) => overlaps(mark, rect))) return mark;
    }
  }
  return null;
}

/* The caption that tells a reader the scene takes a tap or a slide (story 33). */
export const HINT_TEXT = "TAP OR SLIDE";

/* The space in pixels between the hint and the corner of the box. */
const HINT_INSET = 8;

/* Everything that the canvas draws at rest, in the pixels of one box. The page box changes only on a resize. */
export type SceneLayout = {
  points: ScenePoint[];
  guides: SceneGuide[];
  // The label of each light, in the order of the lights. The canvas shows one at a time: the selected light or the light at rest.
  labels: (SceneRect & { side: LabelSide })[];
  // The label of each guide, at one end of its line.
  guideLabels: SceneRect[];
  mark: SceneRect | null;
  hint: SceneRect | null;
};

/*
 * The label of a guide at one end of its line: over the left end, over the right end, under the left end, or under the
 * right end, whichever first is clear of `blocked`. It takes the first place, held inside the box, when none is clear.
 */
function placeGuideLabel(
  guide: SceneGuide,
  size: SceneSize,
  blocked: SceneRect[],
  box: Pick<SceneBox, "width" | "height">,
): SceneRect {
  const ends = [...guide.points].sort((a, b) => a.x - b.x);
  const left = ends[0];
  const right = ends[ends.length - 1];
  const over = (point: ScenePoint) => point.y - LABEL_GAP / 2 - size.height;
  const under = (point: ScenePoint) => point.y + LABEL_GAP / 2;
  const places = [
    { x: left.x, y: over(left) },
    { x: right.x - size.width, y: over(right) },
    { x: left.x, y: under(left) },
    { x: right.x - size.width, y: under(right) },
  ].map((place) => ({
    x: clamp(place.x, 0, box.width - size.width),
    y: clamp(place.y, 0, box.height - size.height),
    width: size.width,
    height: size.height,
  }));
  return places.find((place) => !blocked.some((rect) => overlaps(place, rect))) ?? places[0];
}

/* The hint in the first corner that no light and no other text takes: top left, top right, bottom right, bottom left. */
function placeHint(size: SceneSize, blocked: SceneRect[], box: Pick<SceneBox, "width" | "height">): SceneRect | null {
  const left = HINT_INSET;
  const right = box.width - HINT_INSET - size.width;
  const top = HINT_INSET;
  const bottom = box.height - HINT_INSET - size.height;
  const corners = [
    { x: left, y: top },
    { x: right, y: top },
    { x: right, y: bottom },
    { x: left, y: bottom },
  ];
  for (const corner of corners) {
    const hint = { ...corner, width: size.width, height: size.height };
    if (!blocked.some((rect) => overlaps(hint, rect))) return hint;
  }
  return null;
}

/*
 * The layout of a scene in one box. The margin mark comes once from the labels of its two ends and the label at rest,
 * so it stays in place when the winner or the loser is selected. The canvas passes `measureText` as `measure`.
 */
export function layoutScene(
  scene: HeroScene,
  box: SceneBox,
  measure: (text: string) => SceneSize = (text) => estimateTextSize(text),
): SceneLayout {
  const points = placeLights(scene, box);
  const guides = placeGuides(scene, box);
  const labels = scene.lights.map((light, index) => placeLightLabel(points, index, measure(light.label), box));
  const ends = scene.margin ? [scene.margin.from, scene.margin.to] : [];
  const shown = [...new Set([...ends, ...(scene.restIndex === null ? [] : [scene.restIndex])])].map((index) => labels[index]);
  const mark = scene.margin ? placeMarginMark(points, scene.margin, measure(scene.margin.text), shown, box) : null;
  // The label of each guide keeps clear of the lights, the labels that show most, the mark, and each guide label before it.
  const blocked = [...points.map(lightRect), ...shown, ...(mark ? [mark] : [])];
  const guideLabels: SceneRect[] = [];
  for (const guide of guides) {
    const label = placeGuideLabel(guide, measure(guide.label), [...blocked, ...guideLabels], box);
    guideLabels.push(label);
  }
  const hint = placeHint(measure(HINT_TEXT), [...blocked, ...guideLabels], box);
  return { points, guides, labels, guideLabels, mark, hint };
}
