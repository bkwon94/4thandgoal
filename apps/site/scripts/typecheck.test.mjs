/**
 * Tests the type check script of the site: it runs `next typegen`, then `bun check`, and it fails on a type error.
 * The error case points the script at a scratch project, so the real code stays untouched.
 */
// @vitest-environment node
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, describe, expect, it } from "vitest";

const site = join(import.meta.dirname, "..");
const script = JSON.parse(readFileSync(join(site, "package.json"), "utf8")).scripts.typecheck;
const scratch = mkdtempSync(join(tmpdir(), "typecheck-"));

afterAll(() => rmSync(scratch, { recursive: true, force: true }));

describe("the type check script", () => {
  it("runs next typegen before bun check", () => {
    const typegen = script.indexOf("next typegen");
    const check = script.indexOf("bun check");
    expect(typegen).toBeGreaterThanOrEqual(0);
    expect(check).toBeGreaterThan(typegen);
  });

  it("calls the type checker, not a script named check", () => {
    // Without the flag, `bun check` runs the package script `check` and skips the type check.
    expect(script).toContain("bun check --no-script");
  });

  it("fails with the file and the line of a type error", () => {
    writeFileSync(join(scratch, "tsconfig.json"), JSON.stringify({ compilerOptions: { strict: true, noEmit: true, types: [] }, include: ["bad.ts"] }));
    writeFileSync(join(scratch, "bad.ts"), 'const ok = 1;\nconst name: string = 42;\nexport { ok, name };\n');
    // pnpm adds the extra argument to the end of the script, so it reaches `bun check`.
    const run = spawnSync("pnpm", ["run", "typecheck", "-p", scratch], { cwd: site, encoding: "utf8" });
    expect(run.status).not.toBe(0);
    expect(run.stdout + run.stderr).toMatch(/file="[^"]*bad\.ts" line="2"/);
  }, 120_000);
});
