/**
 * Tests for the module reset helper of `bun test`. A module that reads the env when it loads gets the new value after a reset.
 * A test file that loads the same module with no reset keeps the first value.
 */
import { afterAll, describe, expect, it } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { resetModules } from "./reset-modules";

// A module that reads the env once, when it loads, as a module does that sets a constant from an env value at its top level.
// The module is not in the folder of `os.tmpdir()`. On the first `import` of a path, the resolver of Bun reads each folder
// above it. The macOS temp folder holds some hundred thousand entries that other tests leave, so that read takes 0.6 s
// when the folder is in the cache of the OS, and more than the 5 s limit of a test under load. The ignored folder
// test-results/ of the site is small. The file is `.js`, so the typecheck and the format check, which run at the same
// time, never read it, and oxlint ignores the folder.
const results = join(import.meta.dir, "..", "test-results");
mkdirSync(results, { recursive: true });
const folder = mkdtempSync(join(results, "reset-modules-"));
const reader = join(folder, "reader.js");
writeFileSync(reader, 'export const seen = process.env.RESET_MODULES_VALUE ?? "unset";\n');

afterAll(() => rmSync(folder, { recursive: true, force: true }));

describe("resetModules", () => {
  it("loads a module again, so it reads the env as it is now", async () => {
    process.env.RESET_MODULES_VALUE = "first";
    const first = await import(reader);
    process.env.RESET_MODULES_VALUE = "second";
    expect((await import(reader)).seen).toBe("first");

    resetModules();
    const second = await import(reader);
    delete process.env.RESET_MODULES_VALUE;

    expect(first.seen).toBe("first");
    expect(second.seen).toBe("second");
  });
});
