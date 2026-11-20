/**
 * Tests for the module reset helper of `bun test`. A module that reads the env when it loads gets the new value after a reset.
 * A test file that loads the same module with no reset keeps the first value.
 */
import { describe, expect, it } from "bun:test";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { resetModules } from "./reset-modules";

// A module that reads the env once, when it loads, as the data readers read the working folder.
const folder = mkdtempSync(join(tmpdir(), "reset-modules-"));
const reader = join(folder, "reader.ts");
writeFileSync(reader, 'export const seen = process.env.RESET_MODULES_VALUE ?? "unset";\n');

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
