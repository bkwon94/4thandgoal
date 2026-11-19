/**
 * The Zod schemas of the sim files that the Python build writes: the season file and the week file with its pages.
 * The pipeline owns the shapes in sim/published.py and sim/page.py, and these schemas follow them (ADRs 0011 and 0013).
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

/* A result of a game in a league with a median game sets the median too. A null odds number means no run had it. */
const gameSchema = z.enum(["win", "loss"]);
const medianSchema = z.enum(["above", "below"]).nullable();
const oddsSchema = z.number().int().nullable();

/* One count of more wins in the weeks left, with its playoff odds and its chance in percent of all runs. */
export const ladderStepSchema = z.object({
  more_wins: z.number().int(),
  playoff: oddsSchema,
  chance: z.number(),
  // True when the chance times the effective runs is under 400 runs, so the page shows "about".
  about: z.boolean(),
});

/* One result of Your team in one week, with the odds after it. */
export const weekResultSchema = z.object({
  game: gameSchema,
  median: medianSchema,
  wins_added: z.number().int(),
  playoff: oddsSchema,
  chance: z.number(),
  about: z.boolean(),
});

/* The five reasons of a root-for row (PRD, the page block). */
export const rootForReasonSchema = z.enum([
  "2 wins ahead of you",
  "1 win ahead of you",
  "Level with you",
  "1 win behind you",
  "In the race for the last spot",
]);

/* One result of another game that lifts the odds of Your team after a loss, to `playoff` in whole points. */
export const rootForSchema = z.object({
  winner: z.number(),
  loser: z.number(),
  reason: rootForReasonSchema,
  playoff: z.number().int(),
  about: z.boolean(),
});

/* One regular week left for Your team: four results with a median game, two with none, and up to 3 root-for rows. */
export const pageWeekSchema = z.object({
  week: z.number(),
  opponent: z.number(),
  results: z.array(weekResultSchema),
  loss_playoff: oddsSchema,
  loss_about: z.boolean(),
  root_for: z.array(rootForSchema).max(3),
});

/* One result of Your team in its bracket game of this round, with the title odds after it in whole percent. */
export const playoffResultSchema = z.object({
  game: gameSchema,
  title: oddsSchema,
  chance: z.number(),
  about: z.boolean(),
});

/* The bracket game of Your team in this round. It exists only when both of its teams are set. */
export const playoffGameSchema = z.object({
  week: z.number(),
  opponent: z.number(),
  results: z.array(playoffResultSchema),
});

/* One game of a bracket round, the higher seed first. A null side is a team that is not set yet. */
export const bracketGameSchema = z.object({
  teams: z.tuple([z.number().nullable(), z.number().nullable()]),
  scores: z.tuple([z.number(), z.number()]).nullable(),
  winner: z.number().nullable(),
});

export const bracketRoundSchema = z.object({
  week: z.number(),
  played: z.boolean(),
  games: z.array(bracketGameSchema),
});

/* One seed of the bracket with its title odds in whole percent. A team that lost a played game is not alive. */
export const bracketTeamSchema = z.object({
  roster_id: z.number(),
  seed: z.number().int(),
  title: z.number().int(),
  alive: z.boolean(),
});

/* The playoff part of the page block, with no regular week left: Your team first, then the bracket. */
export const playoffsSchema = z.object({
  seed: z.number().int().nullable(),
  alive: z.boolean(),
  title: z.number().int(),
  // The week of the round to play. Null after the final.
  week: z.number().nullable(),
  bye: z.boolean(),
  game: playoffGameSchema.nullable(),
  teams: z.array(bracketTeamSchema),
  rounds: z.array(bracketRoundSchema),
  champion: z.number().nullable(),
});

/* The page block of one team. sim.json and the What-if answer share it, so the page reads one shape. */
export const simPageSchema = z.object({
  you: z.number(),
  playoff: z.number().int(),
  status: z.enum(["in", "out", "open"]),
  // The real wins and losses at the start of the sim. The median game counts in both.
  record: z.tuple([z.number(), z.number()]),
  weeks_left: z.number().int(),
  wins_left: z.number().int(),
  // The smallest count of more wins with playoff odds of 90 or more, which the sentence names.
  need: z.number().int().nullable(),
  sentence: z.string(),
  ladder: z.array(ladderStepSchema),
  weeks: z.array(pageWeekSchema),
  // The playoff part, with no regular week left. Null in the regular season. An older file has no key.
  playoffs: playoffsSchema.nullable().default(null),
});

/* The week file, week-NN/sim.json: the season shape with the run weights, a page for each team, and the league fact. */
export const weekSimSchema = simSchema.extend({
  effective_runs: z.number(),
  // The weight of each stored run, in the order of `sample`. The replay picks a run in proportion to its weight.
  sample_weights: z.array(z.number()),
  pages: z.record(rosterKey, simPageSchema),
  // The league fact of the Sim tile for a manager with no team set: the race, the favorite, or the champion.
  fact: z.string().nullable(),
  // The real scores of each played bracket week, by week and roster id. An older file has no key.
  played: z.record(rosterKey, z.record(rosterKey, z.number())).default({}),
});
