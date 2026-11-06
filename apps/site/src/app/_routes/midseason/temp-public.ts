/**
 * The temp public/ folder of the tests of the midseason route and the midseason home part. Only those tests import it.
 * It writes real week pages and the given season files, points the working folder at it, and removes it after the test.
 */
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { vi } from "vitest";
import { weekPageJson } from "@/fixtures/week-page-json";

const roots: string[] = [];

/* A temp public/ folder with the week pages of 2026 from week 6 to `latest`, and the midseason file and the sim file
   when each is given. The latest week holds the given avatars. The readers read the working folder when they load, so the module cache resets, and the next
   import of a route or a part reads the temp folder. */
export function publicOver({
  latest = 8,
  report,
  sim,
  avatars = {},
}: {
  latest?: number;
  report?: unknown;
  sim?: unknown;
  avatars?: Record<string, string>;
}): void {
  const root = mkdtempSync(join(tmpdir(), "midseason-public-"));
  roots.push(root);
  for (let week = 6; week <= latest; week++) {
    const folder = join(root, "public", "2026", `week-${String(week).padStart(2, "0")}`);
    mkdirSync(folder, { recursive: true });
    writeFileSync(join(folder, "page.json"), weekPageJson({ week, avatars: week === latest ? avatars : {} }));
  }
  if (report !== undefined) writeFileSync(join(root, "public", "2026", "midseason.json"), JSON.stringify(report));
  if (sim !== undefined) writeFileSync(join(root, "public", "2026", "sim.json"), JSON.stringify(sim));
  vi.spyOn(process, "cwd").mockReturnValue(root);
  vi.resetModules();
}

/* Removes each temp folder of the test and gives the working folder back. Call it after each test. */
export function removePublics(): void {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
  vi.restoreAllMocks();
}
