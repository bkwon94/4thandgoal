/**
 * The runner of the mesh on one Canvas 2D context: the grid, the low corner glow, and a soft hole under each hero text.
 * It draws a frame only on a change, and never while the hero is out of view or the tab is hidden.
 */
import { type MeshWeight, meshNodes } from "./mesh-math";

/* What the mesh shows at a time. `busy` keeps the loop on for the next frame. Idle has no weight and is not busy, so
   the flat mesh costs no frame at all until the layout changes. A later state, such as the grade wait, passes its own drive. */
export type MeshDrive = (now: number) => { weights: MeshWeight[]; busy: boolean };

export const IDLE_DRIVE: MeshDrive = () => ({ weights: [], busy: false });

export type MeshParts = {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  // The hero section. The mesh cuts a hole under each text of its content box.
  hero: HTMLElement;
  // The hidden element with one child each in the grid color, the glow color, and the dot color.
  probe: HTMLElement;
  motionOff: boolean;
  drive?: MeshDrive;
};

/* The dots on the nodes: small and faint, so the grid reads as one surface and not as a field of points. */
const DOT_SIZE = 1.6;
const DOT_ALPHA = 0.22;
/* The glow of ADR 0036: an ellipse of 38 by 46 percent of the box, its center 12 percent under the bottom right corner,
   fading out at 70 percent of its radius. It is the glow of `.hero-texture`, so the mesh hero matches every other hero. */
const GLOW = { rx: 0.38, ry: 0.46, cy: 1.12, fade: 0.7 };
/* The hole under a text takes away this share of the mesh and the glow. The text sits on a dimmer ground, not on a
   dark halo, so the hole never reads as a plate (decision 01). */
const HOLE_DEPTH = 0.5;
/* Small text, such as a column label, needs more contrast than its size can carry, so its hole goes deeper.
   The hole stays as small as the text, so it never reads as a halo. */
const HOLE_DEPTH_SMALL = 0.88;
const SMALL_TEXT_PX = 14;
const HOLE_BLUR = 10;
const HOLE_PAD_X = 8;
const HOLE_PAD_Y = 6;
/* A chip enters in about 200 ms, so a change of the layout keeps the frames on this long, and each hole follows its text. */
const SETTLE_MS = 400;
/* A phone at 3x draws four times the pixels of 1.5x for no visible gain on lines of 1px, so the ratio caps at 2. */
const MAX_DPR = 2;
/* The shadow trick of the hole: the shape draws this far off the canvas, and only its blurred shadow lands. */
const FAR = 10000;

type Hole = { x: number; y: number; w: number; h: number; depth: number };

/* The color of a CSS value as its four channels, from 0 to 255 and an alpha of 0 to 1. A 1px canvas reads it, so a
   value in any syntax, such as color-mix() or oklch(), resolves as the browser draws it. */
function channels(color: string): [number, number, number, number] {
  const probe = document.createElement("canvas").getContext("2d");
  if (!probe) return [0, 0, 0, 0];
  probe.fillStyle = color;
  probe.fillRect(0, 0, 1, 1);
  const [r, g, b, a] = probe.getImageData(0, 0, 1, 1).data;
  return [r, g, b, a / 255];
}

/* Starts the mesh and returns its stop. */
export function runMesh({ canvas, ctx, hero, probe, motionOff, drive = IDLE_DRIVE }: MeshParts): () => void {
  const content = hero.querySelector<HTMLElement>(":scope > [data-hero-content]");
  let width = 0;
  let height = 0;
  let dpr = 1;
  let pitch = 24;
  let colors = { grid: "", dot: "", glow: [0, 0, 0, 0] as number[] };
  let raf = 0;
  let inView = true;
  // A frame is owed: the canvas was cleared or the layout changed while no frame could draw.
  let owed = true;
  let settleUntil = 0;
  // The count of drawn frames. The evidence of AT-16 reads it from the canvas, to prove that a hidden mesh draws nothing.
  let frames = 0;

  function readColors() {
    const [grid, glow, dot] = Array.from(probe.children).map((child) => getComputedStyle(child).color);
    colors = { grid, dot, glow: channels(glow) };
    pitch = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--spacing-hero-grid")) || 24;
  }

  function resize() {
    const box = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    width = box.width;
    height = box.height;
    canvas.width = Math.max(1, Math.round(width * dpr));
    canvas.height = Math.max(1, Math.round(height * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  /* The box of each line of each text of the hero, and of each chip, in the pixels of the canvas. */
  function holes(): Hole[] {
    if (!content) return [];
    const origin = canvas.getBoundingClientRect();
    const list: Hole[] = [];
    const add = (box: DOMRect, depth: number) => {
      if (box.width > 0 && box.height > 0) list.push({ x: box.left - origin.left, y: box.top - origin.top, w: box.width, h: box.height, depth });
    };
    const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const el = node.parentElement;
      if (!el || !node.textContent?.trim()) continue;
      const depth = parseFloat(getComputedStyle(el).fontSize) <= SMALL_TEXT_PX ? HOLE_DEPTH_SMALL : HOLE_DEPTH;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const line of range.getClientRects()) add(line, depth);
    }
    for (const chip of content.querySelectorAll("[data-mesh-hole]")) add(chip.getBoundingClientRect(), HOLE_DEPTH);
    return list;
  }

  function drawGrid(weights: MeshWeight[]) {
    const { cols, rows, x, y } = meshNodes(width, height, pitch, weights);
    const path = new Path2D();
    for (let j = 0; j < rows; j++)
      for (let i = 0; i < cols; i++) {
        const k = j * cols + i;
        if (i === 0) path.moveTo(x[k], y[k]);
        else path.lineTo(x[k], y[k]);
      }
    for (let i = 0; i < cols; i++)
      for (let j = 0; j < rows; j++) {
        const k = j * cols + i;
        if (j === 0) path.moveTo(x[k], y[k]);
        else path.lineTo(x[k], y[k]);
      }
    ctx.lineWidth = 1;
    ctx.strokeStyle = colors.grid;
    ctx.stroke(path);
    ctx.globalAlpha = DOT_ALPHA;
    ctx.fillStyle = colors.dot;
    const half = DOT_SIZE / 2;
    for (let k = 0; k < x.length; k++) ctx.fillRect(x[k] - half, y[k] - half, DOT_SIZE, DOT_SIZE);
    ctx.globalAlpha = 1;
  }

  function drawGlow() {
    const [r, g, b, a] = colors.glow;
    ctx.save();
    ctx.translate(width, height * GLOW.cy);
    ctx.scale(width * GLOW.rx, height * GLOW.ry);
    const fill = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
    // The glow fades to its own color at no alpha, as CSS does, so the edge never greys toward black.
    fill.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${a})`);
    fill.addColorStop(GLOW.fade, `rgba(${r}, ${g}, ${b}, 0)`);
    ctx.fillStyle = fill;
    ctx.fillRect(-1, -1, 2, 2);
    ctx.restore();
  }

  /* The art dims under each text with a short soft edge, so the text needs no plate. */
  function cutHoles() {
    ctx.save();
    ctx.globalCompositeOperation = "destination-out";
    ctx.fillStyle = "#000";
    ctx.shadowColor = "#000";
    // A canvas shadow ignores the transform of the pixel ratio, so its blur and its offset scale by the ratio here.
    ctx.shadowBlur = HOLE_BLUR * dpr;
    ctx.shadowOffsetX = FAR * dpr;
    for (const hole of holes()) {
      ctx.globalAlpha = hole.depth;
      ctx.fillRect(hole.x - HOLE_PAD_X - FAR, hole.y - HOLE_PAD_Y, hole.w + 2 * HOLE_PAD_X, hole.h + 2 * HOLE_PAD_Y);
    }
    ctx.restore();
  }

  function frame(now: number) {
    raf = 0;
    owed = false;
    const { weights, busy } = drive(now);
    ctx.clearRect(0, 0, width, height);
    if (width >= 2 && height >= 2) {
      drawGrid(weights);
      drawGlow();
      cutHoles();
    }
    canvas.dataset.meshFrames = String(++frames);
    if ((busy && !motionOff) || now < settleUntil) schedule();
  }

  /* Asks for one frame. A frame that cannot draw now stays owed until the hero is back in view and the tab shows. */
  function schedule() {
    owed = true;
    if (raf || !inView || document.hidden) return;
    raf = requestAnimationFrame(frame);
  }

  /* The layout or the colors changed. With motion on, the frames run on for the settle, so a hole follows a chip that enters. */
  function touch() {
    if (!motionOff) settleUntil = performance.now() + SETTLE_MS;
    schedule();
  }

  function pause() {
    if (!raf) return;
    cancelAnimationFrame(raf);
    raf = 0;
    owed = true;
  }

  readColors();
  resize();
  schedule();

  const sized = new ResizeObserver(() => {
    resize();
    touch();
  });
  sized.observe(canvas);
  if (content) sized.observe(content);
  // A chip can join a column with no change to the height of the hero, so a change of the content draws a frame too.
  const changed = new MutationObserver(touch);
  if (content) changed.observe(content, { childList: true, subtree: true, characterData: true });
  // The grid color differs per theme, so a switch of the theme reads the colors again.
  const themed = new MutationObserver(() => {
    readColors();
    touch();
  });
  themed.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  const seen = new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    if (!inView) pause();
    else if (owed) schedule();
  });
  seen.observe(canvas);
  const onVisibility = () => {
    if (document.hidden) pause();
    else if (owed) schedule();
  };
  document.addEventListener("visibilitychange", onVisibility);

  return () => {
    if (raf) cancelAnimationFrame(raf);
    sized.disconnect();
    changed.disconnect();
    themed.disconnect();
    seen.disconnect();
    document.removeEventListener("visibilitychange", onVisibility);
  };
}
