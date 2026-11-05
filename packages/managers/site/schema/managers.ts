/**
 * The Zod schema of the season managers file that the Python build writes beside the rankings file.
 * The file holds one entry per roster. The odds and the power rank stay in the rankings file, and the site joins them.
 */
import { z } from "zod";

/* The team as the week page names it. The avatar URL is the Sleeper one; the pages show the week page avatars. */
// A manager with no Sleeper avatar has avatar_url null, as the pipeline model ManagerTeam allows.
export const managerTeamSchema = z.object({ name: z.string(), owner: z.string(), avatar_url: z.string().nullable() });

/* A player of a move, an add, or a performer row. The position is null when the players file lacks him. */
export const managerPlayerSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string().nullable(),
});

/* An add by a waiver claim or a free agent pickup. A free agent pickup has no bid. */
export const moveAddSchema = managerPlayerSchema.extend({
  kind: z.enum(["waiver", "free_agent"]),
  bid: z.number().nullable(),
});

/* One trade from the side of the roster: the other rosters, the players it gave, and the players it got. */
export const moveTradeSchema = z.object({
  with: z.array(z.number()),
  gave: z.array(managerPlayerSchema),
  got: z.array(managerPlayerSchema),
});

/* The moves of one week. A week with no moves holds empty lists. */
export const moveWeekSchema = z.object({
  week: z.number(),
  adds: z.array(moveAddSchema),
  drops: z.array(managerPlayerSchema),
  trades: z.array(moveTradeSchema),
});

/* The season totals and every week from the last saved week down to week 1, newest first. */
export const movesSchema = z.object({
  adds: z.number(),
  drops: z.number(),
  trades: z.number(),
  weeks: z.array(moveWeekSchema),
});

/* An add with the points and the projection of the weeks on the roster since the add. Three at most. */
export const bestAddSchema = managerPlayerSchema.extend({
  week: z.number(),
  points: z.number(),
  projection: z.number(),
  games: z.number(),
});

/* A player with the points of the weeks he started for the roster. Five at most. */
export const topPerformerSchema = managerPlayerSchema.extend({
  points: z.number(),
  games: z.number(),
  per_game: z.number(),
});

/* One saved week: the points, the league median, and the head-to-head result. Won is null for a bye or a tie.
   The median is null for a league with no median game, so the points line has no median line. */
export const seasonWeekSchema = z.object({
  week: z.number(),
  points: z.number(),
  median: z.number().nullable(),
  won: z.boolean().nullable(),
});

/* The worst week of the bench: the points the bench cost and the player that sat. */
export const benchWorstSchema = z.object({
  week: z.number(),
  points: z.number(),
  player_id: z.string(),
  name: z.string(),
});

/* The bench points of the season. Worst is null when no week had a bench gain. */
export const benchSchema = z.object({ total: z.number(), worst: benchWorstSchema.nullable() });

/* The counts of the report awards the roster won. */
export const awardCountsSchema = z.object({
  top_scorer: z.number(),
  mvb: z.number(),
  game_changer: z.number(),
  underperformer: z.number(),
});

/* One slot rank: the team's rank at the position, 1 to 12, and one depth word. */
export const slotRankSchema = z.object({
  position: z.enum(["QB", "RB", "WR", "TE"]),
  rank: z.number(),
  depth: z.enum(["stacked", "deep", "fine", "thin"]),
});

/* One part of the grade: the roster's rank on the part, 1 to 12. */
export const gradePartSchema = z.object({
  key: z.enum(["projection", "production", "trade_value", "depth"]),
  rank: z.number(),
});

/* The roster grade: the letter, the slot ranks in the order QB, RB, WR, TE, and the four parts in the order projection,
   production, trade value, depth. The file never carries the score. */
export const managerGradeSchema = z.object({
  letter: z.string(),
  slots: z.array(slotRankSchema),
  parts: z.array(gradePartSchema),
  read: z.string(),
});

/* One roster of the season, with the record through the last saved week.
   The bench is null when the build had no roster slots. The grade is null when the build had no snapshot. */
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

/* Through is the last saved week the build read. */
export const managersFileSchema = z.object({
  schema_version: z.literal(1),
  season: z.number(),
  through: z.number(),
  managers: z.array(managerEntrySchema),
});
