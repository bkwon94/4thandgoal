/**
 * Runs the real Oxlint config of the repo root on the fixtures of the value rule, one fixture per case.
 * Each case checks the exit code of the lint and the rule name and the line in its output (ADR 0038).
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/* pnpm runs the site tests from apps/site, and Oxlint takes no path with "..", so the lint runs from the repo root. */
const ROOT_DIR = join(process.cwd(), "..", "..");
const OXLINT = join(process.cwd(), "node_modules", ".bin", "oxlint");
const RULE = "design(no-arbitrary-value)";

function lint(fixture: string): { status: number | null; output: string } {
  const run = spawnSync(OXLINT, [`packages/design/lint/fixtures/no-arbitrary-value/${fixture}`], {
    cwd: ROOT_DIR,
    encoding: "utf8",
  });
  return { status: run.status, output: run.stdout + run.stderr };
}

describe("the value rule", () => {
  it("fails an arbitrary color value in a className, at the line of the class", () => {
    const { status, output } = lint("color.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain(RULE);
    expect(output).toContain("color.tsx:6:");
    // The message names the fix, so an agent needs no search.
    expect(output).toContain("Use a role token or a scale step");
  });

  it("fails an arbitrary spacing value in a cn(...) call, at the line of the class", () => {
    const { status, output } = lint("spacing.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain(RULE);
    expect(output).toContain("spacing.tsx:9:");
  });

  it("fails an arbitrary value after a variant on the second line of a template literal", () => {
    const { status, output } = lint("template.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain(RULE);
    expect(output).toContain("template.tsx:7:");
  });

  it("passes a variant, a layout value, and a motion value", () => {
    const { status, output } = lint("allowed.tsx");
    expect(output).not.toContain(RULE);
    expect(status).toBe(0);
  });

  it("passes a spacing value with a one-line ignore and a reason", () => {
    const { status, output } = lint("ignored.tsx");
    expect(output).not.toContain(RULE);
    expect(status).toBe(0);
  });
});
