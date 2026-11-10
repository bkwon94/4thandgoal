/**
 * Reads the data of the front door at build time: the latest week and the teams of the league for the sheet of Your team.
 * Each team comes from the table of the latest week page, so the sheet shows the same names and avatars as the week page.
 */
import { listWeeks, loadWeek } from "./week-data";

/* One team of the sheet. The rank and the record come from the table of the latest week. */
export type DoorTeam = { id: number; name: string; avatar: string | null; wins: number; losses: number; rank: number };

export type FrontDoorData = { week: number; teams: DoorTeam[] };

/* The data of the latest published week, or null when no week is published yet. listWeeks sorts by season, then by
   week, so the last ref is the latest. */
export function loadFrontDoor(): FrontDoorData | null {
  const ref = listWeeks().at(-1);
  if (!ref) return null;
  const page = loadWeek(ref.season, ref.week);
  // The week JSON paths are relative to the week folder, so each avatar gets the folder in front.
  const folder = `/${ref.season}/${ref.week}`;
  const teams = page.table.map(({ team, standing }) => {
    const avatar = page.avatars[String(team.roster_id)];
    return {
      id: team.roster_id,
      name: team.name,
      avatar: avatar ? `${folder}/${avatar}` : null,
      wins: standing.wins,
      losses: standing.losses,
      rank: standing.rank,
    };
  });
  // A manager looks for a name, so the sheet lists the teams by name and not by rank.
  teams.sort((a, b) => a.name.localeCompare(b.name, "en", { sensitivity: "base" }));
  return { week: page.week, teams };
}
