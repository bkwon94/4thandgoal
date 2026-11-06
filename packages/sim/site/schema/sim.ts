/**
 * The Zod schema of the season sim file that the Python build writes beside the week folders.
 * The pipeline owns the shape in sim/published.py, and this schema follows it (ADRs 0011 and 0013).
 */
import { z } from "zod";

/* JSON keeps each roster ID key as a string, so a record of roster IDs reads its keys back as numbers. */
const rosterKey = z.coerce.number();

/* A head-to-head pair of roster IDs. In a bracket game the higher seed comes first. */
const pairSchema = z.tuple([z.number(), z.number()]);

/* One stored run of the sim. GLOSSARY.md, "Sim run". The replay plays it with no draw of its own. */
export const simRunSchema = z.object({
  // The score of each roster in each week of `weeks`. A bracket week of a roster with no game holds null.
  scores: z.record(rosterKey, z.array(z.number().nullable())),
  // The roster IDs in the final order of the regular season. The first `playoff_spots` are the seeds.
  table: z.array(z.number()),
  // The games of each bracket round. A bye plays no game.
  bracket: z.array(z.array(pairSchema)),
  champion: z.number(),
});

/* The odds of one team over all runs. Playoff and bye are whole percent; the rest have one decimal. */
export const teamSimSchema = z.object({
  roster_id: z.number(),
  playoff: z.number(),
  bye: z.number(),
  final: z.number(),
  title: z.number(),
  seeds: z.record(rosterKey, z.number()),
  final_wins: z.record(rosterKey, z.number()),
  mean_wins: z.number(),
});

/* The numbers of the draw. The replay reads only the playoff spots, the byes, and the median game. */
export const simParametersSchema = z.object({
  playoff_spots: z.number(),
  bye_count: z.number(),
  median_game: z.boolean(),
  reseed: z.boolean(),
});

export const simSchema = z.object({
  schema_version: z.number(),
  season: z.number(),
  week: z.number(),
  runs: z.number(),
  // The weeks that a run draws: the regular weeks left, then one week per bracket round.
  weeks: z.array(z.number()),
  bracket_weeks: z.array(z.number()),
  // The real wins, losses, and points for of each roster at the start of the sim.
  records: z.record(rosterKey, z.tuple([z.number(), z.number(), z.number()])),
  // The head-to-head pairs of each regular week left.
  schedule: z.record(rosterKey, z.array(pairSchema)),
  parameters: simParametersSchema,
  teams: z.record(rosterKey, teamSimSchema),
  sample: z.array(simRunSchema),
  names: z.record(rosterKey, z.string()),
});
