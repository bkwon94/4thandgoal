/**
 * Reads the published teams of the Live names from public/ at build time: the names of each roster across the season,
 * newest first, and the avatar URL of the newest week. The LiveNames part swaps each old name for the Live name.
 */
import type { PublishedTeam } from "@cpc/league/live-names";
import { listWeeks, loadWeek } from "./week-data";

/* Every name of a week page of the season counts, because a page of an older week shows the name of its own week. */
export function publishedTeams(season: number): PublishedTeam[] {
  const weeks = listWeeks()
    .filter((ref) => ref.season === String(season))
    .reverse();
  const teams = new Map<number, PublishedTeam>();
  for (const ref of weeks) {
    for (const team of Object.values(loadWeek(ref.season, ref.week).teams)) {
      const known = teams.get(team.roster_id);
      if (!known)
        teams.set(team.roster_id, {
          rosterId: team.roster_id,
          names: [team.name],
          avatarUrl: team.avatar_url,
        });
      else if (!known.names.includes(team.name)) known.names.push(team.name);
    }
  }
  return [...teams.values()];
}
