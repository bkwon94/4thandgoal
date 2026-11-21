/**
 * The paths of the fixed site data of the tests: a copy of the published JSON files of CPC and NorCal, to week 8.
 * A test reads this copy in place of public/ or clients/<slug>/published/, so a weekly publish never changes what a test sees.
 */
import { join } from "node:path";
import { spyOn } from "bun:test";

/* The clients that the copy holds. */
export type FixtureClient = "cpc" | "norcal";

/* The path comes from this module and not from the working folder, because many tests mock process.cwd. */
const SITES = join(__dirname, "sites");

/* The fixed site folder of one client. It holds public/ as the client build leaves it, with the JSON files only. */
export function fixtureSite(slug: FixtureClient): string {
  return join(SITES, slug);
}

/* A path in the fixed copy of the published folder of one client. The layout is the layout of clients/<slug>/published/. */
export function fixturePublished(slug: FixtureClient, ...path: string[]): string {
  return join(SITES, slug, "public", ...path);
}

/* Points the working folder at the fixed site folder of one client, so each reader of public/ reads the fixed copy.
   It is a spy, so the preload puts the real working folder back after each test. A test file calls it in `beforeEach`. */
export function readFixtureSite(slug: FixtureClient = "cpc"): void {
  spyOn(process, "cwd").mockReturnValue(fixtureSite(slug));
}
