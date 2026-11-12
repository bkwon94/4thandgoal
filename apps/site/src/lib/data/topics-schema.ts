/**
 * The Zod schema of topics.json, the file that the weekly build writes beside page.json: the Answer of each league Topic
 * of the front door for each team. The pipeline owns the shape (ADR 0013), in apps/pipeline/src/cornerstone/topics.py.
 */
import { z } from "zod";
import { recapBlockSchema } from "./blocks/recap-schema";

/* The 7 Topics that the weekly build answers. The other 6 Topics of the front door are live from the API. */
export const LEAGUE_TOPICS = ["week_recap", "last_matchup", "next_matchup", "power_rankings", "playoff_race", "your_season", "leaders_trades"] as const;

export const leagueTopicSchema = z.enum(LEAGUE_TOPICS);

/* One number of the data block, such as Rank and 6th. */
export const topicStatSchema = z.object({ label: z.string(), value: z.string() });

/* One line of the data block, such as one side of a game. `you` marks the line of the team of the Answer. */
export const topicRowSchema = z.object({
  label: z.string(),
  value: z.string(),
  note: z.string().nullable(),
  roster_id: z.number().nullable(),
  you: z.boolean(),
});

/* The block of a league Topic: the data of its one card, one union over `kind`. A new kind joins with its schema in
   blocks/ and one line here, and the answer block of the front door adds the same schema to its union. */
export const topicBlockSchema = z.discriminatedUnion("kind", [
  recapBlockSchema,
]);

/* The Answer of one league Topic for one team. The fact is the line of its Suggestion, and the text holds the blurbs of
   the week as they are, one paragraph each. The block is new in version 2: it is null for a Topic with no card, and a
   version 1 file has no block at all. */
export const topicAnswerSchema = z.object({
  topic: leagueTopicSchema,
  fact: z.string(),
  stats: z.array(topicStatSchema),
  rows: z.array(topicRowSchema),
  text: z.array(z.string()),
  block: topicBlockSchema.nullish(),
});

export const topicsFileSchema = z.object({
  schema_version: z.union([z.literal(1), z.literal(2)]),
  season: z.number(),
  week: z.number(),
  // The Answers of each team, keyed by roster id as text.
  teams: z.record(z.string(), z.array(topicAnswerSchema)),
});

export type LeagueTopic = z.infer<typeof leagueTopicSchema>;
export type TopicStat = z.infer<typeof topicStatSchema>;
export type TopicRow = z.infer<typeof topicRowSchema>;
export type TopicBlock = z.infer<typeof topicBlockSchema>;
export type TopicAnswer = z.infer<typeof topicAnswerSchema>;
export type TopicsFile = z.infer<typeof topicsFileSchema>;
