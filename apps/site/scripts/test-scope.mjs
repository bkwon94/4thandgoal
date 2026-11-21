/**
 * Sets the scope of a `bun test` run: the shard of a CI job, and the full suite or only the tests that the diff can reach.
 * scripts/bun-test.mjs reads BUN_TEST_SHARD and BUN_TEST_BASE, and CI sets them in each job of the unit matrix.
 */
import { spawnSync } from "node:child_process";

/* The files that run the full suite when a diff names one, as paths from the root of the repo. `bun test --changed`
   follows the imports of each test file, so it does not see these files: they change each test file and import none.
   An entry that ends in "/" names each file under the folder. A "*" stands for one folder name. */
export const FULL_SUITE_FILES = [
  // The lock file and the workspace change the code of each dependency.
  "pnpm-lock.yaml",
  "pnpm-workspace.yaml",
  "apps/site/package.json",
  "packages/*/site/package.json",
  // The Bun version and the settings of `bun test`, with the preload that each test file loads.
  ".bun-version",
  "apps/site/bunfig.toml",
  "apps/site/test/",
  // The `@` alias and the other paths that Bun resolves.
  "apps/site/tsconfig.json",
  // The Oxlint config and the design rules. The rule tests run Oxlint as a child process and import no rule file.
  ".oxlintrc.json",
  "packages/design/lint/",
  // The runner and the scope, so a change to how CI picks the tests gets a full run.
  "apps/site/scripts/bun-test.mjs",
  "apps/site/scripts/test-scope.mjs",
  ".github/workflows/check.yml",
];

/* A regular expression for one entry of FULL_SUITE_FILES. */
function patternOf(entry) {
  const escaped = entry.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, "[^/]+");
  return new RegExp(entry.endsWith("/") ? `^${escaped}` : `^${escaped}$`);
}

const FULL_SUITE_PATTERNS = FULL_SUITE_FILES.map(patternOf);

/* True when one of the changed files, as paths from the root of the repo, is in FULL_SUITE_FILES. */
export function needsFullSuite(changedFiles) {
  return changedFiles.some((file) => FULL_SUITE_PATTERNS.some((pattern) => pattern.test(file)));
}

/* The measured time of each test file, as a path from apps/site. `bun test --shard` splits the files by count with no
   timings, and one page test takes about 30 s, so a split by count gave 3 shards a slower shard than 2. A file that the
   timings do not name still runs. Refresh it with pnpm test:bun --timings=bun-test-timings.json --update-timings. */
export const TIMINGS_FILE = "bun-test-timings.json";

/* The `bun test` flags of the shard that BUN_TEST_SHARD names, such as "2/4", split by TIMINGS_FILE, or no flag when it
   is not set. A value that names no shard stops the run, because a bad value would make each job of the matrix run every
   file. */
export function shardArg(value) {
  if (value === undefined || value === "") return [];
  const match = /^(\d+)\/(\d+)$/.exec(value);
  const current = match ? Number(match[1]) : 0;
  const total = match ? Number(match[2]) : 0;
  if (current < 1 || current > total) {
    throw new Error(
      `BUN_TEST_SHARD must be <current>/<total>, with 1 <= current <= total, not "${value}".`,
    );
  }
  return [`--shard=${current}/${total}`, `--timings=${TIMINGS_FILE}`];
}

/* The `bun test` flag of the scope. With no base, as on a push, it is the full suite. With a base, as on a PR, it is
   `--changed=<base>`, unless the diff names a file of FULL_SUITE_FILES. `changedFiles` is null when git cannot list the
   diff, and then the run takes the full suite, so a missing base never skips a test. */
export function scopeArgs({ base, changedFiles }) {
  if (base === undefined || base === "") return [];
  if (changedFiles === null || needsFullSuite(changedFiles)) return [];
  return [`--changed=${base}`];
}

/* The files that differ between `base` and the work tree, as paths from the root of the repo, as `bun test --changed`
   compares them. On a PR, CI checks out the test merge commit, so the work tree is the merge result. It is null when git
   cannot list the diff, such as for a base that the checkout does not hold. */
export function changedFilesSince(base) {
  const diff = spawnSync("git", ["diff", "--name-only", "--no-renames", base, "--"], {
    cwd: import.meta.dirname,
    encoding: "utf8",
  });
  if (diff.status !== 0) return null;
  return diff.stdout.split("\n").filter((line) => line !== "");
}
