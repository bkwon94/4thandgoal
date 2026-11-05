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

/* The call for the asker's side. differs is true when the call goes against the chart. The reason then says why. */
export const decisionSchema = z.object({
  for_roster: z.number(),
  answer: z.enum(["yes", "no", "not_as_is"]),
  reason: z.string(),
  differs: z.boolean(),
});

/* One factor leans for the side, against it, or neither way. The first factor of a side is the deal row. */
export const factorSchema = z.object({
  name: z.string(),
  lean: z.enum(["for", "against", "even"]),
  reason: z.string(),
});

/* The read of one side: 2 or 3 bullets, each one sentence, and the factors. bullets is empty when the writer call failed, so the rows stand alone. */
export const decidedSideSchema = z.object({
  roster_id: z.number(),
  bullets: z.array(z.string()),
  factors: z.array(factorSchema),
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
      z.object({ state: z.enum(["win_win", "fair"]), gives_more: z.null() }),
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
  decision: decisionSchema,
  // Optional, because the ticket asks the page to render a document with no block, as a guard. The page then shows no fairness line.
  fairness: fairnessSchema.optional(),
  sides: z.array(decidedSideSchema),
  as_of: asOfSchema,
  // True when the writer call failed, so no side has bullets.
  fallback: z.boolean(),
  missing: z.array(z.string()),
  stale: z.array(z.string()),
});

/* One trade of the finder. The sides share the analyze document's side shape, so the site renders a side one way.
   reason is null when the Claude call failed twice. The fairness line then stands alone. */
export const finderTradeSchema = z.object({
  sides: z.array(tradeSideSchema),
  fairness: fairnessSchema,
  reason: z.string().nullable(),
});

/* The finder document that the site API returns from POST /find. It follows the fixture at .scratch/site-react/fixtures/find-response.json. */
export const findResponseSchema = z.object({
  season: z.number(),
  trade_pair: z.object({
    asker: z.object({ roster_id: z.number(), team: z.string() }),
    partner: z.object({ roster_id: z.number(), team: z.string() }),
  }),
  // Up to three trades, best first. The three share no player.
  trades: z.array(finderTradeSchema),
  // The line for an empty list, or null when the list has a trade. The page shows it as the pipeline writes it.
  empty: z.string().nullable(),
  as_of: asOfSchema,
  // True when the reason call failed, so every reason is null.
  fallback: z.boolean(),
  missing: z.array(z.string()),
  stale: z.array(z.string()),
});
