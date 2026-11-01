/**
 * Parses the two API fixtures with the response schemas.
 * A fixture that drifts from its schema fails here, and the message names the bad field.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { analyzeResponseSchema, findResponseSchema, teamsResponseSchema } from "./api";

const FIXTURES = join(process.cwd(), "src/fixtures");

function fixture(name: string): unknown {
  return JSON.parse(readFileSync(join(FIXTURES, name), "utf8"));
}

describe("API response schemas", () => {
  it("parses the analyze fixture", () => {
    expect(analyzeResponseSchema.safeParse(fixture("analyze-response.json")).success).toBe(true);
  });

  it("parses the find fixture", () => {
    expect(findResponseSchema.safeParse(fixture("find-response.json")).success).toBe(true);
  });

  it("fills a missing team avatar with null", () => {
    const body = { teams: [{ roster_id: 1, team: "A", manager: "Ana", players: [] }] };
    expect(teamsResponseSchema.parse(body).teams[0].avatar).toBeNull();
  });

  it("rejects a lopsided fairness with no gives_more", () => {
    const body = fixture("find-response.json") as { trades: { fairness: Record<string, unknown> }[] };
    body.trades[0].fairness = { sides: [], state: "lopsided", gives_more: null };
    expect(findResponseSchema.safeParse(body).success).toBe(false);
  });
});
