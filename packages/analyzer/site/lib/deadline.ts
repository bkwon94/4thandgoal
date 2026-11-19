/**
 * The clock of Deadline week: the phase and the countdown text from the time and the Lock, as one pure function.
 * Code says Lock. Site copy says "trade deadline", so no text here names the Lock.
 */

/* Open before the last hours, last-hours under 3 h to the Lock, closed from the Lock, and ended one day after the Lock.
   Deadline week ends by itself, so no deploy turns the Deadline banner off. */
export type DeadlinePhase = "open" | "last-hours" | "closed" | "ended";

/* The phase, and the countdown with a tilde before the Lock. The tilde says the Lock is an estimate for the end of the
   Monday night games. After the Lock there is no countdown. */
export type Deadline = { phase: DeadlinePhase; countdown: string | null };

const SECOND = 1000;
const HOUR = 3600 * SECOND;
const DAY = 24 * HOUR;
/* The last hours start under 3 h to the Lock. */
export const LAST_HOURS_MS = 3 * HOUR;
/* Deadline week ends one day after the Lock. */
export const ENDS_AFTER_MS = DAY;

const two = (n: number) => String(n).padStart(2, "0");

/* "2d 14h 05m" while open. In the last hours "2h 41m 10s", and a lead unit of zero drops, such as "5m 09s". A part of
   the last unit left counts as a whole unit, as a countdown does, so the text reads 05m until 4m 00s are left. */
function countdownOf(left: number, seconds: boolean): string {
  const unit = seconds ? SECOND : 60 * SECOND;
  const total = (Math.ceil(left / unit) * unit) / SECOND;
  const d = Math.floor(total / 86400);
  const h = Math.floor((total % 86400) / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (!seconds) return d > 0 ? `~${d}d ${h}h ${two(m)}m` : `~${h}h ${two(m)}m`;
  if (h > 0) return `~${h}h ${two(m)}m ${two(s)}s`;
  if (m > 0) return `~${m}m ${two(s)}s`;
  return `~${s}s`;
}

/* The state of Deadline week at the time `now`, for the Lock `lock`, both in ms since the epoch. */
export function deadlineOf(now: number, lock: number): Deadline {
  const left = lock - now;
  if (left <= -ENDS_AFTER_MS) return { phase: "ended", countdown: null };
  if (left <= 0) return { phase: "closed", countdown: null };
  if (left < LAST_HOURS_MS) return { phase: "last-hours", countdown: countdownOf(left, true) };
  return { phase: "open", countdown: countdownOf(left, false) };
}
