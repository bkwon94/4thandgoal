/**
 * The test of the grade weights: the site constant must equal GRADE_WEIGHTS in the tunables file of the pipeline.
 * The site holds its own copy, so the spec stays on the site only, and this test stops a silent drift (decision 09 of card-polish).
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { GRADE_WEIGHTS } from "@cpc/managers/page/grade-weights";

/* The tunables file of the pipeline. The test sits in the app layer, because a package test reads no file (ADR 0012). */
const TUNABLES = join(__dirname, "../../../packages/managers/python/src/managers/tunables.py");

/* The weights of GRADE_WEIGHTS as the Python file writes them: each `"key": number` line inside the dict. */
function pipelineWeights(): Record<string, number> {
  const source = readFileSync(TUNABLES, "utf8");
  const block = source.match(/^GRADE_WEIGHTS = \{([\s\S]*?)^\}/m);
  if (!block) throw new Error("GRADE_WEIGHTS is not in tunables.py");
  const pairs = [...block[1].matchAll(/^\s*"(\w+)":\s*(\d+),/gm)];
  return Object.fromEntries(pairs.map(([, key, value]) => [key, Number(value)]));
}

describe("GRADE_WEIGHTS", () => {
  it("equals GRADE_WEIGHTS of the pipeline", () => {
    expect(GRADE_WEIGHTS).toEqual(pipelineWeights());
  });
});
