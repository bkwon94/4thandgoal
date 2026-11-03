/**
 * The manager's team pick on the waiver page in local storage, so a manager picks once per phone.
 * Every access is guarded, because a private window or blocked site data makes storage throw.
 */
// Its own key, so the pick never mixes with the passphrase or the analyzer's two sides.
const KEY = "cpc.waiver-team";

/* The saved roster id, or null. A value that is not a whole number reads as no pick. */
export function getTeamPick(): number | null {
  let raw: string | null;
  try {
    raw = localStorage.getItem(KEY);
  } catch {
    return null;
  }
  if (raw === null || !/^\d+$/.test(raw)) return null;
  return Number(raw);
}

export function setTeamPick(rosterId: number): void {
  try {
    localStorage.setItem(KEY, String(rosterId));
  } catch {
    // The page still holds the pick for this visit. The list asks again on the next load.
  }
}
