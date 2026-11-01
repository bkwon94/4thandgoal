/**
 * The Zod schema of the season rankings file that the Python build writes beside the week folders.
 * The rankings types are inferred from it, so the shape has one owner.
 */
import { z } from "zod";

/* One sentence of a blurb, with the IDs of the facts it rests on. */
export const blurbSentenceSchema = z.object({ text: z.string(), fact_ids: z.array(z.string()) });

/* Each component is a rank of 1 to 12, not a score, so the page never shows a sum or a ratio. */
export const componentsSchema = z.object({
  standing: z.number(),
  form: z.number(),
  schedule_played: z.number(),
  scoring: z.number(),
});

/* Playoff and bye are whole percents. Status is "in" when the team has clinched, "out" when it cannot make it. */
export const oddsSchema = z.object({
  playoff: z.number(),
  bye: z.number(),
  seed: z.number().nullable(),
  status: z.enum(["in", "out", "open"]),
});

/* Rows for weeks before the odds engine ran have no odds. */
export const rankingsRowSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  wins: z.number(),
  losses: z.number(),
  rank: z.number(),
  movement: z.number().nullable(),
  components: componentsSchema,
  blurb: z.array(blurbSentenceSchema),
  odds: oddsSchema.optional(),
});

export const rankingsWeekSchema = z.object({ week: z.number(), rows: z.array(rankingsRowSchema) });

export const rankingsSchema = z.object({
  schema_version: z.literal(1),
  season: z.number(),
  weeks: z.array(rankingsWeekSchema),
});
