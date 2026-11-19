/**
 * The state of Deadline week and the countdown text, from the time and the Lock. One pure function, so the Deadline
 * banner, the Trade Wire, and the analyzer eyebrow show the same state at the same second.
 */

/* open: more than 3 h to the Lock. last-hours: 3 h or less. closed: from the Lock to one day after it. ended: after that. */
export type DeadlineStateName = "open" | "last-hours" | "closed" | "ended";

export type DeadlineState = {
  state: DeadlineStateName;
  // "~2d 14h 05m", or "~2h 41m 10s" in the last hours. Null once the Lock has passed.
  countdown: string | null;
};

const SECOND = 1000;
const HOUR = 3600 * SECOND;
const DAY = 24 * HOUR;
// The last hours start 3 h before the Lock.
const LAST_HOURS = 3 * HOUR;

const two = (n: number) => String(n).padStart(2, "0");

/* The tilde marks the Lock as an estimate for the end of the Monday night games. Seconds show only in the last hours. */
function countdownOf(left: number, lastHours: boolean): string {
  const total = Math.floor(left / SECOND);
  const d = Math.floor(total / 86400);
  const h = Math.floor((total % 86400) / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (lastHours) return `~${h}h ${two(m)}m ${two(s)}s`;
  return d > 0 ? `~${d}d ${h}h ${two(m)}m` : `~${h}h ${two(m)}m`;
}

/* `now` and `lock` are epoch milliseconds. */
export function deadlineState(now: number, lock: number): DeadlineState {
  const left = lock - now;
  if (left <= 0) return { state: left > -DAY ? "closed" : "ended", countdown: null };
  const lastHours = left <= LAST_HOURS;
  return { state: lastHours ? "last-hours" : "open", countdown: countdownOf(left, lastHours) };
}
