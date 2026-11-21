/**
 * Parses the API fixtures with the response schemas.
 * A fixture that drifts from its schema fails here, and the message names the bad field.
 */
import { describe, expect, it } from "bun:test";
import analyzeJson from "../fixtures/analyze-response.json";
import findJson from "../fixtures/find-response.json";
import findBoGirdsJson from "../fixtures/find-response-bo-girds-rb.json";
import { analyzeResponseSchema, findResponseSchema, teamsResponseSchema } from "./api";

// The raw JSON of each fixture, before a parse. A copy per call, so a test that changes a body leaves the next test as it was.
const FIXTURES: Record<string, unknown> = {
  "analyze-response.json": analyzeJson,
  "find-response.json": findJson,
  "find-response-bo-girds-rb.json": findBoGirdsJson,
};

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

  it("parses the near ideas of the find fixture, each with its reason", () => {
    const parsed = findResponseSchema.parse(fixture("find-response.json"));
    expect(parsed.near.length).toBeGreaterThan(0);
    expect(parsed.near[0].reason).toMatch(/\w/);
  });

  it("rejects a find document with no near key, so an Answer kept before the near ideas drops", () => {
    const body = fixture("find-response.json") as Record<string, unknown>;
    delete body.near;
    expect(findResponseSchema.safeParse(body).success).toBe(false);
  });

  it("parses the trade value totals of each trade and near idea, in side order", () => {
    const parsed = findResponseSchema.parse(fixture("find-response.json"));
    expect(parsed.trades[1].totals).toEqual([
      { roster_id: 2, trade_value: 26.5 },
      { roster_id: 10, trade_value: 17.0 },
    ]);
    expect(parsed.near[0].totals.map((total) => total.roster_id)).toEqual([2, 10]);
  });

  it("parses the recorded find answer of a real press for Bo Girds, with the totals of each pick and near idea", () => {
    const parsed = findResponseSchema.parse(fixture("find-response-bo-girds-rb.json"));
    expect(parsed.trades.length).toBeGreaterThan(0);
    for (const offer of [...parsed.trades, ...parsed.near])
      expect(offer.totals.map((t) => t.roster_id)).toEqual(offer.sides.map((s) => s.roster_id));
  });

  it("accepts a null trade value total, for a week with no chart", () => {
    const body = fixture("find-response.json") as {
      trades: { totals: { trade_value: number | null }[] }[];
    };
    body.trades[0].totals[0].trade_value = null;
    expect(findResponseSchema.safeParse(body).success).toBe(true);
  });

  it("rejects a find trade with no totals, so an Answer kept before the totals drops", () => {
    const body = fixture("find-response.json") as { trades: Record<string, unknown>[] };
    delete body.trades[0].totals;
    expect(findResponseSchema.safeParse(body).success).toBe(false);
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
    const body = fixture("find-response.json") as {
      trades: { bullets: Record<string, unknown>[] }[];
    };
    delete body.trades[0].bullets[0].fact_text;
    expect(findResponseSchema.safeParse(body).success).toBe(false);
  });

  it("accepts the nulls the API sends in as_of", () => {
    const body = fixture("analyze-response.json") as { as_of: Record<string, unknown> };
    body.as_of = {
      ...body.as_of,
      chart_week: null,
      rosters_fetched: null,
      no_chart: false,
      no_chart_note: null,
    };
    expect(analyzeResponseSchema.safeParse(body).success).toBe(true);
  });
});
