/**
 * Your team of the front door in local storage, so a manager picks once per browser and never logs in.
 * Every access is guarded, because a private window or blocked site data makes storage throw.
 */
// The key and the read live in the analyzer package, so the analyzer opens with the same team.
import { YOUR_TEAM_KEY } from "@cpc/analyzer/lib/your-team";

export { getYourTeam } from "@cpc/analyzer/lib/your-team";

export function setYourTeam(rosterId: number): void {
  try {
    localStorage.setItem(YOUR_TEAM_KEY, String(rosterId));
  } catch {
    // The page still holds Your team for this visit. The sheet asks again on the next load.
  }
}
