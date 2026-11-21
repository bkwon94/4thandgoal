/**
 * Runs `bun test` on each test folder of the site app and of the site side of each package, from apps/site, so Bun reads
 * the preload of bunfig.toml. Run it with pnpm test:bun [<bun test flag> ...]. It exits with the code of `bun test`.
 */
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

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

// --isolate gives each test file its own global and module registry. Without it, Framer Motion keeps the
// reduced-motion value that the first file read, and a file that sets matchMedia late sees the wrong one.
const run = spawnSync("bun", ["test", "--isolate", ...TEST_FOLDERS, ...process.argv.slice(2)], {
  cwd: SITE,
  stdio: "inherit",
});
process.exit(run.status ?? 1);
