/**
 * The runner of the hero scene on one Canvas 2D context: the settle on entry, the rest with no loop, the tap and the slide.
 * It takes the places from the pure math of `scene-math.ts` and `scene-motion.ts` and only paints them (ADR 0027).
 */
import {
  type HeroScene,
  HINT_TEXT,
  LABEL_FONT_PX,
  SCENE_PADDING,
  type SceneBox,
  type SceneLayout,
  type ScenePoint,
  type SceneSize,
  layoutScene,
  nearestLight,
  sceneLines,
} from "./scene-math";
import { type DustPoint, driftAt, dustAt, dustOf, linesAt, phaseAt, scatterOf, settleAt } from "./scene-motion";

/* The three colors that the canvas draws, as the `rgb()` strings that the probe element computes (decision 03). */
export type SceneColors = { accent: string; onDark: string; muted: string };

/* `idle` waits for the hero to enter the view. `drift` is a scene that never settles, such as the 404. */
export type SceneState = "idle" | "settle" | "rest" | "drift";

/* The flag that keeps the hint gone for this reader after the first touch on any scene. */
const HINT_KEY = "cpc-scene-hint-seen";

/* True when this reader already touched a scene. A browser with no storage, or one that throws, shows the hint. */
export function hintSeen(): boolean {
  try {
    return window.localStorage.getItem(HINT_KEY) === "1";
  } catch {
    return false;
  }
}

/* Stores the flag of the hint. A browser with no storage keeps the hint gone until the next load only. */
export function rememberHint(): void {
  try {
    window.localStorage.setItem(HINT_KEY, "1");
  } catch {
    // The scene works with no storage (PRD), so a failed write changes nothing else.
  }
}

/* The count of the points of the faint dust behind the lights. */
const DUST_COUNT = 60;
/* The radius of a light, and the larger radius of a flare. */
const LIGHT_RADIUS = 3;
const FLARE_RADIUS = 4.5;
/* The radius of the ring around the selected light. */
const RING_RADIUS = 8;
/* The share of opacity of a dim light, of the dust, and of the thin lines. */
const DIM_ALPHA = 0.45;
const DUST_ALPHA = 0.35;
const LINE_ALPHA = 0.4;
/* A finger that moves more than this many pixels sideways, and more sideways than up or down, slides. */
const SLIDE_PX = 4;
/* The hero must be in the view by about 40 percent before the settle starts (PRD). */
const ENTRY_RATIO = 0.4;
/* The time in ms that the hint takes to fade after the first touch (PRD). */
const HINT_FADE_MS = 300;

/* The parts of the page that the runner draws on and reads from. */
export type SceneParts = {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  // The box that sets the size of the canvas. The ResizeObserver watches it.
  holder: HTMLElement;
  // The hidden element of the mono font, with one child each in the accent, on-dark, and on-dark-muted colors.
  probe: HTMLElement;
  scene: HeroScene;
  motionOff: boolean;
};

/* The colors of the probe, read once at mount. The three roles are equal in both themes, so a theme switch keeps them right. */
function colorsOf(probe: HTMLElement): SceneColors {
  const [accent, onDark, muted] = Array.from(probe.children).map((child) => getComputedStyle(child).color);
  return { accent, onDark, muted };
}

/* One frame of the scene. The canvas is cleared and drawn in full each time, back to front. */
type Frame = {
  box: SceneBox;
  layout: SceneLayout;
  lights: ScenePoint[];
  dust: ScenePoint[];
  // The share of the thin lines and the guides that is drawn, from 0 to 1.
  lines: number;
  // The label, the ring, the mark, and the hint show only at rest.
  rest: boolean;
  shown: number | null;
  selected: number | null;
  hint: boolean;
  // The opacity of the hint, from 1 to 0 during its fade.
  hintAlpha: number;
};

function paint(ctx: CanvasRenderingContext2D, scene: HeroScene, colors: SceneColors, font: string, frame: Frame) {
  const { box, layout, lights } = frame;
  ctx.clearRect(0, 0, box.width, box.height);
  ctx.font = font;
  ctx.textBaseline = "middle";

  ctx.globalAlpha = DUST_ALPHA;
  ctx.fillStyle = colors.muted;
  for (const point of frame.dust) ctx.fillRect(point.x, point.y, 1, 1);

  if (frame.lines > 0) {
    // The guides, such as the league median, as dashed lines with their labels.
    ctx.globalAlpha = frame.lines;
    ctx.strokeStyle = colors.muted;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    for (const guide of layout.guides) {
      ctx.beginPath();
      guide.points.forEach((point, index) => (index === 0 ? ctx.moveTo(point.x, point.y) : ctx.lineTo(point.x, point.y)));
      ctx.stroke();
    }
    ctx.setLineDash([]);
    ctx.fillStyle = colors.muted;
    layout.guideLabels.forEach((rect, index) => ctx.fillText(layout.guides[index].label, rect.x, rect.y + rect.height / 2));

    // The thin lines of the star chart, between the lights in x order inside one group, drawn from left to right.
    const pairs = sceneLines(scene.lights);
    const segments = pairs.length;
    const reach = frame.lines * segments;
    ctx.globalAlpha = LINE_ALPHA;
    ctx.strokeStyle = colors.onDark;
    ctx.beginPath();
    for (let step = 0; step < segments && step < reach; step++) {
      const a = lights[pairs[step][0]];
      const b = lights[pairs[step][1]];
      const share = Math.min(1, reach - step);
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(a.x + (b.x - a.x) * share, a.y + (b.y - a.y) * share);
    }
    ctx.stroke();
  }

  // The lights over the lines. A flare glows in the accent color, and a dim light uses the opacity, not a new color.
  scene.lights.forEach((light, index) => {
    const point = lights[index];
    ctx.globalAlpha = light.tone === "dim" ? DIM_ALPHA : 1;
    ctx.fillStyle = light.tone === "flare" ? colors.accent : light.tone === "bright" ? colors.onDark : colors.muted;
    ctx.shadowBlur = light.tone === "flare" ? 12 : 0;
    ctx.shadowColor = colors.accent;
    ctx.beginPath();
    ctx.arc(point.x, point.y, light.tone === "flare" ? FLARE_RADIUS : LIGHT_RADIUS, 0, 2 * Math.PI);
    ctx.fill();
  });
  ctx.shadowBlur = 0;
  ctx.globalAlpha = 1;
  if (!frame.rest) return;

  if (frame.selected !== null) {
    const point = lights[frame.selected];
    ctx.strokeStyle = colors.onDark;
    ctx.beginPath();
    ctx.arc(point.x, point.y, RING_RADIUS, 0, 2 * Math.PI);
    ctx.stroke();
  }
  if (frame.shown !== null) {
    const rect = layout.labels[frame.shown];
    ctx.fillStyle = colors.onDark;
    ctx.fillText(scene.lights[frame.shown].label, rect.x, rect.y + rect.height / 2);
  }
  if (scene.margin && layout.mark) {
    ctx.fillStyle = colors.onDark;
    ctx.fillText(scene.margin.text, layout.mark.x, layout.mark.y + layout.mark.height / 2);
  }
  if (frame.hint && layout.hint) {
    ctx.globalAlpha = frame.hintAlpha;
    ctx.fillStyle = colors.muted;
    ctx.fillText(HINT_TEXT, layout.hint.x, layout.hint.y + layout.hint.height / 2);
    ctx.globalAlpha = 1;
  }
}

/*
 * Starts the scene on the canvas and returns the function that stops it. The canvas shows its state in data attributes,
 * so a check of the built page reads the phase, the label that shows, and the hint: `data-scene-state`,
 * `data-scene-label`, and `data-scene-hint`.
 */
export function runScene({ canvas, ctx, holder, probe, scene, motionOff }: SceneParts): () => void {
  const colors = colorsOf(probe);
  const font = `${LABEL_FONT_PX}px ${getComputedStyle(probe).fontFamily}`;
  const settles = scene.mode === "settle";

  let box: SceneBox = { width: 0, height: 0, padding: SCENE_PADDING };
  let layout: SceneLayout | null = null;
  let scatter: ScenePoint[] = [];
  let dust: DustPoint[] = [];
  let state: SceneState = "idle";
  let startedAt = 0;
  let plays = 0;
  let loop = 0;
  // True while the hero is out of the view, so the next entry plays the settle again (story 36).
  let away = true;
  let selected: number | null = null;
  let hint = !hintSeen();
  // The time that the fade of the hint started, or null when the hint does not fade. The hint stays until the fade ends.
  let hintFadeAt: number | null = null;
  let finger: { id: number; x: number; y: number; slid: boolean } | null = null;
  let alive = true;

  const measure = (text: string): SceneSize => {
    ctx.font = font;
    return { width: Math.ceil(ctx.measureText(text).width), height: Math.ceil(LABEL_FONT_PX * 1.4) };
  };

  /* The label that shows: the selected light, or the light at rest. A drift shows no label. */
  const shownIndex = () => (settles && state === "rest" ? (selected ?? scene.restIndex) : null);

  function mark() {
    const shown = shownIndex();
    canvas.dataset.sceneState = state;
    canvas.dataset.sceneLabel = shown === null ? "" : scene.lights[shown].label;
    canvas.dataset.sceneHint = hint && state === "rest" && settles ? "shown" : "gone";
  }

  function draw() {
    if (!layout) return;
    const elapsed = state === "idle" ? 0 : performance.now() - startedAt;
    const rest = state === "rest";
    // Under reduced motion a drift stays still at its start places, and the dust does not move.
    const still = motionOff ? 0 : elapsed;
    const lights = settles
      ? rest
        ? layout.points
        : state === "idle"
          ? scatter
          : settleAt(scatter, layout.points, elapsed)
      : driftAt(scatter, box, still);
    paint(ctx, scene, colors, font, {
      box,
      layout,
      lights,
      dust: settles ? (rest ? dustAt(dust, box, Infinity) : dustAt(dust, box, elapsed)) : dustAt(dust, box, still, Infinity),
      lines: settles ? (rest ? 1 : linesAt(elapsed)) : 0,
      rest: rest && settles,
      shown: shownIndex(),
      selected: rest ? selected : null,
      hint: hint && settles,
      hintAlpha: hintFadeAt === null ? 1 : Math.max(0, 1 - (performance.now() - hintFadeAt) / HINT_FADE_MS),
    });
  }

  function tick() {
    loop = 0;
    if (state === "settle" && phaseAt(performance.now() - startedAt) === "rest") state = "rest";
    // The last frame of the fade draws the hint at zero, and the next frame has no hint.
    if (hintFadeAt !== null && performance.now() - hintFadeAt >= HINT_FADE_MS) endHintFade();
    draw();
    mark();
    // At rest the loop stops, so the scene does no work until a tap or a slide (story 38). A fade of the hint is the one
    // exception, and its loop stops when the fade ends.
    if (state === "settle" || state === "drift" || hintFadeAt !== null) loop = requestAnimationFrame(tick);
  }

  function endHintFade() {
    hint = false;
    hintFadeAt = null;
  }

  function stop() {
    if (loop) cancelAnimationFrame(loop);
    loop = 0;
  }

  function resize(width: number, height: number) {
    if (width <= 0 || height <= 0) return;
    // The device pixel ratio is capped at 2, so a dense screen does not paint four times the pixels (ADR 0027).
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    box = { width, height, padding: SCENE_PADDING };
    layout = layoutScene(scene, box, measure);
    scatter = scatterOf(scene.lights.length, box, plays + 1);
    dust = dustOf(DUST_COUNT, box, 7);
    draw();
    mark();
  }

  function enter() {
    // Under reduced motion the settled chart draws at once, and a re-entry does not replay it (story 37).
    if (motionOff) {
      state = settles ? "rest" : "drift";
      draw();
      mark();
      return;
    }
    plays += 1;
    scatter = scatterOf(scene.lights.length, box, plays);
    selected = null;
    startedAt = performance.now();
    state = settles ? "settle" : "drift";
    stop();
    tick();
  }

  function leave() {
    // A scene out of the view does no work. A settle that leaves plays again in full on the next entry.
    stop();
    if (settles && state === "settle") state = "idle";
    // A fade that the loop cannot finish ends now, so the hint does not wait for a loop that is stopped.
    if (hintFadeAt !== null) endHintFade();
  }

  /* The point of a pointer event in the pixels of the box. */
  const pointOf = (event: PointerEvent) => {
    const rect = canvas.getBoundingClientRect();
    return { x: event.clientX - rect.left, y: event.clientY - rect.top };
  };

  function select(at: { x: number; y: number }) {
    if (!layout) return;
    const index = nearestLight(layout.points, at);
    if (hint && hintFadeAt === null) {
      rememberHint();
      // Under reduced motion the hint goes at once. Else it fades over a short loop.
      if (motionOff) hint = false;
      else hintFadeAt = performance.now();
    }
    if (index !== selected) selected = index;
    // One frame per tap or slide, and no loop (PRD). The loop of the fade of the hint is the exception.
    draw();
    mark();
    if (hintFadeAt !== null && !loop) loop = requestAnimationFrame(tick);
  }

  // A tap or a slide during the settle does nothing. The selection waits for rest (PRD).
  const ready = () => settles && state === "rest";

  function onDown(event: PointerEvent) {
    if (!ready()) return;
    const at = pointOf(event);
    finger = { id: event.pointerId, ...at, slid: false };
  }

  function onMove(event: PointerEvent) {
    if (!finger || event.pointerId !== finger.id || !ready()) return;
    const at = pointOf(event);
    const dx = Math.abs(at.x - finger.x);
    const dy = Math.abs(at.y - finger.y);
    // A sideways move scrubs. An up or down move belongs to the page, as touch-action pan-y gives it to the scroll.
    if (finger.slid || (dx > SLIDE_PX && dx > dy)) {
      finger.slid = true;
      select(at);
    }
  }

  function onUp(event: PointerEvent) {
    if (!finger || event.pointerId !== finger.id) return;
    const slid = finger.slid;
    finger = null;
    if (!slid && ready()) select(pointOf(event));
  }

  function onCancel() {
    // The browser took the touch for a scroll, so the scene selects nothing (story 32).
    finger = null;
  }

  canvas.addEventListener("pointerdown", onDown);
  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerup", onUp);
  canvas.addEventListener("pointercancel", onCancel);

  const size = holder.getBoundingClientRect();
  resize(size.width, size.height);

  const sizes = typeof ResizeObserver === "undefined" ? null : new ResizeObserver((entries) => {
    const rect = entries.at(-1)?.contentRect;
    if (rect && (rect.width !== box.width || rect.height !== box.height)) resize(rect.width, rect.height);
  });
  sizes?.observe(holder);

  // The mono font can load after the first frame. Its real widths then place each label and the mark again.
  document.fonts?.ready.then(() => {
    if (!alive || !layout) return;
    layout = layoutScene(scene, box, measure);
    draw();
  });

  // A browser with no IntersectionObserver never reports the view, so the scene plays at once.
  const view =
    typeof IntersectionObserver === "undefined"
      ? null
      : new IntersectionObserver(
          (entries) => {
            const entry = entries.at(-1);
            if (!entry) return;
            if (entry.intersectionRatio >= ENTRY_RATIO && away) {
              away = false;
              enter();
            } else if (!entry.isIntersecting) {
              away = true;
              leave();
            }
          },
          { threshold: [0, ENTRY_RATIO] },
        );
  if (view) view.observe(holder);
  else enter();

  return () => {
    alive = false;
    stop();
    view?.disconnect();
    sizes?.disconnect();
    canvas.removeEventListener("pointerdown", onDown);
    canvas.removeEventListener("pointermove", onMove);
    canvas.removeEventListener("pointerup", onUp);
    canvas.removeEventListener("pointercancel", onCancel);
  };
}
