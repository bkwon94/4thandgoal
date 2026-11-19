/**
 * The stage lines part: one short line under the title that changes every 2.5 s while a grade runs, or that the caller drives.
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
   The part measures each new line against its box. A line that fits does not move. A line that does not fit scrolls from
   right to left until its end is in view, so no line stays cut off at the edge of the hero. With motion off, the line
   and the sizer share one cell and both wrap, so a long line wraps in full, does not move, and the box keeps one height.
   The mesh then cuts its hole under the sizer only, because the hole of a line that swaps would redraw a mesh that must
   stay still. */
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
  // A new line starts in its enter state, and the part releases it after the gap, so the browser paints the start before the move.
  const [entered, setEntered] = useState(true);

  // A list of one line has no clock. The line holds until the caller sends a new list of one line, and then it swaps
  // with the same motion as a timed line. The Finder wait drives it from the real steps of its stream. The swap runs
  // before the paint, so the new line never shows a frame outside its enter state.
  const driven = lines.length === 1;
  const [drivenText, setDrivenText] = useState(lines[0]);
  useLayoutEffect(() => {
    if (!driven || lines[0] === drivenText) return;
    if (!off) {
      setLeaving({ tick, text: drivenText, over: overRef.current });
      setEntered(false);
    }
    setDrivenText(lines[0]);
    setTick(tick + 1);
  }, [driven, lines, drivenText, tick, off]);

  useEffect(() => {
    if (driven) return;
    const hold = setTimeout(() => {
      if (!off) {
        setLeaving({ tick, text: lines[lineIndex(tick, lines.length)], over: overRef.current });
        setEntered(false);
      }
      setTick(tick + 1);
    }, HOLD_MS);
    return () => clearTimeout(hold);
  }, [tick, lines, off, driven]);

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

  const text = driven ? drivenText : lines[lineIndex(tick, lines.length)];
  // A driven line is the only line, so the sizer is the line on the screen.
  const longest = driven ? drivenText : lines.reduce((a, b) => (b.length > a.length ? b : a), "");
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
    <span ref={box} aria-hidden="true" className={`t-think text-body leading-body${off ? " is-still" : ""}`}>
      <span className="t-think-sizer">{longest}</span>
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
      <span
        ref={live}
        key={tick}
        className={`t-think-text${state}${over > 0 ? " is-scroll" : ""}`}
        data-text={text}
        data-mesh-skip={off ? "" : undefined}
        style={scroll}
      >
        {text}
      </span>
    </span>
  );
}
