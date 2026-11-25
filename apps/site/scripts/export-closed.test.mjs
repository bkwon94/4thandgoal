/**
 * Tests that check-export reads the Trades closed value of the build, never the real clock.
 * A build before the Lock expects the analyzer, and a build after the Lock expects the closed page.
 */
import { describe, expect, it } from "bun:test";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { tradesClosedOfBuild } from "./export-closed.mjs";

const valuesText = (closed) =>
  `export const clientValues: ClientValues = ${JSON.stringify({ slug: "cpc", lock: 1, tradesClosed: closed }, null, 2)};`;

describe("the Trades closed value of a build", () => {
  it("is false for a build before the Lock, so the export holds the analyzer", () => {
    expect(tradesClosedOfBuild(valuesText(false))).toBe(false);
  });

  it("is true for a build after the Lock, so the export holds the closed page", () => {
    expect(tradesClosedOfBuild(valuesText(true))).toBe(true);
  });

  it("throws when the generated text has no value", () => {
    expect(() => tradesClosedOfBuild("export const clientValues = {};")).toThrow();
  });

  it("reads the generated file as the build writes it", () => {
    const dir = mkdtempSync(join(tmpdir(), "export-closed-"));
    try {
      const file = join(dir, "client-values.ts");
      writeFileSync(file, valuesText(true));
      expect(tradesClosedOfBuild(readFileSync(file, "utf8"))).toBe(true);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
