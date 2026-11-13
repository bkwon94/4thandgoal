/**
 * The Zod schema of the rank mover list, the block of Power rankings, and its line of plain text for the Thread.
 * The pipeline owns the shape (ADR 0013), in apps/pipeline/src/cornerstone/topic_blocks.py.
 */
import { z } from "zod";

/* The rank mover list: one row per team by power rank, with its move in places since the week before. The move is
   positive up and negative down, and null in the first ranked week. */
export const rankMoversBlockSchema = z.object({
  kind: z.literal("rank_movers"),
  rows: z.array(z.object({ roster_id: z.number(), name: z.string(), rank: z.number(), move: z.number().nullable(), you: z.boolean() })),
});

export type RankMoversBlock = z.infer<typeof rankMoversBlockSchema>;

/* A move in words, such as "up 3", "down 4", or "no change". */
export const moveWords = (move: number | null): string => (move === null || move === 0 ? "no change" : move > 0 ? `up ${move}` : `down ${-move}`);

/* The list as one short line of plain text, so the turn of the Answer carries it and a follow-up has context. */
export function rankMoversText(block: RankMoversBlock): string {
  return `Power rankings: ${block.rows.map((row) => `${row.rank}. ${row.name}, ${moveWords(row.move)}`).join("; ")}.`;
}
