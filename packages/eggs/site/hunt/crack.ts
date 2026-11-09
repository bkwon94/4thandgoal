/**
 * The shape of the crack of the egg: the tap point, the jagged lines that spread from it, the shards, and the two halves.
 * The units are the units of the egg art, 180 by 220. A seed sets the jitter, so each tap cracks in a new way.
 */

/* A point in the units of the egg art. */
export type Point = { x: number; y: number };

/* The size of the egg art, the same as its viewBox. */
export const EGG_SIZE = { width: 180, height: 220 };

/* The middle of the egg, where a tap by the keyboard cracks it. The egg is wider low down, so its middle sits low. */
export const EGG_MIDDLE: Point = { x: 90, y: 130 };

/* The tap point stays inside these bounds, so a crack never starts on the edge of the egg. */
const BOUNDS = { left: 40, right: 140, top: 60, bottom: 185 };

/* One crack line: its points as an SVG list, and its length, so the line can draw from the tap point out. */
export type CrackLine = { points: string; length: number };

/* One shard: a sliver of shell at the tap point, and the move and the turn of its flight when the shell bursts. */
export type Shard = { points: string; dx: number; dy: number; turn: number };

export type Crack = {
  point: Point;
  lines: CrackLine[];
  shards: Shard[];
  // The clip polygons of the two halves. They meet along a zigzag through the tap point.
  top: string;
  bottom: string;
};

/* The tap point of a pointer tap at (clientX, clientY) on an egg with this box on the screen, clamped inside the egg.
   A box with no size, as in a page with no layout, gives the middle of the egg. */
export function tapPointOf(clientX: number, clientY: number, box: { left: number; top: number; width: number; height: number }): Point {
  if (box.width === 0 || box.height === 0) return EGG_MIDDLE;
  const x = ((clientX - box.left) / box.width) * EGG_SIZE.width;
  const y = ((clientY - box.top) / box.height) * EGG_SIZE.height;
  return {
    x: Math.min(BOUNDS.right, Math.max(BOUNDS.left, x)),
    y: Math.min(BOUNDS.bottom, Math.max(BOUNDS.top, y)),
  };
}

/* A fresh seed for the jitter of one crack. */
export function freshSeed(): number {
  return 1 + Math.floor(Math.random() * 2147483646);
}

/* A small seeded random source (the Park and Miller generator), so one seed always gives one crack. */
function randomOf(seed: number): () => number {
  let state = seed % 2147483647 || 1;
  return () => {
    state = (state * 16807) % 2147483647;
    return (state % 10000) / 10000;
  };
}

const radians = (degrees: number) => (degrees * Math.PI) / 180;
const pair = (x: number, y: number) => `${x.toFixed(1)},${y.toFixed(1)}`;

/* The base angle of each of the six crack lines, in degrees: left and right, then two up and two down at a slant. */
const LINE_ANGLES = [0, 180, 55, 125, 235, 305];

/* The crack of a tap at this point with this seed. */
export function crackOf(point: Point, seed: number): Crack {
  const random = randomOf(seed);
  const { x: tx, y: ty } = point;

  // Each line walks out from the tap point in five jagged steps around its base angle.
  const lines = LINE_ANGLES.map((base) => {
    let x = tx;
    let y = ty;
    let length = 0;
    const points = [pair(x, y)];
    const angle = base + (random() - 0.5) * 30;
    for (let step = 0; step < 5; step++) {
      const turn = radians(angle + (random() - 0.5) * 50);
      const size = 14 + random() * 14;
      x += Math.cos(turn) * size;
      y += Math.sin(turn) * size;
      length += size;
      points.push(pair(x, y));
    }
    // The extra 2 units keep the round cap of the line hidden before it draws.
    return { points: points.join(" "), length: Math.ceil(length) + 2 };
  });

  // Seven slivers of shell around the tap point, each with its own flight out from it.
  const shards = [0, 1, 2, 3, 4, 5, 6].map((index) => {
    const angle = index * 51 + random() * 20;
    const near = 12 + random() * 10;
    const far = 14 + random() * 12;
    const at = (degrees: number, reach: number) => pair(tx + Math.cos(radians(degrees)) * reach, ty + Math.sin(radians(degrees)) * reach);
    const distance = 90 + random() * 60;
    return {
      points: `${pair(tx, ty)} ${at(angle - 20, near)} ${at(angle + 20, far)}`,
      dx: Math.round(Math.cos(radians(angle)) * distance),
      dy: Math.round(Math.sin(radians(angle)) * distance),
      turn: Math.round((random() - 0.5) * 360),
    };
  });

  // The zigzag runs across the egg at the height of the tap point, from the right edge to the left.
  const zigzag = Array.from({ length: 11 }, (_, index) => `${190 - index * 20},${ty + (index % 2 ? -8 : 8)}`).join(" ");
  return {
    point,
    lines,
    shards,
    top: `-40,-40 220,-40 220,${ty} ${zigzag} -40,${ty}`,
    bottom: `-40,260 220,260 220,${ty} ${zigzag} -40,${ty}`,
  };
}
