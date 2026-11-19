/**
 * The Tour of the front door: four Stops, each a dim with a hole on one real control and a Stop card beside it.
 * It shows once per browser. Stop 1 writes the seen key, and the modal card keeps the real controls from a tap.
 */
"use client";

import { AnimatePresence, motion, useIsPresent } from "framer-motion";
import { type ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { StopCard, StopCardContent, StopCardLine, StopCardTitle } from "@cpc/design/ui/stop-card";
import { BLUR_SMALL, EASE_IN_OUT, FAST, GLIDE, QUICK, SCALE_MEDIUM, SCALE_TINY, SMOOTH, fadeIn } from "./motion";
import { markTourSeen, tourSeen } from "./tour-store";

/* The four Stops in order, with the copy of decision 03. Each target has an accessible name already, so the Tour finds it
   by that name and adds no hook to the control. Stop 4 takes the menu button or the pill bar, whichever one shows. */
export const STOPS = [
  {
    key: "suggestions",
    header: "Suggestions",
    line: "Picks for your team right now. Tap one to open it, or tap More for the full list.",
    selector: '[role="group"][aria-label="Suggestions"]',
  },
  {
    key: "ask",
    header: "Ask",
    line: "Type any question about your team or your league, such as start or sit, a trade, or the playoff race.",
    selector: 'form[aria-label="Ask"]',
  },
  {
    key: "team",
    header: "Your team",
    line: "Tap to see the league as another manager.",
    selector: 'button[aria-label^="Your team:"]',
  },
  {
    key: "menu",
    header: "Menu",
    line: "Every page of the league lives here.",
    selector: 'button[aria-label="Open the menu"], nav[aria-label="Site menu"]',
  },
] as const;

type Stop = (typeof STOPS)[number];
type Target = Stop & { el: HTMLElement };
type Box = { x: number; y: number; width: number; height: number };
type Hole = Box & { radius: number };

/* The Tour waits for the entrance of the dock to settle, so Stop 1 measures its control at rest. */
const START_DELAY_MS = 600;
/* The keyboard of a phone closes over about 250 ms. The Tour starts once the viewport holds still this long after a blur. */
const KEYBOARD_SETTLE_MS = 350;
/* The room between the visual box of the control and the edge of the hole, on each side. A small box, such as the
   menu icon, gets more room, so its hole reads as a shape and not as a ring. */
const HOLE_PAD = 6;
const SMALL_PAD = 10;
const SMALL_BOX = 28;
/* The Suggestions row bleeds to both edges and scrolls, so its visual box stops this far inside the screen. */
const SCREEN_INSET = 8;
/* The gap between the hole and the card, and the least room between the card and the edge of the screen. */
const CARD_GAP = 12;
const CARD_EDGE = 16;
/* A smooth scroll ends when no part of the page scrolls for this long. The cap ends the wait if a scroll never settles. */
const SCROLL_SETTLE_MS = 100;
const SCROLL_CAP_MS = 1000;

/* What a refused dismiss does. A press on the dim goes to the next Stop, so a stray tap does not end the Tour, and on
   Stop 4 it ends the Tour. Escape and the Back of Android count as Skip. */
export function dismissStep(reason: string, last: boolean): "next" | "end" {
  return reason === "outside-press" && !last ? "next" : "end";
}

/* Whether a control shows. The site hides one of the menu button and the pill bar with a class at each width. A browser
   with no checkVisibility, and jsdom, read the display of the control and of each parent. */
function shown(el: HTMLElement): boolean {
  if (typeof el.checkVisibility === "function") return el.checkVisibility();
  for (let node: HTMLElement | null = el; node; node = node.parentElement) {
    if (getComputedStyle(node).display === "none") return false;
  }
  return true;
}

function findTargets(): Target[] {
  return STOPS.flatMap((stop) => {
    const el = [...document.querySelectorAll<HTMLElement>(stop.selector)].find(shown);
    return el ? [{ ...stop, el }] : [];
  });
}

/* Whether a part paints its own surface: a fill with some alpha, a border, or a shadow. */
function painted(el: Element): boolean {
  const style = getComputedStyle(el);
  const fill = style.backgroundColor;
  const clear = fill === "transparent" || /rgba\(.*,\s*0\)$/.test(fill);
  return !clear || parseFloat(style.borderTopWidth) > 0 || style.boxShadow !== "none";
}

/* The rects that the eye sees in a control. A control that paints its own surface counts whole, as the ask box does.
   A plain control counts only the parts inside it that show: the icon of the menu button, and the avatar, the name, and
   the mark of the team switch. Inside a row, each link and each button counts whole, as a chip does. */
function visualRects(el: Element, depth = 0): DOMRect[] {
  if (painted(el) || (depth > 0 && el.matches("a, button, svg, img"))) return [el.getBoundingClientRect()];
  const rects: DOMRect[] = [];
  for (const node of el.childNodes) {
    if (node.nodeType === Node.TEXT_NODE && node.textContent?.trim()) {
      const range = document.createRange();
      range.selectNodeContents(node);
      // jsdom gives a range no rect, so a test there falls back to the box of the control.
      if (typeof range.getBoundingClientRect === "function") rects.push(range.getBoundingClientRect());
    } else if (node instanceof HTMLElement || node instanceof SVGElement) {
      if (getComputedStyle(node).display !== "none" && getComputedStyle(node).opacity !== "0") rects.push(...visualRects(node, depth + 1));
    }
  }
  return rects.filter((rect) => rect.width > 0 && rect.height > 0);
}

/* The visual box of a control, not its hit box, kept inside the screen. */
function visualBox(el: HTMLElement): Box {
  const own = el.getBoundingClientRect();
  const rects = visualRects(el);
  const all = rects.length > 0 ? rects : [own];
  const left = Math.max(SCREEN_INSET, Math.min(...all.map((r) => r.left)));
  const right = Math.min(window.innerWidth - SCREEN_INSET, Math.max(...all.map((r) => r.right)));
  const top = Math.min(...all.map((r) => r.top));
  const bottom = Math.max(...all.map((r) => r.bottom));
  return { x: left, y: top, width: right - left, height: bottom - top };
}

/* The hole: the visual box with the same pad on each side. Each control on the front door is a pill or a circle, so
   the radius is half the height. A square box, as the menu icon, then gets a circle. */
function measure(el: HTMLElement): Hole {
  const box = visualBox(el);
  const pad = box.height < SMALL_BOX ? SMALL_PAD : HOLE_PAD;
  const height = box.height + pad * 2;
  return { x: box.x - pad, y: box.y - pad, width: box.width + pad * 2, height, radius: height / 2 };
}

const sameHole = (a: Hole | null, b: Hole) =>
  a !== null && a.x === b.x && a.y === b.y && a.width === b.width && a.height === b.height;

/* The hole of a control, read again when the control changes size, the window or the visual viewport changes, or any
   part of the page scrolls. So the hole follows a resize, a turn of the phone, a zoom, and a scroll. One frame per
   burst of events gives one read. CSS anchor positioning is out, because iOS 18 Safari does not support it. */
function useHole(el: HTMLElement | null): Hole | null {
  const [hole, setHole] = useState<Hole | null>(null);
  useLayoutEffect(() => {
    if (!el) return;
    let frame = 0;
    const read = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const next = measure(el);
        setHole((old) => (sameHole(old, next) ? old : next));
      });
    };
    setHole(measure(el));
    const observer = typeof ResizeObserver === "function" ? new ResizeObserver(read) : null;
    observer?.observe(el);
    const viewport = window.visualViewport;
    window.addEventListener("resize", read);
    document.addEventListener("scroll", read, true);
    viewport?.addEventListener("resize", read);
    viewport?.addEventListener("scroll", read);
    return () => {
      cancelAnimationFrame(frame);
      observer?.disconnect();
      window.removeEventListener("resize", read);
      document.removeEventListener("scroll", read, true);
      viewport?.removeEventListener("resize", read);
      viewport?.removeEventListener("scroll", read);
    };
  }, [el]);
  return hole;
}

/* Whether a modal layer is open, such as the team sheet, the passphrase modal, or an Announcement. Two layers must never
   fight, so the Tour reads the page itself and not a list of the layers that it knows. */
function modalOpen(): boolean {
  return document.querySelector('[aria-modal="true"]') !== null;
}

/* The focused field that opens the keyboard of a phone, if one has the focus. */
function focusedField(): HTMLElement | null {
  const el = document.activeElement;
  return el instanceof HTMLElement && el.matches("input, textarea, [contenteditable]:not([contenteditable='false'])") ? el : null;
}

/* The replay controls sit in the shell, outside the front door, so they reach the Tour by one window event. */
const REPLAY_EVENT = "cpc:tour-replay";

export function replayTour() {
  window.dispatchEvent(new Event(REPLAY_EVENT));
}

/* `ready` is true while Your team is set and no team sheet and no passphrase modal shows. The Tour decides once, on the
   first ready render: a browser with the seen key, or with a store that throws, gets no Tour. Then it waits until no
   modal layer is open. A layer leaves the page only after its exit, so the delay counts from the end of the last exit.
   A replay passes the same start gate in the phase "replay", but it does not read the seen key. */
export function Tour({ ready }: { ready: boolean }) {
  const [phase, setPhase] = useState<"wait" | "replay" | "on" | "done">("wait");
  useEffect(() => {
    if (!ready || (phase !== "wait" && phase !== "replay")) return;
    if (phase === "wait" && tourSeen()) {
      setPhase("done");
      return;
    }
    let timer: number | undefined;
    let blocked: boolean | undefined;
    // A keyboard that stays open covers the Stop, so a focused field loses the focus first. Each step of the keyboard
    // lift resizes the viewport, so the Tour starts only after the viewport holds still.
    const settle = () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(start, KEYBOARD_SETTLE_MS);
    };
    const start = () => {
      const field = focusedField();
      if (!field) return setPhase("on");
      field.blur();
      window.visualViewport?.addEventListener("resize", settle);
      window.addEventListener("resize", settle);
      settle();
    };
    // Only a change from open to clear starts the delay again, so the many changes of a busy page do not hold the Tour off.
    const check = () => {
      const now = modalOpen();
      if (now === blocked) return;
      blocked = now;
      window.clearTimeout(timer);
      if (!now) timer = window.setTimeout(start, START_DELAY_MS);
    };
    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, { subtree: true, childList: true, attributes: true, attributeFilter: ["aria-modal"] });
    check();
    return () => {
      observer.disconnect();
      window.clearTimeout(timer);
      window.visualViewport?.removeEventListener("resize", settle);
      window.removeEventListener("resize", settle);
    };
  }, [ready, phase]);
  // A replay starts at Stop 1 and does not read the seen key. A replay during the Tour changes nothing.
  useEffect(() => {
    if (!ready) return;
    const replay = () => setPhase((now) => (now === "on" ? now : "replay"));
    window.addEventListener(REPLAY_EVENT, replay);
    return () => window.removeEventListener(REPLAY_EVENT, replay);
  }, [ready]);
  return phase === "on" ? <Stops onEnd={() => setPhase("done")} /> : null;
}

/* Move a control into view, then call `done` once the page holds still. A control that is in view already calls `done`
   at once, so the Stop shows in the same frame. Under reduced motion the scroll is not smooth. The return stops the wait. */
function scrollThen(el: HTMLElement, smooth: boolean, done: () => void): () => void {
  const rect = el.getBoundingClientRect();
  const inView = rect.top >= 0 && rect.bottom <= window.innerHeight && rect.left >= -1 && rect.right <= window.innerWidth + 1;
  el.scrollIntoView?.({ block: "nearest", inline: "nearest", behavior: smooth ? "smooth" : "instant" });
  if (inView) {
    done();
    return () => {};
  }
  // WebKit sends no scrollend, so the wait counts the time since the last scroll of any part of the page.
  const start = performance.now();
  let moved = start;
  let frame = 0;
  const onScroll = () => (moved = performance.now());
  const stop = () => {
    cancelAnimationFrame(frame);
    document.removeEventListener("scroll", onScroll, true);
  };
  const check = () => {
    const now = performance.now();
    if (now - moved < SCROLL_SETTLE_MS && now - start < SCROLL_CAP_MS) frame = requestAnimationFrame(check);
    else {
      stop();
      done();
    }
  };
  document.addEventListener("scroll", onScroll, true);
  frame = requestAnimationFrame(check);
  return stop;
}

/* The side of its control that the card takes: under a control in the top half of the screen, and over a control in the
   bottom half, so it never covers the control. */
const sideOf = (hole: Hole) => (hole.y + hole.height / 2 <= window.innerHeight / 2 ? "below" : "above");

/* Text swap soft (34): the old text and the new text cross-blur in one cell, with no move. Under reduced motion only
   the opacity changes. The old text is hidden from a screen reader while it leaves, so the card has one name. */
function Swap({ id, off, className = "", children }: { id: string | number; off: boolean; className?: string; children: ReactNode }) {
  return (
    <span className={`grid ${className}`}>
      <AnimatePresence initial={false}>
        <SwapText key={id} off={off}>
          {children}
        </SwapText>
      </AnimatePresence>
    </span>
  );
}

function SwapText({ off, children }: { off: boolean; children: ReactNode }) {
  const present = useIsPresent();
  const blur = off ? undefined : { filter: BLUR_SMALL };
  const sharp = off ? undefined : { filter: "blur(0px)" };
  return (
    <motion.span
      aria-hidden={present ? undefined : true}
      className="[grid-area:1/1]"
      initial={{ opacity: 0, ...blur }}
      animate={{ opacity: 1, ...sharp }}
      exit={{ opacity: 0, ...blur }}
      transition={{ duration: QUICK, ease: EASE_IN_OUT }}
    >
      {children}
    </motion.span>
  );
}

function Stops({ onEnd }: { onEnd: () => void }) {
  const off = useMotionOff();
  const [targets] = useState(findTargets);
  // `index` is the Stop that Next steps through. `at` is the Stop of the hole: it takes `index` once the scroll ends.
  // `cardAt` is the Stop of the card copy: it takes `at` with the glide, or once the card is back after a fade.
  const [index, setIndex] = useState(0);
  const [at, setAt] = useState<number | null>(null);
  const [cardAt, setCardAt] = useState(0);
  const [open, setOpen] = useState(true);
  const target = at === null ? undefined : targets[at];
  const last = index === targets.length - 1;
  const hole = useHole(target?.el ?? null);
  const [side, setSide] = useState<"below" | "above" | null>(null);
  const [snap, setSnap] = useState(false);
  const held = useRef<{ x: number; y: number } | null>(null);
  const holeLanded = useRef(true);
  const cardOut = useRef(false);

  // Stop 1 writes the seen key, so Done, Skip, and a reload during the Tour each count as seen.
  useEffect(() => {
    markTourSeen();
  }, []);
  useEffect(() => {
    if (targets.length === 0) onEnd();
  }, [targets, onEnd]);
  // Each Stop moves its control into view, so each Stop is on the screen. The scroll ends first, and then the hole
  // reads the control in place and glides. So the hole never chases a control that still moves.
  useLayoutEffect(() => {
    const goal = targets[index];
    if (!goal) return;
    return scrollThen(goal.el, !off, () => setAt(index));
  }, [targets, index, off]);
  useLayoutEffect(() => {
    if (!target) return;
    target.el.setAttribute("data-tour-target", "");
    holeLanded.current = false;
    cardOut.current = false;
    return () => target.el.removeAttribute("data-tour-target");
  }, [target]);

  const wanted = hole ? sideOf(hole) : null;
  // The card leaves and comes back when it must change side, so it never sweeps across the hole. Under reduced motion it
  // leaves on each move, because it does not glide: it fades out at the old Stop and fades in at the new one.
  const away = hole !== null && side !== null && at !== null && (wanted !== side || (off && cardAt !== at));
  // A move on the same side keeps the card: the copy changes with the glide.
  useLayoutEffect(() => {
    if (wanted === null || at === null) return;
    if (side === null) setSide(wanted);
    else if (!away && cardAt !== at) setCardAt(at);
  }, [wanted, side, away, cardAt, at]);
  // After the snap to the new place, the next move glides again.
  useEffect(() => {
    if (!snap) return;
    const frame = requestAnimationFrame(() => setSnap(false));
    return () => cancelAnimationFrame(frame);
  }, [snap]);
  // The card comes back once it is out and the hole has landed: it snaps to the new side, and then fades in.
  const land = () => {
    if (!away || !holeLanded.current || !cardOut.current || at === null) return;
    cardOut.current = false;
    setSide(wanted);
    setCardAt(at);
    setSnap(true);
  };

  if (!target || !hole || side === null) return null;
  const shown = targets[cardAt];
  const next = () => (last ? setOpen(false) : setIndex(index + 1));
  const end = () => setOpen(false);
  const width = Math.min(320, window.innerWidth - CARD_EDGE * 2);
  // The anchor of the card is the middle of its edge on the side of the hole. A card over the control draws up from its
  // anchor, so it needs no measure of its own height.
  const place = {
    x: Math.min(Math.max(CARD_EDGE, hole.x + hole.width / 2 - width / 2), window.innerWidth - CARD_EDGE - width),
    y: side === "below" ? hole.y + hole.height + CARD_GAP : hole.y - CARD_GAP,
  };
  // While the card is away, it holds its place, so it does not sweep across the hole as it fades.
  const card = away && held.current ? held.current : place;
  held.current = card;
  // The hole and the card ride the same spring, so the two never part. Under reduced motion the hole jumps.
  const move = off || snap ? { duration: 0 } : GLIDE;

  return (
    <>
      {/* The spotlight sits above the top band and below the card. Its wide shadow is the dim, and it takes no press. It
          carries no stable id, so a hold on the dim sends no egg check. */}
      {createPortal(
        <motion.div
          aria-hidden
          data-tour-hole=""
          className="pointer-events-none fixed top-0 left-0 z-[60]"
          style={{ boxShadow: "0 0 0 200vmax var(--color-scrim)" }}
          initial={{ opacity: 0, x: hole.x, y: hole.y, width: hole.width, height: hole.height, borderRadius: hole.radius }}
          animate={{ opacity: open ? 1 : 0, x: hole.x, y: hole.y, width: hole.width, height: hole.height, borderRadius: hole.radius }}
          transition={{ default: off ? { duration: 0 } : GLIDE, opacity: fadeIn(open ? FAST : QUICK) }}
          onAnimationComplete={() => {
            holeLanded.current = true;
            land();
          }}
        />,
        document.body,
      )}
      <StopCard
        open={open}
        onOpenChangeComplete={(isOpen) => !isOpen && onEnd()}
        onDismissAttempt={(details) => (dismissStep(details.reason, last) === "next" ? next() : end())}
      >
        {/* The content fills the screen and takes no press, so a press anywhere off the card is a press outside. The
            important inset wins over the inline place that the positioner writes. Its fade on close is the wait of the
            exit, so the card and the dim leave together on QUICK. */}
        <StopCardContent
          anchor={{ x: 0, y: 0 }}
          className="pointer-events-none !inset-0 h-dvh w-screen transition-opacity data-[ending-style]:opacity-0"
          style={{ transitionDuration: `${QUICK}s`, transitionTimingFunction: `cubic-bezier(${SMOOTH.join(", ")})` }}
        >
          {/* Menu dropdown (05): the card grows from its edge on the side of the hole at 0.97 on FAST, and leaves at 0.99
              on QUICK. Under reduced motion it keeps a scale of 1. */}
          <motion.div
            className="pointer-events-none fixed top-0 left-0"
            style={{ width, transformOrigin: "50% 0%" }}
            initial={{ ...card, opacity: 0, scale: off ? 1 : SCALE_MEDIUM }}
            animate={{ ...card, opacity: away ? 0 : 1, scale: open || off ? 1 : SCALE_TINY }}
            transition={{
              x: move,
              y: move,
              opacity: fadeIn(away ? QUICK : FAST),
              scale: { duration: open ? FAST : QUICK, ease: SMOOTH },
            }}
            onAnimationComplete={() => {
              if (!away) return;
              cardOut.current = true;
              land();
            }}
          >
            <div
              data-tour-card=""
              className="pointer-events-auto flex flex-col gap-sp-2 rounded-card border border-door-hair bg-card p-sp-4 pt-sp-3 shadow-drop"
              style={{ translate: side === "above" ? "0 -100%" : undefined }}
            >
              <div className="flex items-baseline justify-between gap-sp-3">
                <StopCardTitle className="m-0 text-body leading-tight font-semibold text-ink">
                  <Swap id={shown.key} off={off}>
                    {shown.header}
                  </Swap>
                </StopCardTitle>
                <span className="flex-none font-mono text-meta leading-tight tracking-caps text-mute uppercase tabular-nums">
                  <Swap id={cardAt} off={off}>{`${cardAt + 1} of ${targets.length}`}</Swap>
                </span>
              </div>
              {/* Each line sits hidden in the same cell, so the card always takes the height of the longest line, and a
                  short line never moves Next under the thumb. The hidden lines draw from an attribute, so a search of the text finds
                  each line once. */}
              <div className="grid text-lead leading-snug text-pretty">
                {targets.map((stop) => (
                  <span key={stop.key} aria-hidden data-line={stop.line} className="invisible [grid-area:1/1] after:content-[attr(data-line)]" />
                ))}
                <StopCardLine className="m-0 text-ink-2 [grid-area:1/1]">
                  <Swap id={shown.key} off={off}>
                    {shown.line}
                  </Swap>
                </StopCardLine>
              </div>
              <div className="mt-sp-1 flex items-center justify-between gap-sp-2">
                {/* The current dot stretches into a short bar, on the slide of Tabs sliding (16). */}
                <span aria-hidden className="flex items-center gap-sp-1">
                  {targets.map((stop, dot) => (
                    <motion.span
                      key={stop.key}
                      data-tour-dot=""
                      data-current={dot === cardAt ? "" : undefined}
                      className="h-1.5 rounded-pill bg-ink"
                      initial={false}
                      animate={{ width: dot === cardAt ? 18 : 6, opacity: dot === cardAt ? 1 : 0.25 }}
                      transition={off ? { duration: 0 } : { duration: FAST, ease: SMOOTH }}
                    />
                  ))}
                </span>
                <div className="flex items-center gap-sp-1">
                  <button
                    type="button"
                    onClick={end}
                    className="press flex min-h-touch items-center rounded-pill px-sp-3 text-body font-semibold text-mute hover-fine:text-ink"
                  >
                    Skip
                  </button>
                  <button
                    type="button"
                    onClick={next}
                    className="press flex min-h-touch min-w-[5.5rem] items-center justify-center rounded-pill bg-accent px-sp-5 text-body font-semibold text-on-dark"
                  >
                    {cardAt === targets.length - 1 ? "Done" : "Next"}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </StopCardContent>
      </StopCard>
    </>
  );
}
