/**
 * Runs the real Oxlint config of the repo root on the fixtures of the element rule design(no-raw-element).
 * Each case checks the exit code of the lint and the rule name, the line, and the wrapper in its output (ADR 0035, ADR 0038).
 */
import { describe, expect, it } from "bun:test";
import { lintFixture } from "./design-rule-lint";

const lint = (fixture: string) => lintFixture(`no-raw-element/${fixture}`);

describe("the element rule", () => {
  it("fails a raw button outside the ui folder, at its line, and names the wrapper", () => {
    const { status, output } = lint("outside/raw-button.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain("design(no-raw-element)");
    expect(output).toContain("raw-button.tsx:6:");
    // The rule cannot tell a sync action from an async one, so the message names both wrappers.
    expect(output).toContain("`Button` from packages/design/site/ui/button.tsx");
    expect(output).toContain('`variant="plain"` keeps your own classes');
    expect(output).toContain(
      "`PendingButton` from packages/design/site/ui/pending-button.tsx for an async action",
    );
  });

  it("fails a raw dialog outside the ui folder, at its line, and names the wrapper", () => {
    const { status, output } = lint("outside/raw-dialog.tsx");
    expect(status).not.toBe(0);
    expect(output).toContain("design(no-raw-element)");
    expect(output).toContain("raw-dialog.tsx:6:");
    expect(output).toContain("packages/design/site/ui/dialog.tsx");
  });

  it("passes a raw button in a test file", () => {
    const { status, output } = lint("outside/raw-button.test.tsx");
    expect(output).not.toContain("no-raw-element");
    expect(status).toBe(0);
  });

  it("passes a raw button and a raw dialog in the ui folder", () => {
    const { status, output } = lint("site/ui/plain-button.tsx");
    expect(output).not.toContain("no-raw-element");
    expect(status).toBe(0);
  });
});
