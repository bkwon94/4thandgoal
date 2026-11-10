/**
 * The Zod schemas of the site API responses for the teams, analyze, and find calls.
 * They follow the fixtures at .scratch/site-react/fixtures/analyze-response.json and find-response.json.
 */
import { z } from "zod";

export const playerSchema = z.object({
  player_id: z.string(),
  name: z.string(),
  position: z.string(),
  nfl_team: z.string(),
  headshot: z.string(),
});

export const teamSchema = z.object({
  roster_id: z.number(),
  team: z.string(),
  manager: z.string(),
  // The live API may not send the avatar yet, so a missing field reads as null.
  avatar: z.string().nullable().default(null),
  players: z.array(playerSchema),
});

export const teamsResponseSchema = z.object({ teams: z.array(teamSchema) });

/* A traded player with his ranks. season_rank is his place at his position by total points this season, such as WR60.
   recent_rank is his place by points per game over the last 4 weeks, and it is null unless the gap to the Season rank is large.
   An old document lacks both, so each is optional. */
export const tradedPlayerSchema = playerSchema.extend({
  season_rank: z.string().nullable().optional(),
  recent_rank: z.string().nullable().optional(),
});

/* A player a side gives. to is the roster id of the side he goes to. An old document lacks it, so it is optional. */
export const givenPlayerSchema = tradedPlayerSchema.extend({ to: z.number().optional() });

/* A player a side gets. from is the roster id of the side he comes from. An old document lacks it, so it is optional. */
export const gotPlayerSchema = tradedPlayerSchema.extend({ from: z.number().optional() });

/* One team in the trade: the players it gives and the players it gets. */
export const tradeSideSchema = z.object({
  roster_id: z.number(),
  team: z.string(),
  gives: z.array(givenPlayerSchema),
  gets: z.array(gotPlayerSchema),
});

/* The Lean of the Advisor for the asker, on a 5-step scale from Pass to Send it. */
export const leanSchema = z.enum(["Send it", "Lean yes", "Gut call", "Lean no", "Pass"]);

/* The Mark of a Bullet: for the side, against it, or even. */
export const markSchema = z.enum(["for", "against", "even"]);

/* One claim of the Advisor about one side, with its Mark and the fact it rests on. fact_text is the text of that fact, so a tap shows it. */
export const bulletSchema = z.object({
  text: z.string(),
  mark: markSchema,
  fact_id: z.string(),
  fact_text: z.string(),
});

/* The Week line of one side for one week, written by the code: the count of the players who play, the opponent, each bye, and each player who is out. It is a plain line of text that the page shows as is. */
export const weekLineSchema = z.object({
  week: z.number(),
  text: z.string(),
});

/* The read of one side: 3 to 5 Bullets, then the Week lines of the trade week and the next week. */
export const readSideSchema = z.object({
  roster_id: z.number(),
  bullets: z.array(bulletSchema),
  week_lines: z.array(weekLineSchema),
});

/* One side of the fairness read: the roster id and the one reason for that side. */
export const fairnessSideSchema = z.object({
  roster_id: z.number(),
  reason: z.string(),
});

/* Whether the trade is good for both sides, fair, or lopsided. A lopsided trade always names gives_more, the roster id of the side that gives more. The other states have none. */
export const fairnessSchema = z
  .object({
    // One entry per side, in the order of the trade's sides.
    sides: z.array(fairnessSideSchema),
  })
  .and(
    z.union([
      z.object({ state: z.literal("fair"), gives_more: z.null() }),
      z.object({ state: z.literal("lopsided"), gives_more: z.number() }),
    ]),
  );

/* The games of the known-games week that the stat readers use. Pending counts are by plain name, such as snaps. */
export const knownGamesSchema = z.object({
  week: z.number(),
  games: z.number(),
  in_progress: z.number(),
  pending: z.record(z.string(), z.number()),
});

export const asOfSchema = z.object({
  // Null when the week has no trade value chart yet. The page never shows it.
  chart_week: z.number().nullable(),
  stats_through: z.number(),
  // A document can lack both fields, so each is optional.
  completed_through: z.number().optional(),
  known_games: knownGamesSchema.nullable().optional(),
  // True when the week has no trade value chart yet. A document can lack both fields, so each is optional.
  no_chart: z.boolean().optional(),
  // The sentence that says so, written by the pipeline. The API sends null on a week that has a chart.
  no_chart_note: z.string().nullable().optional(),
  // An ISO 8601 timestamp with an offset.
  rosters_fetched: z.string().nullable(),
});

export const analyzeResponseSchema = z.object({
  trade: z.object({
    // The roster id of the team that asks for the grade.
    asker: z.number(),
    sides: z.array(tradeSideSchema),
  }),
  // The Lean of the Advisor for the asker, and the Case under it, which leads with its condition.
  lean: leanSchema,
  case: z.string(),
  // Optional, because the ticket asks the page to render a document with no block, as a guard. The page then shows no fairness line.
  fairness: fairnessSchema.optional(),
  sides: z.array(readSideSchema),
  as_of: asOfSchema,
  missing: z.array(z.string()),
  stale: z.array(z.string()),
});

/* One trade of the finder. The sides share the analyze document's side shape, and the Bullets share its Bullet shape,
   so the site renders a side and a row one way. A pick has a headline and 2 to 3 Bullets, and no fact line.
   After a fallback, the headline is null, no Bullet stands, and fact_lines holds plain facts of the offer. */
export const finderTradeSchema = z.object({
  // The id of the offer on the shortlist, such as "2:10213-10:10235". The card keys on it.
  offer_id: z.string(),
  sides: z.array(tradeSideSchema),
  headline: z.string().nullable(),
  bullets: z.array(bulletSchema),
  fact_lines: z.array(z.string()),
});

/* The finder document that the site API returns from POST /find. It follows the fixture at .scratch/site-react/fixtures/find-response.json. */
export const findResponseSchema = z.object({
  season: z.number(),
  trade_pair: z.object({
    asker: z.object({ roster_id: z.number(), team: z.string() }),
    // Null for a find with no partner. Each trade then names its own partner in its sides.
    partner: z.object({ roster_id: z.number(), team: z.string() }).nullable(),
  }),
  // Up to three picks, best first. After a fallback, every offer of the shortlist, in its order.
  trades: z.array(finderTradeSchema),
  // The plain line for an empty list, or null when the list has a trade. The page shows it as the pipeline writes it.
  empty: z.string().nullable(),
  as_of: asOfSchema,
  // True when the pick call failed twice, so the trades are the shortlist with fact lines and no headline.
  fallback: z.boolean(),
  missing: z.array(z.string()),
  stale: z.array(z.string()),
});
