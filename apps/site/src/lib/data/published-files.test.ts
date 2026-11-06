/**
 * Parses every published JSON file under public/ with its Zod schema.
 * A shape change from the pipeline fails here, and the message names the file and the bad field.
 */
import { mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";
import type { ZodType } from "zod";
import { type Offense, report } from "../../rule-report";
import { managersFileSchema } from "@cpc/managers/schema/managers";
import { midseasonSchema } from "@cpc/midseason/schema/midseason";
import { rankingsSchema } from "@cpc/rankings/schema/rankings";
import { simSchema } from "@cpc/sim/schema/sim";
import { waiverBoardSchema } from "@cpc/waiver/schema";
import { weekPageSchema } from "@cpc/week/schema/week";

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
function shapeOffenses(schema: ZodType, file: string): Offense[] {
  const result = schema.safeParse(JSON.parse(readFileSync(file, "utf8")));
  if (result.success) return [];
  return result.error.issues.map((issue) => ({
    path: relative(process.cwd(), file),
    line: issue.path.join(".") || "(root)",
    ruleId: "published/shape",
    what: issue.message,
    rule: "the pipeline owns the published shape, and each file under public/ matches its Zod schema",
    adr: "docs/adr/0013-the-published-shape-has-one-owner.md",
    fix: "change the schema in packages/<package>/site/schema/ and the pipeline's writer together, or republish the file.",
  }));
}

/* A count of zero would pass with no file read, so the three files that always exist must be found. */
describe.each([
  ["page.json", weekPageSchema, 1],
  // No waiver.json is published yet. The waiver page tests cover the waiver schema through the component fixture.
  ["waiver.json", waiverBoardSchema, 0],
  ["rankings.json", rankingsSchema, 1],
  ["managers.json", managersFileSchema, 1],
  // No midseason.json is published yet. The midseason tests cover its schema through the package fixture.
  ["midseason.json", midseasonSchema, 0],
  // No sim.json is published yet. The sim tests cover its schema through the package fixture.
  ["sim.json", simSchema, 0],
])("%s under public/", (name, schema, least) => {
  it("parses with its schema", () => {
    const files = filesNamed(name);
    expect(files.length).toBeGreaterThanOrEqual(least);
    const found = files.flatMap((file) => shapeOffenses(schema, file));
    if (found.length > 0) throw new Error(report(found));
  });
});

describe("the published shape rule", () => {
  it("finds one offense in a page.json on disk with one bad field", () => {
    // A real page with one field of the wrong type, so the schema reports that field and no other.
    const page = JSON.parse(readFileSync(filesNamed("page.json")[0], "utf8"));
    const dir = mkdtempSync(join(tmpdir(), "published-shape-"));
    try {
      const file = join(dir, "page.json");
      writeFileSync(file, JSON.stringify({ ...page, season: "2026" }));
      const found = shapeOffenses(weekPageSchema, file);
      expect(found.map(({ ruleId }) => ruleId)).toEqual(["published/shape"]);
      expect(`${found[0].path}:${found[0].line}`).toMatch(/page\.json:season$/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
