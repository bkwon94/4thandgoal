/**
 * Parses every published JSON file under public/ with its Zod schema.
 * A shape change from the pipeline fails here, and the message names the file and the bad field.
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import type { ZodType } from "zod";
import { managersFileSchema } from "../schemas/managers";
import { rankingsSchema } from "../schemas/rankings";
import { waiverBoardSchema } from "../schemas/waiver";
import { weekPageSchema } from "../schemas/week";

const PUBLIC_DIR = join(process.cwd(), "public");

/* Every file with this name under public/, as a path relative to the repo root. */
function filesNamed(name: string, dir = PUBLIC_DIR): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return filesNamed(name, path);
    return entry.name === name ? [path] : [];
  });
}

/* The failure message holds the file and the path of each bad field, so a reader goes straight to the key. */
function parseFile(schema: ZodType, file: string) {
  const result = schema.safeParse(JSON.parse(readFileSync(file, "utf8")));
  if (result.success) return;
  const issues = result.error.issues.map((issue) => `  ${issue.path.join(".") || "(root)"}: ${issue.message}`);
  throw new Error(`${file} does not match its schema:\n${issues.join("\n")}`);
}

/* A count of zero would pass with no file read, so the three files that always exist must be found. */
describe.each([
  ["page.json", weekPageSchema, 1],
  // No waiver.json is published yet. The waiver page tests cover the waiver schema through the component fixture.
  ["waiver.json", waiverBoardSchema, 0],
  ["rankings.json", rankingsSchema, 1],
  ["managers.json", managersFileSchema, 1],
])("%s under public/", (name, schema, least) => {
  it("parses with its schema", () => {
    const files = filesNamed(name);
    expect(files.length).toBeGreaterThanOrEqual(least);
    for (const file of files) expect(() => parseFile(schema, file)).not.toThrow();
  });
});
