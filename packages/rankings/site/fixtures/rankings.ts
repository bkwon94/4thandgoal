/**
 * The season rankings file as a typed fixture for the rankings tests.
 * It is in the exact shape the pipeline writes, with the week 6 teams and records, so a change to that shape breaks the tests.
 */
import json from "./rankings.json";
import { rankingsSchema } from "../schema/rankings";

/* The parse runs at import, so a stale fixture fails at once. */
export const rankings = rankingsSchema.parse(json);
