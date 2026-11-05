/**
 * Builds the static export of each client folder under clients/, then checks that export and its readability floor.
 * The full check runs it. A change to a shared part then cannot break a second client unseen. It stops at the first failure.
 */
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { REPO_ROOT } from "./client-build.mjs";

const clientsDir = join(REPO_ROOT, "clients");
const slugs = readdirSync(clientsDir)
  .filter((name) => existsSync(join(clientsDir, name, "client.toml")))
  .sort();

for (const slug of slugs) {
  // The floor runs while out/ holds this client, because the next build replaces out/.
  for (const script of ["build", "check:export", "check:floor"]) {
    console.log(`==> site ${script}: ${slug}`);
    const run = spawnSync("pnpm", [script], { stdio: "inherit", env: { ...process.env, CLIENT: slug } });
    if (run.status !== 0) {
      console.error(`The site ${script} of the client ${slug} failed.`);
      process.exit(run.status ?? 1);
    }
  }
}
console.log(`Built and checked ${slugs.length} clients: ${slugs.join(", ")}.`);
