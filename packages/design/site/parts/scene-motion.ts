/**
 * The motion of the hero scene as pure functions of the time after entry: the scatter, the settle, the dust, and the drift.
 * The canvas asks for the places at each frame, so a test checks the motion with no canvas and no clock.
 */
import type { SceneBox, ScenePoint } from "./scene-math";

/* The lights settle in about 1.9 s (PRD). The thin lines then draw in 0.3 s, so the scene is at rest by 2.2 s (AT-16). */
export const SETTLE_MS = 1900;
export const LINES_MS = 300;
export const REST_MS = SETTLE_MS + LINES_MS;

/* `settle` runs the frames of the settle. `rest` draws one frame per tap or slide and runs no loop (story 38). */
export type ScenePhase = "settle" | "rest";

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

/* The strong ease-out of the settle: fast at entry and slow into the chart. The quartic curve covers 94% of the way at half time. */
export function easeOut(t: number): number {
  return 1 - (1 - clamp01(t)) ** 4;
}

/* A small seeded random source (mulberry32), so a scatter is the same for the same seed and a test can check it. */
function randomOf(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* The start place of each light: a scatter inside the padding of the box. */
export function scatterOf(count: number, box: SceneBox, seed: number): ScenePoint[] {
  const random = randomOf(seed);
  return Array.from({ length: count }, () => ({
    x: box.padding + random() * (box.width - 2 * box.padding),
    y: box.padding + random() * (box.height - 2 * box.padding),
  }));
}

/* The place of each light at a time in the settle, on the way from its start place to its place in the chart. */
export function settleAt(from: ScenePoint[], to: ScenePoint[], elapsed: number): ScenePoint[] {
  const t = easeOut(elapsed / SETTLE_MS);
  // The chart itself at the end, so the lights at rest sit exactly on their places with no rounding left.
  if (t >= 1) return to;
  return from.map((start, index) => ({
    x: start.x + (to[index].x - start.x) * t,
    y: start.y + (to[index].y - start.y) * t,
  }));
}

/* The share of the thin lines between the lights that is drawn, from 0 when the lights settle to 1 at rest. */
export function linesAt(elapsed: number): number {
  return clamp01((elapsed - SETTLE_MS) / LINES_MS);
}

export function phaseAt(elapsed: number): ScenePhase {
  return elapsed >= REST_MS ? "rest" : "settle";
}

/* One point of the faint dust behind the lights: a start place and a speed in pixels per second. */
export type DustPoint = { x: number; y: number; vx: number; vy: number };

/* The faint dust of the scene: 40 to 80 tiny points (PRD). Each drifts slowly in its own direction. */
export function dustOf(count: number, box: SceneBox, seed: number): DustPoint[] {
  const random = randomOf(seed);
  return Array.from({ length: Math.max(40, Math.min(80, count)) }, () => ({
    x: random() * box.width,
    y: random() * box.height,
    vx: (random() - 0.5) * 16,
    vy: (random() - 0.5) * 10,
  }));
}

/* A value wrapped into the range from 0 to size, so a point that leaves one edge comes back at the other. */
const wrap = (value: number, size: number) => ((value % size) + size) % size;

/* The place of each point of dust at a time after entry. The dust stops at `stopAt`, the time of rest of the scene. */
export function dustAt(dust: DustPoint[], box: SceneBox, elapsed: number, stopAt: number = REST_MS): ScenePoint[] {
  const seconds = Math.min(elapsed, stopAt) / 1000;
  return dust.map((point) => ({
    x: wrap(point.x + point.vx * seconds, box.width),
    y: wrap(point.y + point.vy * seconds, box.height),
  }));
}

/* The reach in pixels of a drifting light from its start place. */
const DRIFT_REACH = 14;

/* The place of each light of a scene that never settles, such as the 404: each light circles slowly near its start place. */
export function driftAt(from: ScenePoint[], box: SceneBox, elapsed: number): ScenePoint[] {
  const seconds = elapsed / 1000;
  return from.map((start, index) => {
    // Each light gets its own speed and its own start angle, so the lights never move as one.
    const speed = 0.35 + (index % 5) * 0.08;
    const angle = seconds * speed + index * 1.7;
    return {
      x: Math.max(box.padding, Math.min(box.width - box.padding, start.x + DRIFT_REACH * Math.cos(angle))),
      y: Math.max(box.padding, Math.min(box.height - box.padding, start.y + DRIFT_REACH * Math.sin(angle * 1.3))),
    };
  });
}
