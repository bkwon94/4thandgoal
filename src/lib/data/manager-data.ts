/**
 * Reads the season managers file from public/ at build time and joins it with the last week of the rankings file.
 * The file sits beside the rankings file, so a missing file means the pipeline has not written it yet.
 */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
// Relative imports, not the @ alias: next.config imports this module, and its loader does not resolve the alias.
import { managersHref } from "../routes";
import { managersFileSchema } from "../schemas/managers";
import type { Manager, ManagerEntry, Managers } from "../manager-types";
import { latestSeason, loadRankings } from "./rankings-data";
import type { RankingsRow } from "../rankings-types";

/* The managers file layout version this site reads. It counts apart from the page JSON version. */
const SCHEMA_VERSION = 1;

/* The managers file of the latest season, or null when no season has a week page. */
function managersFile(): string | null {
  const season = latestSeason();
  return season === null ? null : join(process.cwd(), "public", season, "managers.json");
}

/* The standings order with no rankings file: more wins first, then more points. */
function byRecord(a: ManagerEntry, b: ManagerEntry): number {
  return b.wins - a.wins || b.points_for - a.points_for;
}

/* A schema change must fail the build loud, the same rule as the week reader. A missing file is not an error:
   the site ships before the pipeline writes the file, so the routes do not build and the menu has no entry. */
export function loadManagers(): Managers | null {
  const file = managersFile();
  if (file === null || !existsSync(file)) return null;
  const data = JSON.parse(readFileSync(file, "utf8")) as { schema_version?: unknown };
  if (data.schema_version !== SCHEMA_VERSION) {
    throw new Error(
      `${file} has schema_version ${String(data.schema_version)}, but this site reads schema_version ${SCHEMA_VERSION}.`,
    );
  }
  const { season, through, managers } = managersFileSchema.parse(data);
  // One number has one source, so the odds and the power rank come from the last week of the rankings file.
  const weeks = loadRankings()?.weeks ?? [];
  const rowsOf = (index: number) => new Map((weeks.at(index)?.rows ?? []).map((row) => [row.roster_id, row]));
  const last = rowsOf(-1);
  const before = weeks.length > 1 ? rowsOf(-2) : new Map<number, RankingsRow>();
  const fallback = [...managers].sort(byRecord).map((entry) => entry.roster_id);
  const joined: Manager[] = managers.map((entry) => {
    const row = last.get(entry.roster_id);
    const prior = before.get(entry.roster_id)?.odds;
    const odds = row?.odds ?? null;
    return {
      ...entry,
      standing: row ? row.components.standing : fallback.indexOf(entry.roster_id) + 1,
      rank: row?.rank ?? null,
      movement: row?.movement ?? null,
      odds,
      odds_change: odds && prior ? odds.playoff - prior.playoff : null,
    };
  });
  return { season, through, managers: joined.sort((a, b) => a.standing - b.standing) };
}

/* The masthead link to the managers index of the latest season. A season with no file has no route, so no link.
   The link is a plain anchor, so the route builder puts the base path in it. */
export function currentManagersHref(): string | null {
  const file = managersFile();
  const season = latestSeason();
  return file !== null && season !== null && existsSync(file) ? managersHref(season) : null;
}

/* The managers index of the season a page shows, for the links from its team names.
   Only the latest season builds the managers routes, so a page of an older season gets null and plain names. */
export function seasonManagersHref(season: string): string | null {
  return season === latestSeason() ? currentManagersHref() : null;
}

/* Whether the build has the managers routes. A static export fails on a dynamic route with no params,
   so the route files only count as pages when the latest season has a managers file. */
export function managersRouteOn(): boolean {
  return currentManagersHref() !== null;
}
