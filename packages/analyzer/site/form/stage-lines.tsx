/**
 * The stage lines part: one short line under the title that changes every 2.5 s while a grade runs.
 * It is a separate part, so the hero can place it over any art. It is hidden from a screen reader, which hears the status only.
 */
"use client";

import { type CSSProperties, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";

// Each line holds for 2.5 s. The swap and the gap are the thinking states timing of transitions.dev.
const HOLD_MS = 2500;
const SWAP_MS = 150;
const GAP_MS = 50;
// A line wider than its box scrolls once to its end. It waits until the line has risen in and the reader sees where it
// starts, moves for 1.3 s, and then rests at its end for the last 0.6 s, so the end is readable before the swap.
const SCROLL_DELAY_MS = 600;
const SCROLL_MS = 1300;

/* The line that the n-th tick shows. The list runs once, and then it starts again at line 2, because line 1 only opens the wait. */
function lineIndex(tick: number, count: number): number {
  return tick < count ? tick : 1 + ((tick - 1) % (count - 1));
}

/* The classes of a line live in globals.css. The sizer is the longest line, so the box keeps one height through each swap.
   Each new line is measured against its box. A line that fits does not move. A line that does not fit scrolls from
   right to left until its end is in view, so no line stays cut off at the edge of the hero. With motion off, the line
   sits in the flow with no sizer, so a long line wraps in full and does not move. */
export function StageLines({ lines }: { lines: string[] }) {
  const off = useMotionOff();
  const [tick, setTick] = useState(0);
  // The outgoing line stays for one swap, so the old line leaves while the new line rises in.
  const [leaving, setLeaving] = useState<{ tick: number; text: string; over: number } | null>(null);
  // The px by which the line of a tick is wider than its box: 0 for a line that fits, and always 0 with motion off.
  // It is kept with its tick, so a new line is measured at rest and never takes the scroll of the line before it.
  const [fit, setFit] = useState({ tick: 0, over: 0 });
  const over = fit.tick === tick ? fit.over : 0;
  // The hold reads the measure from a ref, so a new measure does not restart the 2.5 s of the line.
  const overRef = useRef(0);
  overRef.current = over;
  const box = useRef<HTMLSpanElement>(null);
  const live = useRef<HTMLSpanElement>(null);

  // The measure runs before the paint, so a long line never shows a frame in the wrong place.
  useLayoutEffect(() => {
    const room = box.current?.clientWidth ?? 0;
    const width = live.current?.scrollWidth ?? 0;
    setFit({ tick, over: off ? 0 : Math.max(0, Math.ceil(width - room)) });
  }, [tick, off]);
  // A new line starts in its enter state and is released after the gap, so the browser paints the start before the move.
  const [entered, setEntered] = useState(true);

  useEffect(() => {
    const hold = setTimeout(() => {
      if (!off) {
        setLeaving({ tick, text: lines[lineIndex(tick, lines.length)], over: overRef.current });
        setEntered(false);
      }
      setTick(tick + 1);
    }, HOLD_MS);
    return () => clearTimeout(hold);
  }, [tick, lines, off]);

  useEffect(() => {
    if (entered) return;
    const release = setTimeout(() => setEntered(true), GAP_MS);
    return () => clearTimeout(release);
  }, [entered]);

  useEffect(() => {
    if (!leaving) return;
    const gone = setTimeout(() => setLeaving(null), SWAP_MS + GAP_MS);
    return () => clearTimeout(gone);
  }, [leaving]);

  const text = lines[lineIndex(tick, lines.length)];
  const longest = lines.reduce((a, b) => (b.length > a.length ? b : a), "");
  const state = off ? " is-still" : entered ? "" : " is-enter-start";
  const scroll =
    over > 0
      ? ({
          "--think-scroll": `-${over}px`,
          "--think-scroll-delay": `${SCROLL_DELAY_MS}ms`,
          "--think-scroll-time": `${SCROLL_MS}ms`,
        } as CSSProperties)
      : undefined;
  return (
    <span ref={box} aria-hidden="true" className="t-think text-body leading-body">
      {!off && <span className="t-think-sizer">{longest}</span>}
      {leaving && (
        // The outgoing line leaves from the place where it rests, so a long line does not jump back to its start.
        <span
          key={leaving.tick}
          className="t-think-text is-exit"
          data-text={leaving.text}
          style={leaving.over > 0 ? { translate: `-${leaving.over}px 0` } : undefined}
        >
          {leaving.text}
        </span>
      )}
      <span ref={live} key={tick} className={`t-think-text${state}${over > 0 ? " is-scroll" : ""}`} data-text={text} style={scroll}>
        {text}
      </span>
    </span>
  );
}
