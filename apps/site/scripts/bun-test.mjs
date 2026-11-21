/**
 * Runs `bun test` on each test folder of the site app and of the site side of each package, from apps/site, so Bun reads
 * the preload of bunfig.toml. Run it with pnpm test:bun [<bun test flag> ...]. It exits with the code of `bun test`.
 * BUN_TEST_WORKERS=<n> sets the count of worker processes. The default is the count of CPU cores.
 * CI sets BUN_TEST_SHARD, such as "2/4", for the shard of each job, and BUN_TEST_BASE on a PR for the tests the diff can reach.
 */
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { availableParallelism } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { changedFilesSince, scopeArgs, shardArg } from "./test-scope.mjs";

const SITE = join(fileURLToPath(new URL(".", import.meta.url)), "..");
const PACKAGES = join(SITE, "..", "..", "packages");

/* The test folders, as paths from apps/site. Bun reads a path that starts with "./" or "../" as a path, not as a name
   filter. The list names folders and not the whole app or the whole packages folder, because Bun also runs each
   `*.spec.ts` file, such as the Playwright specs of e2e/, and the lint fixtures of packages/design/lint/ hold test files
   that break the rules on purpose. */
const TEST_FOLDERS = [
  "./src",
  "./scripts",
  "./test",
  // Each package with a site side, so a new package gets its tests run with no change here.
  ...readdirSync(PACKAGES)
    .filter((name) => existsSync(join(PACKAGES, name, "site")))
    .map((name) => `../../packages/${name}/site`),
];

/* --parallel runs the files in worker processes at the same time. In one process the files run one after another, and
   the suite takes about 3 times as long. The hook sets a lower count, so two commits at the same time leave each test
   enough CPU for its 5 s timeout. */
const workers = process.env.BUN_TEST_WORKERS || String(availableParallelism());

// The scope of the run. With no BUN_TEST_BASE, or a diff that names a config file, the run takes the full suite.
const base = process.env.BUN_TEST_BASE;
const scope = scopeArgs({ base, changedFiles: base ? changedFilesSince(base) : [] });
const args = [
  "test",
  // --isolate gives each test file its own global and module registry. Without it, Framer Motion keeps the
  // reduced-motion value that the first file read, and a file that sets matchMedia late sees the wrong one.
  "--isolate",
  `--parallel=${workers}`,
  ...shardArg(process.env.BUN_TEST_SHARD),
  ...scope,
  ...TEST_FOLDERS,
  ...process.argv.slice(2),
];
// The log of a CI job shows the scope, so a reader sees if the run took the full suite or only the reachable tests.
console.log(`bun ${args.filter((arg) => !TEST_FOLDERS.includes(arg)).join(" ")}`);
console.log(
  scope.length === 0
    ? "The run takes the full suite."
    : `The run takes only the tests that the diff since ${base} can reach.`,
);
const run = spawnSync("bun", args, {
  cwd: SITE,
  stdio: "inherit",
});
process.exit(run.status ?? 1);
