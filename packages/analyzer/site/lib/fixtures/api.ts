/**
 * The four API response documents as typed fixtures for the analyzer tests, and the API target of the tests.
 * Each one is in the exact shape the site API returns, so a change to that shape breaks the tests.
 */
import analyzeJson from "./analyze-response.json";
import analyzeThreeJson from "./analyze-response-three.json";
// The real answer of the API to grade-clarity trade A, recorded in `.scratch/grade-clarity/evidence/AT-1/`.
import analyzeTradeAJson from "./analyze-response-trade-a.json";
import findJson from "./find-response.json";
import type { ApiTarget } from "../api";
import { analyzeResponseSchema, findResponseSchema } from "../schemas/api";

/* The parse runs at import, so a stale fixture fails at once. */
export const analyzeResponse = analyzeResponseSchema.parse(analyzeJson);
export const analyzeResponseThree = analyzeResponseSchema.parse(analyzeThreeJson);
export const analyzeResponseTradeA = analyzeResponseSchema.parse(analyzeTradeAJson);
export const findResponse = findResponseSchema.parse(findJson);

/* The API of the tests. Each call of a test goes to the routes of cpc at this URL. */
export const apiTarget: ApiTarget = { url: "https://api.example.test", client: "cpc", season: 2026 };
