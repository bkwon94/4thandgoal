/**
 * The fixed layout of the drift field: six slots, one per rank, each with a place, a headshot size, and a drift.
 * The places are fixed and never random, so the page is the same on every render and a test proves no overlap at 390.
 */

/* The geometry is numbers here and not tokens in globals.css: the overlap test does sums on it, and the drift takes numbers.
   The field is 358 pixels wide, the page column at 390 less the two gutters. On a wider page the field box centers. */
export const FIELD = { width: 358, height: 316 } as const;

/* The name label under a headshot: its width, so a short name fits on one line, and its height for the name and the meta line. */
export const LABEL = { width: 84, height: 30, gap: 4 } as const;

/* The price tag sits over the top right edge of the headshot, so it reaches out past the headshot by this much. */
export const TAG = { out: 10, up: 6 } as const;

export type Slot = {
  // The center of the headshot from the left edge of the field, and the top of the headshot.
  x: number;
  y: number;
  size: number;
  // The far end of the drift, as a move from the place. The drift runs there and back.
  dx: number;
  dy: number;
  // One pass of the drift in seconds. Each slot has its own period, so the field never moves in step.
  period: number;
};

/* Rank 1 is the biggest and sits in the middle. Ranks 2 and 3 sit high on the sides, ranks 4 and 5 low on the sides,
   and rank 6 under rank 1. The sizes follow the mockup: 88, 64, and 52 pixels. */
export const SLOTS: readonly Slot[] = [
  { x: 179, y: 70, size: 88, dx: 8, dy: -10, period: 7 },
  { x: 58, y: 20, size: 64, dx: -8, dy: 8, period: 9 },
  { x: 300, y: 30, size: 64, dx: 8, dy: 8, period: 8 },
  { x: 58, y: 170, size: 52, dx: 8, dy: -8, period: 10 },
  { x: 300, y: 180, size: 52, dx: -8, dy: -8, period: 6 },
  { x: 179, y: 220, size: 52, dx: -6, dy: 6, period: 11 },
];

export type Box = { left: number; top: number; right: number; bottom: number };

/* The box a slot can cover at any point of its drift: the headshot with its tag and its label, grown by the drift on each side. */
export function slotBox(slot: Slot): Box {
  const half = Math.max(slot.size / 2 + TAG.out, LABEL.width / 2);
  const driftX = Math.abs(slot.dx);
  const driftY = Math.abs(slot.dy);
  return {
    left: slot.x - half - driftX,
    top: slot.y - TAG.up - driftY,
    right: slot.x + half + driftX,
    bottom: slot.y + slot.size + LABEL.gap + LABEL.height + driftY,
  };
}

/* The scale of the field in a column of this width. The field never grows past the table, and it shrinks under 358.
   A width of 0 means the column is not measured yet, so the field keeps the table size. */
export function fieldScale(width: number): number {
  return width > 0 ? Math.min(1, width / FIELD.width) : 1;
}

/* A slot at a scale. The period stays, so a small phone gets the same slow drift. */
export function scaleSlot(slot: Slot, scale: number): Slot {
  return {
    x: slot.x * scale,
    y: slot.y * scale,
    size: slot.size * scale,
    dx: slot.dx * scale,
    dy: slot.dy * scale,
    period: slot.period,
  };
}
