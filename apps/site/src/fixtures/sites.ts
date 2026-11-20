/**
 * The paths of the fixed site data of the tests: a copy of the published JSON files of CPC and NorCal, to week 8.
 * A test reads this copy in place of public/ or clients/<slug>/published/, so a weekly publish never changes what a test sees.
 */
import { join } from "node:path";

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

/* The real working folder function, kept from the first load of this module. */
const realCwd = process.cwd;

/* Points the working folder at the fixed site folder of one client, so each reader of public/ reads the fixed copy.
   It sets `process.cwd` itself and no spy of one runner, because Vitest and `bun test` both run the tests that call it.
   A test file under `bun test` calls `restoreFixtureSite` after each test. */
export function readFixtureSite(slug: FixtureClient = "cpc"): void {
  process.cwd = () => fixtureSite(slug);
}

/* Puts the real working folder function back. */
export function restoreFixtureSite(): void {
  process.cwd = realCwd;
}
