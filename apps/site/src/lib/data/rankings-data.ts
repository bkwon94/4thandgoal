/**
 * Reads the season rankings file from public/ at build time, and the avatars of the latest published week.
 * The file sits beside the week folders, so a missing file means the pipeline has not written it yet.
 */
import { join } from "node:path";
// Relative imports, not the @ alias: next.config imports the managers reader, which imports this module.
import { rankingsSchema } from "@cpc/rankings/schema/rankings";
import type { Rankings } from "@cpc/rankings/schema/rankings-types";
import { readPublished } from "./published-file";
import { listWeeks, loadWeek } from "./week-data";
import type { AvatarMap } from "@cpc/week/schema/week-types";

/* The rankings file layout version this site reads. It counts apart from the page JSON version. */
const SCHEMA_VERSION = 1;

/* The latest season is the highest season folder with a week page. */
export function latestSeason(): string | null {
  const seasons = listWeeks().map((ref) => ref.season);
  return seasons.length === 0 ? null : seasons.sort().at(-1)!;
}

/* A schema change must fail the build loud, the same rule as the week reader. A missing file is not an error:
   the site ships before the pipeline writes the file, so the route shows an empty state. */
export function loadRankings(): Rankings | null {
  const season = latestSeason();
  if (season === null) return null;
  return readPublished(join(process.cwd(), "public", season, "rankings.json"), SCHEMA_VERSION, rankingsSchema);
}

/* The avatars of the latest published week in a season, so the rankings rows show the same images as the week page.
   The week JSON paths are relative to the week folder, so each path gets the folder in front. */
export function latestAvatars(season: number): AvatarMap {
  const ref = listWeeks()
    .filter((week) => week.season === String(season))
    .at(-1);
  if (!ref) return {};
  const folder = `/${ref.season}/${ref.week}`;
  const avatars = loadWeek(ref.season, ref.week).avatars;
  return Object.fromEntries(Object.entries(avatars).map(([id, path]) => [id, `${folder}/${path}`]));
}
