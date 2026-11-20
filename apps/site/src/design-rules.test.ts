/**
 * Runs the real Oxlint config of the repo root on the fixture files of packages/design/lint/fixtures/, one fixture per case.
 * Each case checks the exit code of the lint and the rule name and the line in its output (ADR 0035, ADR 0038).
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { describe, expect, it } from "bun:test";

/* pnpm runs the site tests from apps/site, and Oxlint takes no path with "..", so the lint runs from the repo root. */
const ROOT_DIR = join(process.cwd(), "..", "..");
const OXLINT = join(process.cwd(), "node_modules", ".bin", "oxlint");

function lint(fixture: string): { status: number | null; output: string } {
  const run = spawnSync(OXLINT, [`packages/design/lint/fixtures/${fixture}`], {
    cwd: ROOT_DIR,
    encoding: "utf8",
  });
  return { status: run.status, output: run.stdout + run.stderr };
}

describe("the @ui-sdk import rule", () => {
  it("fails a file outside the ui folder that imports @ui-sdk/react, at the line of the import", () => {
    const { status, output } = lint("outside/top-band.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain("top-band.tsx:5:");
    expect(output).toContain("no-restricted-imports");
    // The message names the fix, so an agent needs no search.
    expect(output).toContain("Import the wrapper in the ui folder of the design package.");
  });

  it("passes a file in the fixture copy of the ui folder that imports @ui-sdk/react", () => {
    const { status, output } = lint("ui/sheet.tsx");
    expect(output).not.toContain("no-restricted-imports");
    expect(status).toBe(0);
  });
});
