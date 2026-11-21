/**
 * The state of Deadline week now, from the Lock, read from the clock each second. The Deadline banner and the analyzer
 * eyebrow both read it, so they show the same phase and countdown at the same second.
 */
"use client";

import { useEffect, useState } from "react";
import { type Deadline, deadlineOf } from "./deadline";

/* Null with no Lock, and until the first tick in the browser, because the static export renders at build time, and the
   time of the build is not the time of the reader. A tick that gives the same phase and text keeps the old state, so the
   page renders only when the text changes. */
export function useDeadline(lock: number | null | undefined): Deadline | null {
  const [deadline, setDeadline] = useState<Deadline | null>(null);
  useEffect(() => {
    if (lock === null || lock === undefined) {
      setDeadline(null);
      return;
    }
    const tick = () =>
      setDeadline((last) => {
        const next = deadlineOf(Date.now(), lock);
        return last !== null && last.phase === next.phase && last.countdown === next.countdown
          ? last
          : next;
      });
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [lock]);
  return deadline;
}
