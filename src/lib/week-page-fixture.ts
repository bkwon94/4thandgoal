/**
 * Builds a week page JSON string for tests that write a temp public/ folder.
 * It reads the live week 6 page on purpose, so the tests follow the real shape. A reshape of that file changes ten tests.
 * The base is the real week 6 page, so the loader's schema accepts it, and each test overrides only the keys it reads.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";

/* The path is fixed when the module loads, because tests mock process.cwd to point at the temp folder after the import. */
const WEEK_6 = join(process.cwd(), "public", "2026", "week-06", "page.json");

export function weekPageJson(overrides: Record<string, unknown> = {}): string {
  return JSON.stringify({ ...JSON.parse(readFileSync(WEEK_6, "utf8")), ...overrides });
}
