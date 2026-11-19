/**
 * Reads the sim files from public/ at build time: the season file of the midseason replay, and the newest week file of
 * the sim page, week-NN/sim.json, with a page block for each team.
 */
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { simSchema, weekSimSchema } from "@cpc/sim/schema/sim";
import type { Sim, WeekSim } from "@cpc/sim/schema/sim-types";
import { readPublished } from "./published-file";

/* The sim file layout version this site reads. It counts apart from the other published files. */
const SCHEMA_VERSION = 1;
const FILE = "sim.json";
const SEASON = /^\d{4}$/;
const WEEK = /^week-\d{2}$/;

const publicDir = () => join(process.cwd(), "public");

/* A schema change must fail the build loud, the same rule as the week reader. A season with no file gives null. */
export function loadSim(season: string): Sim | null {
  return readPublished(join(publicDir(), season, FILE), SCHEMA_VERSION, simSchema);
}

/* The week folders of a season that hold a week sim file, oldest first. The names sort as numbers, week-09 before week-10. */
function simWeeks(season: string): string[] {
  const dir = join(publicDir(), season);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((name) => WEEK.test(name) && existsSync(join(dir, name, FILE)))
    .sort();
}

/* Each season folder of public/ with at least one week sim file, oldest first. The sim page builds one route for each. */
export function weekSimSeasons(): string[] {
  if (!existsSync(publicDir())) return [];
  return readdirSync(publicDir())
    .filter((name) => SEASON.test(name) && simWeeks(name).length > 0)
    .sort();
}

/* The week sim file of the newest week of the season, which the sim page reads. A season with none gives null. */
export function latestWeekSim(season: string): WeekSim | null {
  const week = simWeeks(season).at(-1);
  return week === undefined ? null : readPublished(join(publicDir(), season, week, FILE), SCHEMA_VERSION, weekSimSchema);
}
