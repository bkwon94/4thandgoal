/**
 * Your team of the front door in local storage, so a manager picks once per browser and never logs in.
 * Every access is guarded, because a private window or blocked site data makes storage throw.
 */
// Its own key, so Your team never mixes with the passphrase, the waiver pick, or the two sides of the analyzer.
export const YOUR_TEAM_KEY = "cpc.your-team";

/* The stored roster id, or null. A value that is not a whole number reads as no pick. */
export function getYourTeam(): number | null {
  let raw: string | null;
  try {
    raw = localStorage.getItem(YOUR_TEAM_KEY);
  } catch {
    return null;
  }
  if (raw === null || !/^\d+$/.test(raw)) return null;
  return Number(raw);
}

export function setYourTeam(rosterId: number): void {
  try {
    localStorage.setItem(YOUR_TEAM_KEY, String(rosterId));
  } catch {
    // The page still holds Your team for this visit. The sheet asks again on the next load.
  }
}
