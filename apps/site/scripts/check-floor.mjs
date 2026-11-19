/**
 * Runs the readability floor in two passes: the parallel pass of the project "floor", then the project "floor-timing" with one worker.
 * Extra arguments, such as -g midseason, go to both passes.
 */
import { spawnSync } from "node:child_process";

const args = process.argv.slice(2);

// A filter such as -g midseason can leave no test in the timing pass, so that pass allows an empty run.
const PASSES = [
  ["--project=floor"],
  ["--project=floor-timing", "--workers=1", "--pass-with-no-tests"],
];

for (const pass of PASSES) {
  const run = spawnSync("pnpm", ["exec", "playwright", "test", ...pass, ...args], { stdio: "inherit" });
  if (run.status !== 0) process.exit(run.status ?? 1);
}
