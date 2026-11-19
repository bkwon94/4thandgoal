/**
 * The state of Deadline week now, from the Lock. It reads the clock after the first paint and ticks each second, so the
 * static page and the browser agree on the first paint, and the countdown stays right while the page is open.
 */
"use client";

import { useEffect, useState } from "react";
import { type DeadlineState, deadlineState } from "../lib/deadline";

/* Null with no Lock, and before the first tick, because the static build has no clock of the reader. */
export function useDeadline(lock: number | null | undefined): DeadlineState | null {
  const [state, setState] = useState<DeadlineState | null>(null);
  useEffect(() => {
    if (lock === null || lock === undefined) {
      setState(null);
      return;
    }
    // A tick that gives the same state and text keeps the old object, so the page renders only when the text changes.
    const tick = () => {
      const next = deadlineState(Date.now(), lock);
      setState((old) => (old?.state === next.state && old.countdown === next.countdown ? old : next));
    };
    tick();
    // One tick each second carries the seconds of the last hours, and a minute ends within one second of the clock.
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [lock]);
  return state;
}
