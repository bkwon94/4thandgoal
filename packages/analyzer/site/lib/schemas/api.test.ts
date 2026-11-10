/**
 * Parses the two API fixtures with the response schemas.
 * A fixture that drifts from its schema fails here, and the message names the bad field.
 */
import { describe, expect, it } from "vitest";
import analyzeJson from "../fixtures/analyze-response.json";
import findJson from "../fixtures/find-response.json";
import { analyzeResponseSchema, findResponseSchema, teamsResponseSchema } from "./api";

// The raw JSON of each fixture, before a parse. A copy per call, so a test that changes a body leaves the next test as it was.
const FIXTURES: Record<string, unknown> = { "analyze-response.json": analyzeJson, "find-response.json": findJson };

function fixture(name: string): unknown {
  return structuredClone(FIXTURES[name]);
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
    const body = fixture("analyze-response.json") as { fairness: Record<string, unknown> };
    body.fairness = { sides: [], state: "lopsided", gives_more: null };
    expect(analyzeResponseSchema.safeParse(body).success).toBe(false);
  });

  it("rejects a finder Bullet with no fact text", () => {
    const body = fixture("find-response.json") as { trades: { bullets: Record<string, unknown>[] }[] };
    delete body.trades[0].bullets[0].fact_text;
    expect(findResponseSchema.safeParse(body).success).toBe(false);
  });

  it("accepts the nulls the API sends in as_of", () => {
    const body = fixture("analyze-response.json") as { as_of: Record<string, unknown> };
    body.as_of = { ...body.as_of, chart_week: null, rosters_fetched: null, no_chart: false, no_chart_note: null };
    expect(analyzeResponseSchema.safeParse(body).success).toBe(true);
  });
});
