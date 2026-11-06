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

/* Draft steals and busts: the cost rank against the points rank among the drafted players of each position. */
export const draftRowSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  roster_id: z.number(),
  team: z.string(),
  // The price in dollars in an auction, the pick number in a snake.
  cost: z.number(),
  cost_rank: z.number(),
  points: z.number(),
  points_rank: z.number(),
  swing: z.number(),
  // "hurt" or "just bad" on a bust. Null on a steal.
  tag: z.enum(["hurt", "just bad"]).nullable(),
  // "the one that got away" on a steal that its drafter dropped.
  line: z.string().nullable(),
});

export const draftChapterSchema = z.object({
  key: z.literal("draft"),
  title: z.string(),
  facts: z.object({
    draft_type: z.enum(["auction", "snake", "linear"]),
    steals: z.array(draftRowSchema),
    busts: z.array(draftRowSchema),
  }),
  ...prose,
});

/* Waiver hits and misses: one stint of an added player on the roster that added him. */
export const pickupSchema = z.object({
  player_id: z.string(),
  player: z.string(),
  position: z.string(),
  roster_id: z.number(),
  team: z.string(),
  week: z.number(),
  // 0 for a free agent add.
  bid: z.number(),
  starts: z.number(),
  points: z.number(),
  points_over_line: z.number().nullable(),
  swung_wins: z.number(),
  played: z.boolean(),
});

export const outbidSchema = z.object({
  player_id: z.string(),
  player: z.string(),
  roster_id: z.number(),
  team: z.string(),
  bid: z.number(),
  winner_roster_id: z.number(),
  winner: z.string(),
  winner_bid: z.number(),
  margin: z.number(),
  winner_points_over_line: z.number(),
});

export const streamerSchema = z.object({
  roster_id: z.number(),
  team: z.string(),
  players: z.number(),
  starts: z.number(),
  points: z.number(),
});

export const waiversChapterSchema = z.object({
  key: z.literal("waivers"),
  title: z.string(),
  facts: z.object({
    hits: z.array(pickupSchema),
    misses: z.array(pickupSchema),
    outbid: z.array(outbidSchema),
    // Most points first. The first is the streaming king.
    streamers: z.array(streamerSchema),
  }),
  ...prose,
});

/* The trade report card: every trade, the biggest gap first, each Too soon trade last. */
export const tradePlayerSchema = z.object({
  player_id: z.string(),
  player: z.string(),
  position: z.string(),
  starts: z.number(),
  points_over_line: z.number().nullable(),
  // True when he missed his NFL team's game in the first week after the trade.
  hurt_on_arrival: z.boolean(),
});

export const tradeSideSchema = z.object({
  roster_id: z.number(),
  team: z.string(),
  got: z.array(tradePlayerSchema),
  net: z.number(),
  // The record of the team since the trade.
  since: z.object({ wins: z.number(), losses: z.number(), ties: z.number() }),
});

export const tradeCardSchema = z.object({
  transaction_id: z.string(),
  week: z.number(),
  weeks_since: z.number(),
  sides: z.array(tradeSideSchema),
  gap: z.number(),
  result: z.enum(["Robbery", "Clear win", "Slight edge", "Push", "Too soon"]),
  winner: z.string().nullable(),
});

export const tradesChapterSchema = z.object({
  key: z.literal("trades"),
  title: z.string(),
  facts: z.object({ trades: z.array(tradeCardSchema) }),
  ...prose,
});

/* Lineup choices: one row per team, most Bench points first, with the losses that its best lineup would have won. */
export const lostWeekSchema = z.object({
  week: z.number(),
  opponent_roster_id: z.number(),
  opponent: z.string(),
  score: z.number(),
  best: z.number(),
  bench_points: z.number(),
  margin: z.number(),
});

export const teamLineupSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  rank: z.number(),
  bench_points: z.number(),
  lost_with_better: z.array(lostWeekSchema),
});

export const lineupChapterSchema = z.object({
  key: z.literal("lineup"),
  title: z.string(),
  facts: z.object({ teams: z.array(teamLineupSchema) }),
  ...prose,
});

/* The record book: the four records of the season, then the seven awards in page order. */
export const teamScoreSchema = z.object({ week: z.number(), roster_id: z.number(), team: z.string(), score: z.number() });

export const gameSchema = z.object({
  week: z.number(),
  winner_roster_id: z.number(),
  winner: z.string(),
  winner_score: z.number(),
  loser_roster_id: z.number(),
  loser: z.string(),
  loser_score: z.number(),
  margin: z.number(),
});

export const awardSchema = z.object({
  key: z.enum(["mvp", "streaming-king", "bench-crime", "heartbreak", "beatdown", "most-active", "set-and-forget"]),
  title: z.string(),
  roster_id: z.number(),
  team: z.string(),
  value: z.number(),
  player: z.string().nullable(),
  week: z.number().nullable(),
  // True for Heartbreak and Beatdown, which the page shows on their game of the record book.
  in_record_book: z.boolean(),
  fact: z.string(),
});

export const recordsChapterSchema = z.object({
  key: z.literal("records"),
  title: z.string(),
  facts: z.object({
    high: teamScoreSchema,
    low: teamScoreSchema,
    biggest_margin: gameSchema,
    closest: gameSchema,
    awards: z.array(awardSchema),
  }),
  ...prose,
});

/* The look ahead: each team's games left with the record of each opponent, the softest schedule first. */
export const gameLeftSchema = z.object({
  week: z.number(),
  opponent: z.number(),
  name: z.string(),
  wins: z.number(),
  losses: z.number(),
  ties: z.number(),
});

export const teamLookAheadSchema = z.object({
  roster_id: z.number(),
  name: z.string(),
  games: z.array(gameLeftSchema),
  // The win rate of all the opponents, with a tie as half a win. Null when the team has no game left.
  opponents_rate: z.number().nullable(),
});

export const lookAheadChapterSchema = z.object({
  key: z.literal("look-ahead"),
  title: z.string(),
  facts: z.object({ teams: z.array(teamLookAheadSchema), softest: z.number().nullable(), hardest: z.number().nullable() }),
  ...prose,
});

/* Players to watch: Due to rise and Due to fall from the Expected gap, and Grab him now from the projections. */
export const gapPlayerSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  nfl_team: z.string().nullable(),
  // The Expected gap per game. Under zero is under expected.
  gap: z.number(),
  games: z.number(),
  roster_id: z.number(),
  manager: z.string(),
});

export const grabPlayerSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  nfl_team: z.string().nullable(),
  // The sum of his projections for the weeks left of the regular season.
  projection: z.number(),
  roster_id: z.null(),
});

export const watchChapterSchema = z.object({
  key: z.literal("watch"),
  title: z.string(),
  facts: z.object({
    due_to_rise: z.array(gapPlayerSchema),
    due_to_fall: z.array(gapPlayerSchema),
    grab_him_now: z.array(grabPlayerSchema),
  }),
  ...prose,
});

/* Each chapter has a fixed key, so the page picks the part of a chapter by its key. */
export const chapterSchema = z.discriminatedUnion("key", [
  stateChapterSchema,
  arcsChapterSchema,
  luckChapterSchema,
  injuryChapterSchema,
  top10ChapterSchema,
  draftChapterSchema,
  waiversChapterSchema,
  tradesChapterSchema,
  lineupChapterSchema,
  recordsChapterSchema,
  lookAheadChapterSchema,
  watchChapterSchema,
]);

/* One of the three acts of the report, each opened by a dark title page. */
export const actSchema = z.object({
  key: z.enum(["how-we-got-here", "the-moves", "what-comes-next"]),
  title: z.string(),
  chapters: z.array(chapterSchema),
});

export const midseasonSchema = z.object({
  schema_version: z.literal(1),
  season: z.number(),
  // The last week that the report counts.
  week: z.number(),
  // The last published week that still shows the takeover on the home page.
  takeover_end_week: z.number(),
  opener: openerSchema,
  acts: z.array(actSchema),
});
