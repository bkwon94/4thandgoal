/**
 * Runs the real Oxlint config of the repo root on the fixtures of the raw color rule.
 * Each case checks the exit code, the rule name, and the line in the output (ADR 0038).
 */
import { describe, expect, it } from "bun:test";
import { lintFixture } from "./design-rule-lint";

const lint = (fixture: string) => lintFixture(`raw-color/${fixture}`);

describe("the raw color rule", () => {
  it("fails a hex color in a style object and an rgb() color in a class string, and an oklch() color in a template, once for each line", () => {
    const { status, output } = lint("colored.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain("colored.tsx:6:");
    expect(output).toContain("colored.tsx:7:");
    expect(output).toContain("colored.tsx:8:");
    expect(output.match(/design\(no-raw-color\)/g)).toHaveLength(3);
    // The message names the file of the role tokens, so an agent needs no search.
    expect(output).toContain("Use a role token of apps/site/src/app/globals.css");
  });

  it("passes a file with no color literal", () => {
    const { status, output } = lint("clean.tsx");
    expect(output).not.toContain("no-raw-color");
    expect(status).toBe(0);
  });
});
