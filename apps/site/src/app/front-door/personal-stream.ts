/**
 * A personal Topic as the Thread reads it: the data block from code, then the text and the check of the stream that the
 * free answer reads too. The block comes first in the stream, so the card shows the numbers before any word.
 */
import type { UIMessage } from "ai";
import { z } from "zod";
import { type TopicRow, type TopicStat, topicRowSchema, topicStatSchema } from "@/lib/data/topics-schema";
import { type AnswerBlock, answerBlockSchema } from "./answer-block";
import { type FreeView, viewOf } from "./free-stream";
import { lineupBlockSchema } from "./lineup-block";

/* The 4 personal Topics, which the API builds live for one team. */
export const PERSONAL_TOPICS = ["weak_spots", "stack_up", "waiver_targets", "start_sit"] as const;
export type PersonalTopic = (typeof PERSONAL_TOPICS)[number];
export const isPersonal = (key: string): key is PersonalTopic => (PERSONAL_TOPICS as readonly string[]).includes(key);

/* The line of each personal Topic in "More". The fact of a personal Topic comes with its Answer, so the line says what
   it does. */
export const PERSONAL_LINES: Record<PersonalTopic, string> = {
  weak_spots: "Where your lineup is soft",
  stack_up: "Your roster against the league",
  waiver_targets: "Adds that fit your weak spots",
  start_sit: "Your lineup for this week",
};

/* The Topic, the team, and the fact that each data block of a personal Topic carries, whatever its kind. */
const personalHeadSchema = z.object({ topic: z.enum(PERSONAL_TOPICS), team: z.number(), fact: z.string() });

/* The data block of a personal Topic with the kind "rows", in the shape of the data block of a league Topic: stats and
   rows. A block kept before the kind has none, so it reads as "rows". */
const rowsBlockSchema = personalHeadSchema.extend({
  kind: z.literal("rows").default("rows"),
  stats: z.array(topicStatSchema),
  rows: z.array(topicRowSchema),
  // When the numbers are from, such as "as of today" for the live grade of How you stack up.
  as_of: z.string().optional(),
  // The one block of the Topic, such as the slot rank bars of How you stack up. It takes the place of the stats and the
  // rows in the card. A block kept before the Topic had one has none, so the card shows its stats and rows.
  block: answerBlockSchema.optional(),
});

/* The data block of a personal Topic: the stats and rows, the lineup of Start or sit, or one block of the block
   contract, such as the waiver list. The lineup carries no fact, so it has its own branch. */
export const personalBlockSchema = z.union([
  rowsBlockSchema,
  lineupBlockSchema,
  z.intersection(answerBlockSchema, personalHeadSchema),
]);
export type PersonalBlock = z.infer<typeof personalBlockSchema>;

/* The stats and the rows that a data block shows on the card, and the block of the block contract that shows under
   them. A block of the contract has no stats and no rows of its own. A Topic Answer shows one block at most, so a
   rows part with its own nested block shows that block in place of its stats and rows. */
export function shownBlock(block: PersonalBlock): { stats: TopicStat[]; rows: TopicRow[]; asOf?: string; answerBlock: AnswerBlock | null } {
  if (block.kind === "rows") {
    if (block.block) return { stats: [], rows: [], asOf: block.as_of, answerBlock: block.block };
    return { stats: block.stats, rows: block.rows, asOf: block.as_of, answerBlock: null };
  }
  return { stats: [], rows: [], answerBlock: block };
}

/* The calm line of a cap from the API, with the closest Topics. Past a cap, the API makes no Claude call. */
export type PersonalCap = { line: string; closest: string[] };

/* What the stream shows so far: the view of the free answer, plus the data block, the key of the Answer, and the cap
   line in place of the text. */
export type PersonalView = FreeView & { block: PersonalBlock | null; key: string | null; cap: PersonalCap | null };

/* The checked Answer that the browser keeps: the data block, the text, and the key that the API kept it under. */
export const personalResultSchema = z.object({ block: personalBlockSchema, text: z.string(), key: z.string() });
export type PersonalResult = z.infer<typeof personalResultSchema>;

export function personalViewOf(message: UIMessage | undefined): PersonalView {
  let block: PersonalBlock | null = null;
  let key: string | null = null;
  let cap: PersonalCap | null = null;
  for (const part of message?.parts ?? []) {
    if (part.type === "data-block") {
      const parsed = personalBlockSchema.safeParse((part as { data: unknown }).data);
      if (parsed.success) block = parsed.data;
    } else if (part.type === "data-key") {
      const data = (part as { data: { key?: unknown } }).data;
      if (typeof data?.key === "string") key = data.key;
    } else if (part.type === "data-cap") {
      const data = (part as { data: { line?: unknown; closest?: unknown } }).data;
      if (typeof data?.line === "string" && Array.isArray(data.closest)) cap = { line: data.line, closest: data.closest.map(String) };
    }
  }
  // The data block of a personal Topic shows from `block`, so the free answer view of the same part shows no second copy.
  return { ...viewOf(message), answerBlock: null, block, key, cap };
}
