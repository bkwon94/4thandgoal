/**
 * The three API response documents as typed fixtures for the analyzer tests.
 * Each one is in the exact shape the site API returns, so a change to that shape breaks the tests.
 */
import analyzeJson from "./analyze-response.json";
import analyzeThreeJson from "./analyze-response-three.json";
import findJson from "./find-response.json";
import { analyzeResponseSchema, findResponseSchema } from "@/lib/schemas/api";

/* The parse runs at import, so a stale fixture fails at once. */
export const analyzeResponse = analyzeResponseSchema.parse(analyzeJson);
export const analyzeResponseThree = analyzeResponseSchema.parse(analyzeThreeJson);
export const findResponse = findResponseSchema.parse(findJson);
