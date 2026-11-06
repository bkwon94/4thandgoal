/**
 * Reads the season midseason file from public/ at build time: the midseason report of one season.
 * The file sits beside the week folders, and only a season with a published report holds it.
 */
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { midseasonSchema } from "@cpc/midseason/schema/midseason";
import type { Midseason } from "@cpc/midseason/schema/midseason-types";
import { readPublished } from "./published-file";

/* The midseason file layout version this site reads. It counts apart from the page JSON version. */
const SCHEMA_VERSION = 1;
const FILE = "midseason.json";
const SEASON = /^\d{4}$/;

/* Each season folder of public/ that holds a midseason file, oldest first. */
export function midseasonSeasons(): string[] {
  const root = join(process.cwd(), "public");
  if (!existsSync(root)) return [];
  return readdirSync(root)
    .filter((name) => SEASON.test(name) && existsSync(join(root, name, FILE)))
    .sort();
}

/* A schema change must fail the build loud, the same rule as the week reader. A season with no file gives null. */
export function loadMidseason(season: string): Midseason | null {
  return readPublished(join(process.cwd(), "public", season, FILE), SCHEMA_VERSION, midseasonSchema);
}
