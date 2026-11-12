/**
 * The Zod schema of the recap card, the block of Week recap in topics.json, and its line of plain text for the Thread.
 * The pipeline owns the shape (ADR 0013), in apps/pipeline/src/cornerstone/topic_blocks.py.
 */
import { z } from "zod";
import { num, ordinal } from "@cpc/design/format/format";

/* The recap card: the score and the place of Your team, its opponent, one mark per team high to low, the top scorer of
   Your team against his projection, and the first sentence of the recap of its game. The median is null in a league
   that plays no median game, so the strip draws no median tick there. */
export const recapBlockSchema = z.object({
  kind: z.literal("recap"),
  score: z.number(),
  place: z.number(),
  teams: z.number(),
  opponent: z.string().nullable(),
  opponent_score: z.number().nullable(),
  strip: z.array(z.object({ roster_id: z.number(), name: z.string(), score: z.number(), you: z.boolean() })),
  median: z.number().nullable(),
  top: z.object({ name: z.string(), position: z.string(), points: z.number(), projection: z.number().nullable() }).nullable(),
  sentence: z.string().nullable(),
});

export type RecapBlock = z.infer<typeof recapBlockSchema>;

/* The card as one short line of plain text, so the turn of the Answer carries it and a follow-up has context. */
export function recapText(block: RecapBlock): string {
  const game = block.opponent && block.opponent_score !== null ? ` against ${block.opponent}, ${num(block.opponent_score)}` : "";
  const median = block.median === null ? "" : ` The median was ${num(block.median)}.`;
  const top = block.top ? ` Top scorer: ${block.top.name}, ${num(block.top.points)}${block.top.projection === null ? "" : ` (projected ${num(block.top.projection)})`}.` : "";
  return `You scored ${num(block.score)}${game}, ${ordinal(block.place)} of ${block.teams}.${median}${top}`;
}
