/**
 * The seen key of the Tour, kept in local storage next to Your team, the opened Topics, and the Thread.
 * One read and one write: the Tour writes the key when Stop 1 opens, so each browser sees the Tour once (decision 04).
 */
export const TOUR_SEEN_KEY = "cpc.tour-seen";

/* Any value counts as seen. A read that throws counts as seen too, so a blocked store never shows the Tour on each visit. */
export function tourSeen(): boolean {
  try {
    return localStorage.getItem(TOUR_SEEN_KEY) !== null;
  } catch {
    return true;
  }
}

export function markTourSeen(): void {
  try {
    localStorage.setItem(TOUR_SEEN_KEY, "1");
  } catch {
    // The Tour still runs for this visit. It may show again on the next visit.
  }
}
