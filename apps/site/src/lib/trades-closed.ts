/**
 * Trades closed: the state of a client from its Lock onward. The client build and the Deadline banner both read it.
 * One pure function of the Lock and the time, so a test sets the time and never waits for a date.
 */

/* The line of a closed trade page. The API words the same line for a refused route, and the closed page of the site
   shows this constant, because the build writes it with no call to the API. */
export const CLOSED_LINE = "The trade deadline has passed. Trades open again next season.";

/* True at or after the Lock. A client with no Lock is never closed. Both values are ms since the epoch. */
export function tradesClosed(lock: number | null, now: number): boolean {
  return lock !== null && now >= lock;
}
