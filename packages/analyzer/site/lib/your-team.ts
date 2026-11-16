/**
 * Your team of the front door in local storage, read by the front door and by the analyzer.
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
