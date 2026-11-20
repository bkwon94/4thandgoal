/**
 * Runs the real Oxlint config of the repo root on the fixtures of the raw color rule.
 * Each case checks the exit code, the rule name, and the line in the output (ADR 0038).
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { describe, expect, it } from "bun:test";

/* pnpm runs the site tests from apps/site, and Oxlint takes no path with "..", so the lint runs from the repo root. */
const ROOT_DIR = join(process.cwd(), "..", "..");
const OXLINT = join(process.cwd(), "node_modules", ".bin", "oxlint");

function lint(fixture: string): { status: number | null; output: string } {
  const run = spawnSync(OXLINT, [`packages/design/lint/fixtures/raw-color/${fixture}`], {
    cwd: ROOT_DIR,
    encoding: "utf8",
  });
  return { status: run.status, output: run.stdout + run.stderr };
}

describe("the raw color rule", () => {
  it("fails a hex color in a style object and an rgb() color in a class string, and an oklch() color in a template, once for each line", () => {
    const { status, output } = lint("colored.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain("colored.tsx:6:");
    expect(output).toContain("colored.tsx:7:");
    expect(output).toContain("colored.tsx:8:");
    expect(output.match(/design\(no-raw-color\)/g)).toHaveLength(3);
  });

  it("passes a file with no color literal", () => {
    const { status, output } = lint("clean.tsx");
    expect(output).not.toContain("no-raw-color");
    expect(status).toBe(0);
  });
});
