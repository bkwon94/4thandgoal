/**
 * Runs `bun test` on the folders of scripts/bun-test-files.mjs, from apps/site, so Bun reads the preload of bunfig.toml.
 * Run it with pnpm test:bun [<bun test flag> ...]. It exits with the code of `bun test`.
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { BUN_TEST_DIRS } from "./bun-test-files.mjs";

const SITE = join(fileURLToPath(new URL(".", import.meta.url)), "..");

// Bun reads a path that starts with "../" as a path, not as a name filter, so each folder goes from apps/site to the root.
const paths = BUN_TEST_DIRS.map((dir) => `../../${dir}`);
// --isolate gives each file a fresh global and module registry, as Vitest does. Framer Motion reads matchMedia once per
// module, so a motion-off file that runs after a motion-on file reads the wrong value without it.
const run = spawnSync("bun", ["test", "--isolate", ...paths, ...process.argv.slice(2)], {
  cwd: SITE,
  stdio: "inherit",
});
process.exit(run.status ?? 1);
