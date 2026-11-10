/**
 * Builds a week page JSON string for tests that write a temp public/ folder.
 * It reads the fixed copy of the real week 6 page on purpose, so the tests follow the real shape. A reshape of that file changes ten tests.
 * The base is the real week 6 page, so the loader's schema accepts it, and each test overrides only the keys it reads.
 */
import { readFileSync } from "node:fs";
import { fixturePublished } from "./sites";

/* The path comes from the fixture module and not from the working folder, because tests mock process.cwd to point at
   the temp folder. It reads the fixed copy of the cpc data, so a test needs no client build first. */
const WEEK_6 = fixturePublished("cpc", "2026", "week-06", "page.json");

export function weekPageJson(overrides: Record<string, unknown> = {}): string {
  return JSON.stringify({ ...JSON.parse(readFileSync(WEEK_6, "utf8")), ...overrides });
}
