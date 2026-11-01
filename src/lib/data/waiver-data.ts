/**
 * Reads the waiver.json file of each week folder in public/ at build time.
 * The file is optional: the site ships before the pipeline writes it, and old weeks never have one.
 */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
// Relative imports, not the @ alias: next.config imports this module, and its loader does not resolve the alias.
import { waiverOn } from "../config";
import { waiverHref } from "../routes";
import { listWeeks, type WeekRef } from "./week-data";
import { waiverBoardSchema } from "../schemas/waiver";
import type { WaiverBoard } from "../waiver-types";

/* The waiver file layout version this site reads. It counts apart from the page JSON version. */
const SCHEMA_VERSION = 1;

function waiverFile(season: string, week: string): string {
  return join(process.cwd(), "public", season, week, "waiver.json");
}

/* Every week page that also holds a waiver file, oldest first, as listWeeks sorts them. */
export function listWaiverWeeks(): WeekRef[] {
  return listWeeks().filter(({ season, week }) => existsSync(waiverFile(season, week)));
}

/* A schema change must fail the build loud, the same rule as the week reader. A missing file is not an error. */
export function loadWaiver(season: string, week: string): WaiverBoard | null {
  const file = waiverFile(season, week);
  if (!existsSync(file)) return null;
  const board = JSON.parse(readFileSync(file, "utf8")) as { schema_version?: unknown };
  if (board.schema_version !== SCHEMA_VERSION) {
    throw new Error(
      `${file} has schema_version ${String(board.schema_version)}, but this site reads schema_version ${SCHEMA_VERSION}.`,
    );
  }
  return waiverBoardSchema.parse(board);
}

/* The masthead link to the waiver page of the latest week with a file. A build with the flag off has no route, so no link.
   The link is a plain anchor, so the route builder puts the base path in it. */
export function currentWaiverHref(): string | null {
  if (!waiverOn) return null;
  const latest = listWaiverWeeks().at(-1);
  return latest ? waiverHref(latest.season, latest.week) : null;
}

/* Whether the build has a waiver route. A static export fails on a dynamic route with no params,
   so the route file only counts as a page when the flag is on and at least one week has a file. */
export function waiverRouteOn(): boolean {
  return waiverOn && listWaiverWeeks().length > 0;
}
