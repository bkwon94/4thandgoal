/**
 * Runs the real Oxlint config of the repo root on the fixture files of the doc rule, one fixture per case.
 * Each case checks the exit code of the lint and the rule name, the file, and the missing line in its output (ADR 0038).
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/* The lint runs from the repo root, because Oxlint takes no path with "..". */
const ROOT_DIR = join(process.cwd(), "..", "..");
const OXLINT = join(process.cwd(), "node_modules", ".bin", "oxlint");

function lint(fixture: string): { status: number | null; output: string } {
  const run = spawnSync(OXLINT, [`packages/design/lint/fixtures/use-lines/${fixture}`], {
    cwd: ROOT_DIR,
    encoding: "utf8",
  });
  return { status: run.status, output: run.stdout + run.stderr };
}

describe("the use lines rule", () => {
  it("fails a part with no `Use it when:` line, and names the rule, the file, and the line", () => {
    const { status, output } = lint("parts/no-use-line.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain("design(use-lines)");
    expect(output).toContain("no-use-line.tsx");
    expect(output).toContain("Use it when:");
  });

  it("fails a part with no `Do not use it when:` line", () => {
    const { status, output } = lint("parts/no-avoid-line.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain("design(use-lines)");
    expect(output).toContain("Do not use it when:");
  });

  it("passes a ui file with both lines", () => {
    const { status, output } = lint("ui/both-lines.tsx");
    expect(output).not.toContain("design(use-lines)");
    expect(status).toBe(0);
  });

  it("skips a test file", () => {
    const { status, output } = lint("parts/both-lines.test.tsx");
    expect(output).not.toContain("design(use-lines)");
    expect(status).toBe(0);
  });
});
