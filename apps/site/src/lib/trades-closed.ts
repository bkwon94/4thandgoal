/**
 * Trades closed: the state of a client from its Lock onward. The client build and the Deadline banner both read it.
 * One pure function of the Lock and the time, so a test sets the time and never waits for a date.
 */

/* True at or after the Lock. A client with no Lock is never closed. Both values are ms since the epoch. */
export function tradesClosed(lock: number | null, now: number): boolean {
  return lock !== null && now >= lock;
}
