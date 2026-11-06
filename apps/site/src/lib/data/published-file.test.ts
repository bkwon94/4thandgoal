/**
 * Tests of the shared read of a published file: a missing file, a file of another schema version, and a good file.
 * Each test writes a real file to a temp folder and reads it with the real schema of the sim file.
 */
// @vitest-environment node
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { simSchema } from "@cpc/sim/schema/sim";
import simFixture from "@cpc/sim/fixtures/sim.json";
import { readPublished } from "./published-file";

const roots: string[] = [];
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

function fileOf(data?: unknown): string {
  const root = mkdtempSync(join(tmpdir(), "published-file-"));
  roots.push(root);
  const file = join(root, "sim.json");
  if (data !== undefined) writeFileSync(file, JSON.stringify(data));
  return file;
}

describe("the read of a published file", () => {
  it("gives null for a missing file", () => {
    expect(readPublished(fileOf(), 1, simSchema)).toBeNull();
  });

  it("fails loud on a file of another schema version, and names the file and both versions", () => {
    const file = fileOf({ ...simFixture, schema_version: 2 });
    expect(() => readPublished(file, 1, simSchema)).toThrow(
      `${file} has schema_version 2, but this site reads schema_version 1.`,
    );
  });

  it("parses a good file with its schema", () => {
    const sim = readPublished(fileOf(simFixture), 1, simSchema);
    expect(sim?.runs).toBe(simFixture.runs);
  });
});
