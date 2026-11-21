/**
 * A fake clock for the tests of the analyzer: it fakes `setTimeout` and `setInterval`, and it can fix `Date` too.
 * The fake timers of `bun:test` drop a timer that is still pending when they end, and a Framer Motion part then stalls.
 */
import { setSystemTime, spyOn } from "bun:test";

/**
 * Starts the clock at 0 ms. The timers of the page move only when the test calls `advance`. The preload keeps its frame
 * timer on the real `setTimeout`, and `setImmediate` stays real, so a frame and a stream read still run. The spies end
 * with the test. After `setTime`, `Date` moves with the clock too.
 */
export function fakeClock() {
  let now = 0;
  let lastId = 0;
  // The real time at 0 ms of the clock, once a test fixes `Date`.
  let base: number | null = null;
  const pending = new Map<number, { at: number; every: number | null; run: () => void }>();
  const add = (run: () => void, delay: number, every: number | null) => {
    lastId += 1;
    pending.set(lastId, { at: now + delay, every, run });
    return lastId;
  };
  const drop = (id: number) => void pending.delete(id);
  const moveDate = () => {
    if (base !== null) setSystemTime(new Date(base + now));
  };
  spyOn(globalThis, "setTimeout").mockImplementation(((run: () => void, delay = 0) =>
    add(run, delay, null)) as unknown as typeof setTimeout);
  spyOn(globalThis, "setInterval").mockImplementation(((run: () => void, delay = 0) =>
    add(run, delay, Math.max(delay, 1))) as unknown as typeof setInterval);
  spyOn(globalThis, "clearTimeout").mockImplementation(drop as unknown as typeof clearTimeout);
  spyOn(globalThis, "clearInterval").mockImplementation(drop as unknown as typeof clearInterval);
  return {
    /** Fixes `Date` at `at` now, and moves it with each later `advance`. */
    setTime(at: Date) {
      base = at.getTime() - now;
      moveDate();
    },
    /** Runs each timer that falls due within `ms`, in order, as the timers that they set may fall due too. */
    advance(ms: number) {
      const end = now + ms;
      for (;;) {
        const due = [...pending]
          .filter(([, timer]) => timer.at <= end)
          .sort((a, b) => a[1].at - b[1].at)[0];
        if (!due) break;
        const [id, timer] = due;
        now = timer.at;
        if (timer.every === null) pending.delete(id);
        else timer.at = now + timer.every;
        moveDate();
        timer.run();
      }
      now = end;
      moveDate();
    },
  };
}
