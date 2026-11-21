/**
 * The shared helper of the design rule tests: it runs the real Oxlint config of the repo root on one lint fixture.
 * Each rule test imports it, so the path of Oxlint and the run of the lint sit in one place (ADR 0038).
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";

/* pnpm runs the site tests from apps/site, and Oxlint takes no path with "..", so the lint runs from the repo root. */
const ROOT_DIR = join(process.cwd(), "..", "..");
const OXLINT = join(process.cwd(), "node_modules", ".bin", "oxlint");

/* Lints one fixture, given as a path under packages/design/lint/fixtures/, and gives the exit code and the output. */
export function lintFixture(fixture: string): { status: number | null; output: string } {
  const run = spawnSync(
    OXLINT,
    ["--format", "default", `packages/design/lint/fixtures/${fixture}`],
    {
      cwd: ROOT_DIR,
      encoding: "utf8",
      // Oxlint picks its format from the env: agent vars give a plain format, CI gives color codes.
      // --format default and the strip below give one output in every env.
      // A run with GITHUB_ACTIONS set still passed with --format default, so the unset is a guard only.
      env: { ...process.env, GITHUB_ACTIONS: undefined },
    },
  );
  // Strips the ANSI color codes, which sit between the file name and the line number.
  const output = (run.stdout + run.stderr).replace(/\x1b\[[0-9;]*m/g, "");
  return { status: run.status, output };
}
