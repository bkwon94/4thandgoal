/**
 * The Zod schema of the week page JSON that the Python build writes beside each week's images.
 * The JSON turns int keys into strings, so maps take string roster ids.
 */
import { z } from "zod";

/* A player on bye next week. A key starter is a player the team started in 3 of its last 4 weeks. */
export const byePlayerSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  key: z.boolean(),
});

export const teamSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  owner: z.string(),
  avatar_url: z.string().nullable(),
  wins: z.number(),
  losses: z.number(),
  points_for: z.number(),
  /* Only a next-week side has this list. Key starters come first. Older page JSON has none, which reads as empty. */
  byes: z.array(byePlayerSchema).optional(),
});

/* One player's line for the week. A defense has its team code as the player id. */
export const playerLineSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  nfl_team: z.string().nullable(),
  points: z.number(),
  projection: z.number().nullable(),
  season_avg: z.number().nullable(),
  started: z.boolean(),
  slot: z.string().nullable(),
  injury_status: z.string().nullable(),
  injury_body_part: z.string().nullable(),
});

/* One side of a matchup. A tie sets neither winner nor loser. */
export const matchupSideSchema = z.object({
  team: teamSchema,
  score: z.number(),
  top: playerLineSchema.nullable(),
  winner: z.boolean(),
  loser: z.boolean(),
});

export const pickSchema = z.object({
  reason: z.string(),
  sides: z.tuple([matchupSideSchema, matchupSideSchema]),
});

export const gameChangerSchema = z.object({
  award: z.object({
    key: z.string(),
    line: playerLineSchema,
    roster_id: z.number(),
    reason: z.string(),
  }),
  team: z.string(),
});

/* An award tile. A missing tile has no player, because the week had no projections. */
export const awardSchema = z.discriminatedUnion("missing", [
  z.object({ title: z.string(), missing: z.literal(true) }),
  z.object({
    title: z.string(),
    missing: z.literal(false),
    player: z.string(),
    player_id: z.string(),
    points: z.number(),
    team: z.string(),
    projection: z.number().nullable(),
  }),
]);

export const leaderRowSchema = z.object({
  rank: z.number(),
  player: z.string(),
  player_id: z.string(),
  nfl_team: z.string().nullable(),
  points: z.number(),
  team: z.string(),
});

export const leaderBoardSchema = z.object({
  position: z.string(),
  rows: z.array(leaderRowSchema),
});

export const tradeSideSchema = z.object({
  team: teamSchema,
  players: z.array(z.object({ name: z.string(), headshot: z.string() })),
  picks: z.array(z.string()),
});

export const tradeSchema = z.object({ sides: z.array(tradeSideSchema) });

export const matchupSchema = z.object({
  id: z.number(),
  sides: z.tuple([matchupSideSchema, matchupSideSchema]),
  is_pick: z.boolean(),
  recap: z.string().nullable(),
});

export const medianSchema = z.object({
  value: z.number(),
  above: z.object({ team: teamSchema, gap: z.number() }),
  below: z.object({ team: teamSchema, gap: z.number() }),
  bars: z.array(z.object({ team: teamSchema, score: z.number(), above: z.boolean(), pct: z.number() })),
  line_pct: z.number(),
});

export const tableRowSchema = z.object({
  standing: z.object({
    rank: z.number(),
    roster_id: z.number(),
    wins: z.number(),
    losses: z.number(),
    points_for: z.number(),
  }),
  team: teamSchema,
});

export const nextGameSchema = z.object({
  a: teamSchema,
  b: teamSchema,
  must_watch: z.boolean(),
  reason: z.string().nullable(),
});

/* The catchall holds the per-matchup recap keys, which the page names by matchup. */
export const blurbsSchema = z
  .object({
    motw: z.string(),
    game_changer: z.string().optional(),
    awards: z.string(),
    position_leaders: z.string().optional(),
    median: z.string().optional(),
    next_week: z.string().optional(),
  })
  .catchall(z.string().optional());

/* Image paths in both maps are relative to the week folder, for example avatars/4.jpg. */
export const avatarMapSchema = z.record(z.string(), z.string());
export const headshotMapSchema = z.record(z.string(), z.string());

export const weekPageSchema = z.object({
  schema_version: z.literal(2),
  season: z.number(),
  week: z.number(),
  dates: z.string(),
  publish_date: z.string(),
  summary: z.string(),
  teams: z.record(z.string(), teamSchema),
  pick: pickSchema,
  game_changer: gameChangerSchema.nullable(),
  awards: z.array(awardSchema),
  leaders: z.array(leaderBoardSchema),
  trades: z.array(tradeSchema),
  matchups: z.array(matchupSchema),
  median: medianSchema.nullable(),
  table: z.array(tableRowSchema),
  next: z.array(nextGameSchema),
  blurbs: blurbsSchema,
  avatars: avatarMapSchema,
  headshots: headshotMapSchema,
});
