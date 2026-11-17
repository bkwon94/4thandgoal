/**
 * The runner of the mesh on one Canvas 2D context: the grid, the low corner glow, the weights and the light pulses of a
 * wait, and a soft hole under each hero text. It draws a frame only on a change, and never while the hero is out of view.
 */
import { type MeshLine, type MeshNodes, type MeshWeight, meshNodes, pointOnLine, pullSigma, turnPulls } from "./mesh-math";

/* A point in the pixels of the canvas. */
export type MeshPoint = { x: number; y: number };

/* What the mesh shows at a time. `anchors` holds the center of each `[data-mesh-anchor]` of the hero, in the order of the
   markup, so a drive can set a weight under each side. `busy` keeps the loop on for the next frame. `pulses` is the share
   of the light pulses that shows, from 0 to 1, and none shows when it is left out. Idle has no weight and is not busy, so
   the flat mesh costs no frame at all until the layout changes. The grade wait passes its own drive. */
export type MeshDrive = (now: number, anchors: readonly MeshPoint[]) => { weights: MeshWeight[]; busy: boolean; pulses?: number };

export const IDLE_DRIVE: MeshDrive = () => ({ weights: [], busy: false });

/* The pull of the weight that holds the turn, at its peak. It stops well short of 1, so the mesh sags under a side and
   never folds into a knot. */
const WAIT_PULL = 0.5;

/* The drive of the grade wait, from the time it starts: a weight under each anchor pulls the mesh down in turn, and the
   pulses run. It has no end, because the wait has no minimum time and ends when the grade does. */
export function waitDrive(start: number): MeshDrive {
  return (now, anchors) => {
    const pulls = turnPulls(now - start, anchors.length, WAIT_PULL);
    return { weights: anchors.map((a, i) => ({ x: a.x, y: a.y, pull: pulls[i] })), busy: true, pulses: 1 };
  };
}

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
/* A chip enters in about 200 ms, so a change of the layout keeps the frames on this long, and each hole follows its text.
   The holes and the anchors are read again on each frame of the settle, and kept as they are after it. */
const SETTLE_MS = 400;
/* A phone at 3x draws four times the pixels of 1.5x for no visible gain on lines of 1px, so the ratio caps at 2. */
const MAX_DPR = 2;
/* The shadow trick of the hole: the shape draws this far off the canvas, and only its blurred shadow lands. */
const FAR = 10000;

/* A weight lights the mesh lines near it, so the dip reads as a weight and not as a bend alone. The light stays soft,
   and the deep hole under a small label takes most of it away, so the label of the side that pulls keeps its contrast. */
const WEIGHT_LIGHT = 0.8;
/* The light of a weight reaches this many sigmas of its pull. */
const WEIGHT_LIGHT_REACH = 2.6;

/* The pulses of a wait, after the pulses of the scrolltide item light-cove: a bright head, a soft tail, and a small bloom.
   Few and slow, so the mesh stays calm. */
const PULSE_COUNT = 8;
/* The speed of a pulse in grid cells per second, and the extra speed near a weight that pulls. */
const PULSE_SPEED = 2.2;
const PULSE_BOOST = 3;
/* The tail of a pulse in grid cells, and the count of points that draw it. */
const PULSE_TAIL = 2.4;
const TAIL_STEPS = 12;
const BLOOM = 12;
/* A pulse fades out over this many pixels as it nears a text, so neither its head nor its bloom ever sits behind a word.
   The reach is twice the bloom, so the bloom has faded before its edge reaches a hole. */
const PULSE_CLEAR = 2 * BLOOM;
/* The share of the pulses fades to its target at this rate per second, so no pulse cuts off when a wait starts or ends. */
const PULSE_FADE = 3;
/* A frame after a long pause, such as a hidden tab, moves the pulses no more than one frame at 30 fps. */
const MAX_STEP_S = 1 / 30;

type Hole = { x: number; y: number; w: number; h: number; depth: number };
type Pulse = MeshLine & { t: number; sign: 1 | -1; speed: number };

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
  let colors = { grid: "", dot: "", glow: [0, 0, 0, 0] as number[], pulse: [0, 0, 0, 0] as number[] };
  let raf = 0;
  let inView = true;
  // A frame is owed: the canvas was cleared or the layout changed while no frame could draw.
  let owed = true;
  let settleUntil = 0;
  // The count of drawn frames. The evidence of AT-16 reads it from the canvas, to prove that a hidden mesh draws nothing.
  let frames = 0;
  // The layout that the frames reuse: the holes, the mask they cut, and the anchors. A change of the layout marks it stale.
  let layoutStale = true;
  let holeList: Hole[] = [];
  let anchors: MeshPoint[] = [];
  const mask = document.createElement("canvas");
  const maskCtx = mask.getContext("2d");
  let pulses: Pulse[] = [];
  let pulseShare = 0;
  let lastNow = 0;

  function readColors() {
    const [grid, glow, dot, pulse] = Array.from(probe.children).map((child) => getComputedStyle(child).color);
    colors = { grid, dot, glow: channels(glow), pulse: channels(pulse ?? glow) };
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
    mask.width = canvas.width;
    mask.height = canvas.height;
    layoutStale = true;
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

  /* The center of each anchor of the hero, such as a side of the trade on the stage, in the pixels of the canvas. */
  function readAnchors(): MeshPoint[] {
    if (!content) return [];
    const origin = canvas.getBoundingClientRect();
    return Array.from(content.querySelectorAll("[data-mesh-anchor]"), (el) => {
      const box = el.getBoundingClientRect();
      return { x: box.left - origin.left + box.width / 2, y: box.top - origin.top + box.height / 2 };
    });
  }

  /* Reads the layout again and draws the holes into the mask once, so a frame of the wait cuts them with one copy. */
  function readLayout() {
    layoutStale = false;
    holeList = holes();
    anchors = readAnchors();
    if (!maskCtx) return;
    maskCtx.setTransform(1, 0, 0, 1, 0, 0);
    maskCtx.clearRect(0, 0, mask.width, mask.height);
    maskCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    maskCtx.fillStyle = "#000";
    maskCtx.shadowColor = "#000";
    // A canvas shadow ignores the transform of the pixel ratio, so its blur and its offset scale by the ratio here.
    maskCtx.shadowBlur = HOLE_BLUR * dpr;
    maskCtx.shadowOffsetX = FAR * dpr;
    for (const hole of holeList) {
      maskCtx.globalAlpha = hole.depth;
      maskCtx.fillRect(hole.x - HOLE_PAD_X - FAR, hole.y - HOLE_PAD_Y, hole.w + 2 * HOLE_PAD_X, hole.h + 2 * HOLE_PAD_Y);
    }
    maskCtx.globalAlpha = 1;
  }

  function gridPath({ cols, rows, x, y }: MeshNodes): Path2D {
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
    return path;
  }

  function drawGrid(nodes: MeshNodes, path: Path2D) {
    const { x, y } = nodes;
    ctx.lineWidth = 1;
    ctx.strokeStyle = colors.grid;
    ctx.stroke(path);
    ctx.globalAlpha = DOT_ALPHA;
    ctx.fillStyle = colors.dot;
    const half = DOT_SIZE / 2;
    for (let k = 0; k < x.length; k++) ctx.fillRect(x[k] - half, y[k] - half, DOT_SIZE, DOT_SIZE);
    ctx.globalAlpha = 1;
  }

  /* The lines near each weight that pulls light up in the pulse color, in proportion to its pull. */
  function drawWeightLight(path: Path2D, weights: MeshWeight[]) {
    const [r, g, b] = colors.pulse;
    const reach = pullSigma(width) * WEIGHT_LIGHT_REACH;
    for (const w of weights) {
      if (w.pull < 0.01) continue;
      const peak = Math.min(1, w.pull / WAIT_PULL) * WEIGHT_LIGHT;
      const fill = ctx.createRadialGradient(w.x, w.y, 0, w.x, w.y, reach);
      fill.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${peak})`);
      fill.addColorStop(0.4, `rgba(${r}, ${g}, ${b}, ${peak * 0.4})`);
      fill.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
      ctx.strokeStyle = fill;
      ctx.stroke(path);
    }
  }

  /* 0 inside a text and its pad, rising to 1 at PULSE_CLEAR pixels out. */
  function clearOf(px: number, py: number): number {
    let f = 1;
    for (const hole of holeList) {
      const dx = Math.max(hole.x - HOLE_PAD_X - px, 0, px - (hole.x + hole.w + HOLE_PAD_X));
      const dy = Math.max(hole.y - HOLE_PAD_Y - py, 0, py - (hole.y + hole.h + HOLE_PAD_Y));
      if (dx >= PULSE_CLEAR || dy >= PULSE_CLEAR) continue;
      f = Math.min(f, Math.hypot(dx, dy) / PULSE_CLEAR);
      if (f === 0) return 0;
    }
    return Math.min(1, f);
  }

  /* A new pulse enters from one end of a line. Half of them take a line near a weight, so the light gathers where the
     sides are. The first pulses of a wait start part way along their lines, so the wait does not open with a wave
     from the edges. */
  function spawn(nodes: MeshNodes, spread: boolean): Pulse {
    const dir: "h" | "v" = Math.random() < 0.5 ? "h" : "v";
    const sign: 1 | -1 = Math.random() < 0.5 ? 1 : -1;
    const lines = dir === "h" ? nodes.rows : nodes.cols;
    const length = dir === "h" ? nodes.cols : nodes.rows;
    const near = anchors.length > 0 && Math.random() < 0.5 ? anchors[Math.floor(Math.random() * anchors.length)] : null;
    const index = near
      ? Math.round(((dir === "h" ? near.y : near.x) + pitch) / pitch + (Math.random() - 0.5) * 6)
      : 1 + Math.floor(Math.random() * (lines - 2));
    const t = spread ? Math.random() * (length - 1) : sign > 0 ? -PULSE_TAIL : length - 1 + PULSE_TAIL;
    return { dir, index: Math.max(1, Math.min(lines - 2, index)), t, sign, speed: PULSE_SPEED * (0.8 + Math.random() * 0.4) };
  }

  /* Moves each pulse along its line and draws it. A pulse near a weight that pulls runs faster, so the side that pulls
     reads as busy. A pulse that runs off its line ends, and a new one takes its place while the wait runs. */
  function drawPulses(nodes: MeshNodes, weights: MeshWeight[], want: number, step: number) {
    pulseShare += (want - pulseShare) * Math.min(1, step * PULSE_FADE);
    if (want > 0) {
      const spread = pulses.length === 0;
      while (pulses.length < PULSE_COUNT) pulses.push(spawn(nodes, spread));
    }
    if (pulseShare < 0.01 && want === 0) {
      pulses = [];
      return;
    }
    const [r, g, b] = colors.pulse;
    const twoSigmaSq = 2 * pullSigma(width) ** 2;
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    pulses = pulses.filter((pulse) => {
      const head = pointOnLine(nodes, pulse, pulse.t);
      let boost = 0;
      for (const w of weights) boost += w.pull * Math.exp(-((head.x - w.x) ** 2 + (head.y - w.y) ** 2) / twoSigmaSq);
      pulse.t += pulse.sign * pulse.speed * (1 + PULSE_BOOST * boost) * step;
      const length = pulse.dir === "h" ? nodes.cols : nodes.rows;
      if (pulse.t < -PULSE_TAIL || pulse.t > length - 1 + PULSE_TAIL) return false;
      // The tail: points behind the head that fade and thin, so the pulse reads as a streak and not as a dot.
      for (let i = TAIL_STEPS; i >= 1; i--) {
        const u = i / TAIL_STEPS;
        const at = pointOnLine(nodes, pulse, pulse.t - pulse.sign * u * PULSE_TAIL);
        const alpha = pulseShare * (1 - u) ** 2 * 0.9 * clearOf(at.x, at.y);
        if (alpha < 0.01) continue;
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(at.x, at.y, 0.8 + (1 - u) * 1.1, 0, Math.PI * 2);
        ctx.fill();
      }
      const clear = clearOf(head.x, head.y) * pulseShare;
      if (clear < 0.01) return true;
      // The bloom of the head: one soft radial glow, cheap enough for a phone.
      const bloom = ctx.createRadialGradient(head.x, head.y, 0, head.x, head.y, BLOOM);
      bloom.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${0.5 * clear})`);
      bloom.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
      ctx.globalAlpha = 1;
      ctx.fillStyle = bloom;
      ctx.fillRect(head.x - BLOOM, head.y - BLOOM, 2 * BLOOM, 2 * BLOOM);
      // The head is the pulse color lifted toward white, so it reads as the hot point of the streak.
      ctx.fillStyle = `rgb(${(r + 255 * 2) / 3}, ${(g + 255 * 2) / 3}, ${(b + 255 * 2) / 3})`;
      ctx.globalAlpha = clear;
      ctx.beginPath();
      ctx.arc(head.x, head.y, 1.4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
      return true;
    });
    ctx.restore();
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

  /* The art dims under each text with a short soft edge, so the text needs no plate. The mask holds the holes, drawn
     once per layout, so each frame cuts them all with one copy. The pulses and the weight light sit under the cut too. */
  function cutHoles() {
    if (mask.width < 1 || mask.height < 1) return;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalCompositeOperation = "destination-out";
    ctx.drawImage(mask, 0, 0);
    ctx.restore();
  }

  function frame(now: number) {
    raf = 0;
    owed = false;
    if (layoutStale || now < settleUntil) readLayout();
    const step = lastNow ? Math.min(MAX_STEP_S, (now - lastNow) / 1000) : 0;
    lastNow = now;
    const drawn = drive(now, anchors);
    // With motion off, the mesh is still and flat: no weight pulls and no pulse runs.
    const weights = motionOff ? [] : drawn.weights;
    const pulseWant = motionOff ? 0 : (drawn.pulses ?? 0);
    ctx.clearRect(0, 0, width, height);
    if (width >= 2 && height >= 2) {
      const nodes = meshNodes(width, height, pitch, weights);
      const path = gridPath(nodes);
      drawGrid(nodes, path);
      drawWeightLight(path, weights);
      drawGlow();
      drawPulses(nodes, weights, pulseWant, step);
      cutHoles();
    }
    canvas.dataset.meshFrames = String(++frames);
    // The pull of each weight, in the order of the anchors. The evidence of AT-5 reads it to find the side that pulls.
    canvas.dataset.meshPulls = (motionOff ? drawn.weights.map(() => 0) : drawn.weights.map((w) => w.pull)).map((p) => p.toFixed(3)).join(",");
    const fading = pulses.length > 0 && pulseShare >= 0.01;
    if (((drawn.busy || fading) && !motionOff) || now < settleUntil) schedule();
    else lastNow = 0;
  }

  /* Asks for one frame. A frame that cannot draw now stays owed until the hero is back in view and the tab shows. */
  function schedule() {
    owed = true;
    if (raf || !inView || document.hidden) return;
    raf = requestAnimationFrame(frame);
  }

  /* The layout or the colors changed. With motion on, the frames run on for the settle, so a hole follows a chip that enters. */
  function touch() {
    layoutStale = true;
    if (!motionOff) settleUntil = performance.now() + SETTLE_MS;
    schedule();
  }

  function pause() {
    lastNow = 0;
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
