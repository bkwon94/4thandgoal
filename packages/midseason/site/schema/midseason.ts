/**
 * The Zod schema of the season midseason file that the Python build writes beside the week folders.
 * The pipeline owns the shape in midseason/published.py, and this schema follows it (ADRs 0011 and 0013).
 */
import { z } from "zod";

/* One sentence of a blurb, with the IDs of the facts it rests on. */
export const sentenceSchema = z.object({
  text: z.string(),
  fact_ids: z.array(z.string()),
  roster_id: z.number().nullable().optional(),
});

/* The prose of one block. The writer marks a fallback when no draft passed the verifier. */
export const blurbSchema = z.object({
  chapter: z.string(),
  sentences: z.array(sentenceSchema),
  attempt: z.number(),
  fallback: z.boolean(),
});

/* The blurb and the roast of a chapter or of the opener. A roast is null when the roast setting of the client is off. */
const prose = { blurb: blurbSchema.nullable(), roast: blurbSchema.nullable() };

/* The opener, the title race: the leaders by title odds, best first, and the record leader. */
export const titleLeaderSchema = z.object({ roster_id: z.number(), name: z.string(), title_odds: z.number() });

export const recordLeaderSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  wins: z.number(),
  losses: z.number(),
  ties: z.number(),
  title_odds: z.number().nullable(),
  // The place of its title odds in the league, best first.
  title_rank: z.number().nullable(),
});

export const openerSchema = z.object({
  title: z.string(),
  facts: z.object({ leaders: z.array(titleLeaderSchema), record_leader: recordLeaderSchema }),
  ...prose,
});

/* The state of the league: one row per team in standings order. The full record counts the median game in CPC. */
export const teamStateSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  rank: z.number(),
  wins: z.number(),
  losses: z.number(),
  ties: z.number(),
  points_for: z.number(),
  points_against: z.number(),
  streak: z.object({ kind: z.enum(["W", "L"]), length: z.number() }).nullable(),
  // Whole percent. Null when the app had no odds for the team.
  playoff_odds: z.number().nullable(),
});

export const stateChapterSchema = z.object({
  key: z.literal("state"),
  title: z.string(),
  facts: z.object({ teams: z.array(teamStateSchema) }),
  ...prose,
});

/* The arcs: at most 2 per team, the biggest swing first. Each arc fills only the numbers that it reads. */
export const windowRecordSchema = z.object({
  first_week: z.number(),
  last_week: z.number(),
  wins: z.number(),
  losses: z.number(),
  ties: z.number(),
});

export const arcSchema = z.object({
  kind: z.enum([
    "Turnaround",
    "Collapse",
    "Wire to wire",
    "Never got going",
    "Roller coaster",
    "Snakebit",
    "Smoke and mirrors",
    "Heater",
  ]),
  swing: z.number(),
  start: windowRecordSchema.nullable(),
  now: windowRecordSchema.nullable(),
  win_streak: z.number().nullable(),
  loss_streak: z.number().nullable(),
  schedule_luck: z.number().nullable(),
});

export const teamArcsSchema = z.object({ roster_id: z.number(), name: z.string(), arcs: z.array(arcSchema) });

export const arcsChapterSchema = z.object({
  key: z.literal("arcs"),
  title: z.string(),
  facts: z.object({ teams: z.array(teamArcsSchema) }),
  ...prose,
});

/* Schedule luck: head-to-head wins minus All-play wins, most luck first. A tie counts half in each count. */
export const teamLuckSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  head_to_head_wins: z.number(),
  all_play_wins: z.number(),
  schedule_luck: z.number(),
  points_against: z.number(),
  // The rank puts the most points against first.
  points_against_rank: z.number(),
  close_wins: z.number(),
  close_losses: z.number(),
  close_ties: z.number(),
});

/* The record of the row team with the schedule of `schedule_of`. */
export const swapCellSchema = z.object({
  schedule_of: z.number(),
  wins: z.number(),
  losses: z.number(),
  ties: z.number(),
});

export const swapRowSchema = z.object({ roster_id: z.number(), name: z.string(), cells: z.array(swapCellSchema) });

/* The best schedule other than its own for one team, with the record that it gives. */
export const bestMissedSchema = swapCellSchema.extend({ roster_id: z.number() });

export const scheduleSwapSchema = z.object({
  // A row is a team and a column is a schedule, both in standings order.
  rows: z.array(swapRowSchema),
  best_missed: z.array(bestMissedSchema),
  most_better: z.object({ roster_id: z.number(), count: z.number() }).nullable(),
});

export const luckChapterSchema = z.object({
  key: z.literal("luck"),
  title: z.string(),
  facts: z.object({ teams: z.array(teamLuckSchema), swap: scheduleSwapSchema }),
  ...prose,
});

/* The injury toll: one row per team, most starter games lost first. */
export const injuredStarterSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  games: z.number(),
  weeks: z.array(z.number()),
});

export const teamInjuryTollSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  rank: z.number(),
  games: z.number(),
  players: z.array(injuredStarterSchema),
});

export const injuryChapterSchema = z.object({
  key: z.literal("injuries"),
  title: z.string(),
  facts: z.object({ teams: z.array(teamInjuryTollSchema) }),
  ...prose,
});

/* Position top 10: one board per position that the league starts, in lineup order. */
export const topPlayerSchema = z.object({
  rank: z.number(),
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  nfl_team: z.string().nullable(),
  points: z.number(),
  games: z.number(),
  points_per_game: z.number(),
  // The team that rosters him now. Null, with the tag "Free agent", for a free agent.
  roster_id: z.number().nullable(),
  manager: z.string().nullable(),
  tag: z.string().nullable(),
});

export const positionBoardSchema = z.object({ position: z.string(), players: z.array(topPlayerSchema) });

export const top10ChapterSchema = z.object({
  key: z.literal("top10"),
  title: z.string(),
  facts: z.object({ positions: z.array(positionBoardSchema) }),
  ...prose,
});

/* A chapter of Act II or Act III. The page shows its title and its prose. Its facts stay unknown until a part of the
   package reads them, so the schema checks only what the page reads. */
export const otherChapterSchema = z.object({
  key: z.enum(["draft", "waivers", "trades", "look-ahead", "watch"]),
  title: z.string(),
  facts: z.unknown(),
  ...prose,
});

/* Each chapter has a fixed key, so the page picks the part of a chapter by its key. */
export const chapterSchema = z.discriminatedUnion("key", [
  stateChapterSchema,
  arcsChapterSchema,
  luckChapterSchema,
  injuryChapterSchema,
  top10ChapterSchema,
  otherChapterSchema,
]);

/* One of the three acts of the report, each opened by a dark title page. */
export const actSchema = z.object({
  key: z.enum(["how-we-got-here", "the-moves", "what-comes-next"]),
  title: z.string(),
  chapters: z.array(chapterSchema),
});

/* The one big fact of the home tile, which the home page shows after the takeover ends. */
export const reportTileSchema = z.object({ label: z.string(), value: z.string(), note: z.string() });

export const midseasonSchema = z.object({
  schema_version: z.literal(1),
  season: z.number(),
  // The last week that the report counts.
  week: z.number(),
  // The last published week that still shows the takeover on the home page.
  takeover_end_week: z.number(),
  opener: openerSchema,
  acts: z.array(actSchema),
  tile: reportTileSchema,
});
