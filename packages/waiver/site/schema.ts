/**
 * The Zod schema of the waiver.json file that the Python build writes beside page.json in a week folder.
 * A key that an older build may leave out is optional, so the site reads every file the pipeline wrote.
 */
import { z } from "zod";

/* The three scores of a pool player, each from 0 to 1. A score with no input is 0. */
export const boardScoresSchema = z.object({
  usage: z.number(),
  environment: z.number(),
  projection: z.number(),
});

/* One fact of the pipeline. The numbers field holds every number in the text, so the checks can match the page to the facts. */
export const waiverFactSchema = z.object({
  id: z.string(),
  text: z.string(),
  numbers: z.array(z.string()),
  teams: z.array(z.string()),
  players: z.array(z.string()),
});

/* The most recent winning claim at the player's position this season. The roster id names the fantasy team that won it. */
export const lastLikeSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  roster_id: z.number(),
  team: z.string(),
  week: z.number(),
  bid: z.number(),
});

/* The bid to win of one pool player, a whole dollar, with the fact that holds its inputs.
   The outbid map maps a budget level to the count of managers that can bid more than that level. */
export const waiverPriceSchema = z.object({
  bid: z.number(),
  fact: waiverFactSchema,
  // Null when no claim at the position won this season.
  last_like: lastLikeSchema.nullable(),
  outbid: z.record(z.string(), z.number()),
});

/* Whether a research claim backs the board facts, disputes them, or is plain news. */
export const claimStanceSchema = z.enum(["backs", "disputes", "news"]);

/* One research claim: one sentence from a web source, with the link, the source name, and an ISO 8601 date. */
export const researchClaimSchema = z.object({
  text: z.string(),
  url: z.string(),
  source: z.string(),
  date: z.string(),
  stance: claimStanceSchema,
});

/* Why a rostered player is a drop: the roster and team name that hold him, the reason code,
   and the pool player who beats him by a margin in points a week. */
export const dropInfoSchema = z.object({
  roster_id: z.number(),
  holder: z.string(),
  reason: z.string(),
  beaten_by: z.string(),
  beaten_by_name: z.string(),
  margin: z.number(),
});

/* One ranked player of a bucket. The week projection is for the next week, the rest of season one runs to week 17. */
export const waiverPlayerSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  team: z.string(),
  week_projection: z.number(),
  ros_projection: z.number(),
  scores: boardScoresSchema,
  board_score: z.number(),
  // The first file has no bye. A later build adds it.
  bye: z.number().nullable().optional(),
  // The Sleeper injury status and the expected return week, for a stash.
  injury_status: z.string().nullable().optional(),
  return_week: z.number().nullable().optional(),
  // The adds across all Sleeper leagues in the last day. 0 when he is not in the trending file.
  trending_count: z.number().optional(),
  facts: z.array(waiverFactSchema).optional(),
  // Null for a drop.
  price: waiverPriceSchema.nullable().optional(),
  research: z.array(researchClaimSchema).optional(),
  // The reason code of the bucket rule that picked the player, or null.
  reason: z.string().nullable().optional(),
  // Null for a pool player. Only a player in the drops bucket has it.
  drop: dropInfoSchema.nullable().optional(),
});

/* The FAAB budget left and the waiver order of one roster. */
export const budgetRowSchema = z.object({
  roster_id: z.number(),
  budget_left: z.number(),
  waiver_order: z.number(),
});

/* The board of one week: the buckets by key, each in rank order, and the budget table in roster order. */
export const waiverBoardSchema = z.object({
  schema_version: z.literal(1),
  week: z.number(),
  // An ISO 8601 date and time.
  built: z.string(),
  buckets: z.record(z.string(), z.array(waiverPlayerSchema)),
  budgets: z.array(budgetRowSchema),
  // True when the research step failed for every player, so the page says the experts are out.
  experts_missing: z.boolean().optional(),
});
