/**
 * The stage lines part: one short line under the title that changes every 2.5 s while a grade runs.
 * It is a separate part, so the hero can place it over any art. It is hidden from a screen reader, which hears the status only.
 */
"use client";

import { useEffect, useState } from "react";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";

// Each line holds for 2.5 s. The swap and the gap are the thinking states timing of transitions.dev.
const HOLD_MS = 2500;
const SWAP_MS = 150;
const GAP_MS = 50;

/* The line that the n-th tick shows. The list runs once, and then it starts again at line 2, because line 1 only opens the wait. */
function lineIndex(tick: number, count: number): number {
  return tick < count ? tick : 1 + ((tick - 1) % (count - 1));
}

/* The classes of a line live in globals.css. The sizer is the longest line, so the box keeps one width through each swap. */
export function StageLines({ lines }: { lines: string[] }) {
  const off = useMotionOff();
  const [tick, setTick] = useState(0);
  // The outgoing line stays for one swap, so the old line leaves while the new line rises in.
  const [leaving, setLeaving] = useState<{ tick: number; text: string } | null>(null);
  // A new line starts in its enter state and is released after the gap, so the browser paints the start before the move.
  const [entered, setEntered] = useState(true);

  useEffect(() => {
    const hold = setTimeout(() => {
      if (!off) {
        setLeaving({ tick, text: lines[lineIndex(tick, lines.length)] });
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
  return (
    <span aria-hidden="true" className="t-think text-lead leading-body">
      <span className="t-think-sizer">{longest}</span>
      {leaving && (
        <span key={leaving.tick} className="t-think-text is-exit" data-text={leaving.text}>
          {leaving.text}
        </span>
      )}
      <span key={tick} className={`t-think-text${off ? " is-still" : entered ? "" : " is-enter-start"}`} data-text={text}>
        {text}
      </span>
    </span>
  );
}
