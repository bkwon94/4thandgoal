/**
 * Reads the waiver.json file of each week folder in public/ at build time.
 * The file is optional: the site ships before the pipeline writes it, and old weeks never have one.
 */
import { existsSync } from "node:fs";
import { join } from "node:path";
import { waiverHref } from "../routes";
import { readPublished } from "./published-file";
import { listWeeks, type WeekRef } from "./week-data";
import { waiverBoardSchema } from "@cpc/waiver/schema";
import type { WaiverBoard } from "@cpc/waiver/types";

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
  return readPublished(waiverFile(season, week), SCHEMA_VERSION, waiverBoardSchema);
}

/* The masthead link to the waiver page of the latest week with a file. Only a client that takes waiver imports it.
   The link is a plain anchor, so the route builder puts the base path in it. */
export function currentWaiverHref(): string | null {
  const latest = listWaiverWeeks().at(-1);
  return latest ? waiverHref(latest.season, latest.week) : null;
}
