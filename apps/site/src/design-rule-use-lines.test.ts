/**
 * Runs the real Oxlint config of the repo root on the fixture files of the doc rule, one fixture per case.
 * Each case checks the exit code of the lint and the rule name, the file, and the missing line in its output (ADR 0038).
 */
import { describe, expect, it } from "bun:test";
import { lintFixture } from "./design-rule-lint";

const lint = (fixture: string) => lintFixture(`use-lines/${fixture}`);

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

  it("skips a parts file that exports no component", () => {
    const { status, output } = lint("parts/no-component.tsx");
    expect(output).not.toContain("design(use-lines)");
    expect(status).toBe(0);
  });

  it("skips a test file", () => {
    const { status, output } = lint("parts/both-lines.test.tsx");
    expect(output).not.toContain("design(use-lines)");
    expect(status).toBe(0);
  });
});
