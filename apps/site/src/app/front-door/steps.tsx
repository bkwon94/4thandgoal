/**
 * The one step pattern of every wait on the front door: small mono lines, a braille spinner on the live step, and a
 * check on a done step. Under reduced motion the live step shows a static dot, and no frame timer runs.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { spinners } from "unicode-animations";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { QUICK, SLOW, STAGGER, fadeIn } from "./motion";

/* One step of a wait: its plain line, and whether its work is done. */
export type Step = { line: string; done: boolean };

/* The line of every wait before its first step comes, so each kind of Answer starts the same way. */
export const FIRST_LINE = "Reading the league";

/* The intent delay in ms before a wait shows its first line: --duration-slow. A kept Answer of the API comes back in
   about 200 ms, so it shows whole with no step line first (AT-8). A fresh Answer waits seconds, so its steps still show. */
export const INTENT_MS = SLOW * 1000;

/* Whether the intent delay of a wait has passed since the part mounted. */
export function useIntentDelay(ms = INTENT_MS): boolean {
  const [passed, setPassed] = useState(false);
  useEffect(() => {
    const timer = setTimeout(() => setPassed(true), ms);
    return () => clearTimeout(timer);
  }, [ms]);
  return passed;
}

/* The frames of the braille spinner, and the time of each frame in ms, from the frame data of unicode-animations. */
const BRAILLE = spinners.braille;

/* The braille spinner of the live step. It turns on one timer at 80 ms a frame, a steady linear loop with no ease. */
export function Spinner({ className = "" }: { className?: string }) {
  const [frame, setFrame] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => setFrame((count) => (count + 1) % BRAILLE.frames.length), BRAILLE.interval);
    return () => clearInterval(timer);
  }, []);
  return (
    <span data-mark="" aria-hidden className={className}>
      {BRAILLE.frames[frame]}
    </span>
  );
}

/* The mark of one step: the spinner while it is live, then the check, through a quick cross-blur in place, as the icon
   swap of transitions-dev. With motion off, the live step holds a static dot and the check only fades in. */
function Mark({ live }: { live: boolean }) {
  const off = useMotionOff();
  return (
    <span className="flex w-sp-4 flex-none items-center justify-center">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={live ? "live" : "done"}
          className="flex items-center justify-center"
          initial={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
          animate={off ? { opacity: 1 } : { opacity: 1, filter: "blur(0px)" }}
          exit={off ? { opacity: 0 } : { opacity: 0, filter: "blur(2px)" }}
          transition={fadeIn(QUICK)}
        >
          {!live ? (
            <span data-mark="" aria-hidden className="text-mute">
              ✔
            </span>
          ) : off ? (
            <span data-mark="" data-dot="" aria-hidden className="size-1.5 rounded-full bg-ink" />
          ) : (
            <Spinner className="text-ink" />
          )}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}

/* The steps of a wait, one line each. While `live`, a step that is not done is the live step, and the first line
   stands in until a step comes. Each live line ends in one "…", added here and nowhere else. Each step lands with a
   short rise from a soft blur, and with motion off it only fades in. Once the wait ends, each step shows done. `first`
   is the stand-in line, the first line of the league by default. */
export function Steps({ steps, live, first = FIRST_LINE }: { steps: Step[]; live: boolean; first?: string }) {
  const off = useMotionOff();
  const lines = live && steps.length === 0 ? [{ line: first, done: false }] : steps;
  if (lines.length === 0) return null;
  return (
    <div role="status">
      <ol aria-label="Steps" className="m-0 flex list-none flex-col gap-sp-1 p-0">
        {lines.map((step, index) => {
          const running = live && !step.done;
          return (
            <motion.li
              // The first line gives its place to the first step, so the list never jumps.
              key={index}
              data-state={running ? "live" : "done"}
              className="flex items-center gap-sp-2 font-mono text-meta leading-tight"
              initial={off ? { opacity: 0 } : { opacity: 0, y: 4, filter: "blur(2px)" }}
              animate={off ? { opacity: 1 } : { opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={fadeIn(QUICK, Math.min(index, 6) * STAGGER)}
            >
              <Mark live={running} />
              <span data-line="" className={`transition-colors duration-150 ${running ? "text-ink" : "text-mute"}`}>
                {running ? `${step.line}…` : step.line}
              </span>
            </motion.li>
          );
        })}
      </ol>
    </div>
  );
}
