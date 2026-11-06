/**
 * The evidence run of one feature: it builds the client, serves its export, and takes the shots of each step list.
 * Run it with pnpm evidence <slug> [AT-<n> ...]. The wrapper scripts/evidence.mjs passes the slug and the ids as env values.
 */
import { test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { loadTests, runRound } from "./evidence";
import { serveDir } from "./serve";

// pnpm runs each script of the site in apps/site, so the tracker sits two folders up.
const SCRATCH = join(process.cwd(), "..", "..", ".scratch");
const OUT = join(process.cwd(), "out");
const SLUG = process.env.EVIDENCE_SLUG ?? "";
const IDS = (process.env.EVIDENCE_TESTS ?? "").split(/\s+/).filter(Boolean);

// Check every step list when the file loads, so a bad list stops the run before the build and before any shot.
if (SLUG) loadTests(SCRATCH, SLUG, IDS);

test(`the evidence of ${SLUG || "no feature"}`, async ({ browser }) => {
  test.skip(!SLUG, "Run it with pnpm evidence <slug>.");
  // A round takes minutes, and each test logs its own time, so the run has no time limit.
  test.setTimeout(0);
  await runRound({
    scratch: SCRATCH,
    slug: SLUG,
    ids: IDS,
    browser,
    serve: async (client) => {
      const start = Date.now();
      // pnpm build runs the prebuild step too, which copies the published weeks of the client into public/.
      execFileSync("pnpm", ["build"], { env: { ...process.env, CLIENT: client }, stdio: "ignore" });
      console.log(`build ${client}: ${((Date.now() - start) / 1000).toFixed(1)} s`);
      return serveDir(OUT);
    },
    log: (line) => console.log(line),
  });
});
