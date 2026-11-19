/**
 * The Tour of the front door: four Stops, each a dim with a hole on one real control and a Stop card beside it.
 * It shows once per browser. Stop 1 writes the seen key, and the modal card keeps the real controls from a tap.
 */
"use client";

import { useEffect, useLayoutEffect, useState } from "react";
import { createPortal } from "react-dom";
import { StopCard, StopCardContent, StopCardLine, StopCardTitle } from "@cpc/design/ui/stop-card";
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
   modal layer is open. A layer leaves the page only after its exit, so the delay counts from the end of the last exit. */
export function Tour({ ready }: { ready: boolean }) {
  const [phase, setPhase] = useState<"wait" | "on" | "done">("wait");
  useEffect(() => {
    if (!ready || phase !== "wait") return;
    if (tourSeen()) {
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
    const replay = () => setPhase("on");
    window.addEventListener(REPLAY_EVENT, replay);
    return () => window.removeEventListener(REPLAY_EVENT, replay);
  }, [ready]);
  return phase === "on" ? <Stops onEnd={() => setPhase("done")} /> : null;
}

function Stops({ onEnd }: { onEnd: () => void }) {
  const [targets] = useState(findTargets);
  const [index, setIndex] = useState(0);
  const [open, setOpen] = useState(true);
  const target = targets[index];
  const last = index === targets.length - 1;
  // The target scrolls into view in the layout effect below, before the first frame reads the hole.
  const hole = useHole(target?.el ?? null);

  // Stop 1 writes the seen key, so Done, Skip, and a reload during the Tour each count as seen.
  useEffect(() => {
    markTourSeen();
  }, []);
  useEffect(() => {
    if (targets.length === 0) onEnd();
  }, [targets, onEnd]);
  // Each Stop moves its control into view, so each Stop is on the screen. The hole then reads the control in place.
  useLayoutEffect(() => {
    if (!target) return;
    target.el.scrollIntoView?.({ block: "nearest", inline: "nearest" });
    target.el.setAttribute("data-tour-target", "");
    return () => target.el.removeAttribute("data-tour-target");
  }, [target]);

  if (!target || !hole) return null;
  const next = () => (last ? setOpen(false) : setIndex(index + 1));
  const end = () => setOpen(false);
  // The card sits under a control in the top half of the screen, and over a control in the bottom half, so it never
  // covers the control. A card over the control sets its bottom edge, so it needs no measure of its own height.
  const below = hole.y + hole.height / 2 <= window.innerHeight / 2;
  const width = Math.min(320, window.innerWidth - CARD_EDGE * 2);
  const left = Math.min(Math.max(CARD_EDGE, hole.x + hole.width / 2 - width / 2), window.innerWidth - CARD_EDGE - width);
  const place = below ? { top: hole.y + hole.height + CARD_GAP } : { bottom: window.innerHeight - hole.y + CARD_GAP };

  return (
    <>
      {/* The spotlight sits above the top band and below the card. Its wide shadow is the dim, and it takes no press. It
          carries no stable id, so a hold on the dim sends no egg check. */}
      {open &&
        createPortal(
          <div
            aria-hidden
            data-tour-hole=""
            className="pointer-events-none fixed z-[60]"
            style={{ left: hole.x, top: hole.y, width: hole.width, height: hole.height, borderRadius: hole.radius, boxShadow: "0 0 0 200vmax var(--color-scrim)" }}
          />,
          document.body,
        )}
      <StopCard
        open={open}
        onOpenChangeComplete={(isOpen) => !isOpen && onEnd()}
        onDismissAttempt={(details) => (dismissStep(details.reason, last) === "next" ? next() : end())}
      >
        {/* The content fills the screen and takes no press, so a press anywhere off the card is a press outside. The
            important inset wins over the inline place that the positioner writes. */}
        <StopCardContent anchor={{ x: 0, y: 0 }} className="pointer-events-none !inset-0 h-dvh w-screen">
          <div
            data-tour-card=""
            className="pointer-events-auto fixed flex flex-col gap-sp-2 rounded-card border border-door-hair bg-card p-sp-4 pt-sp-3 shadow-drop"
            style={{ left, width, ...place }}
          >
            <div className="flex items-baseline justify-between gap-sp-3">
              <StopCardTitle className="m-0 text-body leading-tight font-semibold text-ink">{target.header}</StopCardTitle>
              <span className="flex-none font-mono text-meta leading-tight tracking-caps text-mute uppercase tabular-nums">
                {`${index + 1} of ${targets.length}`}
              </span>
            </div>
            {/* Each line sits hidden in the same cell, so the card always takes the height of the longest line, and a
                short line never moves Next under the thumb. The hidden lines draw from an attribute, so a search of the text finds
                each line once. */}
            <div className="grid text-lead leading-snug text-pretty">
              {targets.map((stop) => (
                <span key={stop.key} aria-hidden data-line={stop.line} className="invisible [grid-area:1/1] after:content-[attr(data-line)]" />
              ))}
              <StopCardLine className="m-0 text-ink-2 [grid-area:1/1]">{target.line}</StopCardLine>
            </div>
            <div className="mt-sp-1 flex items-center justify-between gap-sp-2">
              <span aria-hidden className="flex items-center gap-sp-1">
                {targets.map((stop, at) => (
                  <span
                    key={stop.key}
                    data-tour-dot=""
                    data-current={at === index ? "" : undefined}
                    className={`h-1.5 rounded-pill bg-ink ${at === index ? "w-[18px]" : "w-1.5 opacity-25"}`}
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
                  {last ? "Done" : "Next"}
                </button>
              </div>
            </div>
          </div>
        </StopCardContent>
      </StopCard>
    </>
  );
}
