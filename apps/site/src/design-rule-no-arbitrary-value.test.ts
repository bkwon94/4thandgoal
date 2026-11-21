/**
 * Runs the real Oxlint config of the repo root on the fixtures of the value rule, one fixture per case.
 * Each case checks the exit code of the lint and the rule name and the line in its output (ADR 0038).
 */
import { describe, expect, it } from "bun:test";
import { lintFixture } from "./design-rule-lint";

const RULE = "design(no-arbitrary-value)";

const lint = (fixture: string) => lintFixture(`no-arbitrary-value/${fixture}`);

describe("the value rule", () => {
  it("fails an arbitrary color value in a className, at the line of the class", () => {
    const { status, output } = lint("color.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain(RULE);
    expect(output).toContain("color.tsx:6:");
    // The message names the fix, so an agent needs no search.
    expect(output).toContain("Use a role token or a scale step");
    // Oxlint prints the rule name, so the message does not start with it again.
    expect(output).not.toContain("design/no-arbitrary-value: `");
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

  it("passes an arbitrary color value in a test file", () => {
    const { status, output } = lint("color.test.tsx");
    expect(output).not.toContain(RULE);
    expect(status).toBe(0);
  });

  it("passes an arbitrary value in a plain string outside a class string", () => {
    const { status, output } = lint("plain-string.tsx");
    expect(output).not.toContain(RULE);
    expect(status).toBe(0);
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
