/**
 * The Zod schema of the season managers file that the Python build writes beside the rankings file.
 * The managers types are inferred from it, so the shape has one owner.
 */
import { z } from "zod";
// A relative import, not the @ alias: next.config loads the managers reader, and its loader does not resolve the alias.
import { oddsSchema } from "./rankings";

export const managerTeamSchema = z.object({ name: z.string(), owner: z.string(), avatar_url: z.string() });

/* The position is null when the players file lacks the player. */
export const managerPlayerSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string().nullable(),
});

/* A free agent pickup has no bid. */
export const moveAddSchema = managerPlayerSchema.extend({
  kind: z.enum(["waiver", "free_agent"]),
  bid: z.number().nullable(),
});

export const moveTradeSchema = z.object({
  with: z.array(z.number()),
  gave: z.array(managerPlayerSchema),
  got: z.array(managerPlayerSchema),
});

export const moveWeekSchema = z.object({
  week: z.number(),
  adds: z.array(moveAddSchema),
  drops: z.array(managerPlayerSchema),
  trades: z.array(moveTradeSchema),
});

export const movesSchema = z.object({
  adds: z.number(),
  drops: z.number(),
  trades: z.number(),
  weeks: z.array(moveWeekSchema),
});

export const bestAddSchema = managerPlayerSchema.extend({
  week: z.number(),
  points: z.number(),
  projection: z.number(),
  games: z.number(),
});

export const topPerformerSchema = managerPlayerSchema.extend({
  points: z.number(),
  games: z.number(),
  per_game: z.number(),
});

/* Won is null for a bye or a tie. */
export const seasonWeekSchema = z.object({
  week: z.number(),
  points: z.number(),
  median: z.number(),
  won: z.boolean().nullable(),
});

export const benchWorstSchema = z.object({
  week: z.number(),
  points: z.number(),
  player_id: z.string(),
  name: z.string(),
});

/* Worst is null when no week had a bench gain. */
export const benchSchema = z.object({ total: z.number(), worst: benchWorstSchema.nullable() });

export const awardCountsSchema = z.object({
  top_scorer: z.number(),
  mvb: z.number(),
  game_changer: z.number(),
  underperformer: z.number(),
});

export const slotRankSchema = z.object({
  position: z.enum(["QB", "RB", "WR", "TE"]),
  rank: z.number(),
  depth: z.enum(["stacked", "deep", "fine", "thin"]),
});

export const gradePartSchema = z.object({
  key: z.enum(["projection", "production", "trade_value", "depth"]),
  rank: z.number(),
});

export const managerGradeSchema = z.object({
  letter: z.string(),
  slots: z.array(slotRankSchema),
  parts: z.array(gradePartSchema),
  read: z.string(),
});

/* The bench is null when the build had no roster slots. The grade is null when the build had no snapshot. */
export const managerEntrySchema = z.object({
  roster_id: z.number(),
  team: managerTeamSchema,
  wins: z.number(),
  losses: z.number(),
  points_for: z.number(),
  moves: movesSchema,
  best_adds: z.array(bestAddSchema),
  top_performers: z.array(topPerformerSchema),
  weeks: z.array(seasonWeekSchema),
  bench: benchSchema.nullable(),
  awards: awardCountsSchema,
  grade: managerGradeSchema.nullable(),
});

export const managersFileSchema = z.object({
  schema_version: z.literal(1),
  season: z.number(),
  through: z.number(),
  managers: z.array(managerEntrySchema),
});

/* The joined shape that the loader builds is not a published file, so its type stays in manager-types.ts. */
