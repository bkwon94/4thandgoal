/**
 * The Zod schema of the answer of the What-if route, POST /clients/<slug>/sim/what-if, and of its set results.
 * The route in apps/api/src/cornerstone_api/what_if.py owns the shape, and this schema follows it (ADR 0013).
 */
import { z } from "zod";
import { simPageSchema, simRunSchema, teamSimSchema } from "./sim";

/* JSON keeps each roster ID key as a string, so a record of roster IDs reads its keys back as numbers. */
const rosterKey = z.coerce.number();

/* One result of Your team in one week left. A week of a league with a median game sets the median too. */
export const setResultSchema = z.object({
  week: z.number().int(),
  game: z.enum(["win", "loss"]),
  median: z.enum(["above", "below"]).nullable(),
});

/* The answer of one What-if: the sim again with the set results held, and the page block of Your team. */
export const whatIfAnswerSchema = z.object({
  schema_version: z.number(),
  season: z.number(),
  week: z.number(),
  runs: z.number(),
  effective_runs: z.number(),
  you: z.number(),
  set: z.array(setResultSchema),
  teams: z.record(rosterKey, teamSimSchema),
  sample: z.array(simRunSchema),
  // The weight of each stored run, in the order of `sample`. The replay picks a run in proportion to its weight.
  sample_weights: z.array(z.number()),
  page: simPageSchema,
});
