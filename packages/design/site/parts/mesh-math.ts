/**
 * The pure math of the mesh: the nodes of the grid at the pitch of the hero grid, each pulled toward the weights.
 * It knows no canvas and no DOM, so the runner of `mesh-canvas.ts` only paints the places it gives.
 */

/* A weight under the mesh: its place in the pixels of the canvas, and its pull from 0 (none) to below 1.
   Idle has no weight. A later state, such as the grade wait, sets one weight under each side of the trade. */
export type MeshWeight = { x: number; y: number; pull: number };

/* The nodes of the grid, row by row. Node k sits at (x[k], y[k]). */
export type MeshNodes = { cols: number; rows: number; x: Float32Array; y: Float32Array };

/* The reach of a weight, in pixels. A Gaussian of this sigma pulls the nodes near a weight, after the scrolltide
   item mesh-flow. It caps at a share of the width, so a phone keeps the pull inside one side. */
const PULL_SIGMA = 85;
const PULL_SIGMA_SHARE = 0.18;

/* A weight with less pull than this moves no node by a visible amount, so the math skips it. */
const MIN_PULL = 0.002;

/* The sigma of the pull for a canvas of this width. */
export function pullSigma(width: number): number {
  return Math.min(PULL_SIGMA, width * PULL_SIGMA_SHARE);
}

/*
 * The nodes of a mesh that covers a box of this size. One extra node past each edge lets a pulled line run off the box
 * and never end inside it. The half pixel puts each line of 1px on the same pixels as the lines of `.hero-texture`.
 */
export function meshNodes(width: number, height: number, pitch: number, weights: readonly MeshWeight[]): MeshNodes {
  const cols = Math.ceil(width / pitch) + 3;
  const rows = Math.ceil(height / pitch) + 3;
  const origin = -pitch + 0.5;
  const x = new Float32Array(cols * rows);
  const y = new Float32Array(cols * rows);
  const live = weights.filter((w) => w.pull > MIN_PULL);
  const twoSigmaSq = 2 * pullSigma(width) ** 2;
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      const nx = origin + i * pitch;
      const ny = origin + j * pitch;
      let dx = 0;
      let dy = 0;
      for (const w of live) {
        const ox = nx - w.x;
        const oy = ny - w.y;
        const pull = Math.exp(-(ox * ox + oy * oy) / twoSigmaSq) * w.pull;
        dx -= ox * pull;
        dy -= oy * pull;
      }
      const k = j * cols + i;
      x[k] = nx + dx;
      y[k] = ny + dy;
    }
  }
  return { cols, rows, x, y };
}
