/**
 * The Zod schema of the standings ladder, the block of Playoff race, and its line of plain text for the Thread.
 * The pipeline owns the shape (ADR 0013), in apps/pipeline/src/cornerstone/topic_blocks.py.
 */
import { z } from "zod";

/* The standings ladder: one row per team by standing, with its record and its playoff odds in percent. The odds are
   null when the week has no odds for a team. The playoff line sits under the row of rank `playoff_teams`. */
export const ladderBlockSchema = z.object({
  kind: z.literal("ladder"),
  playoff_teams: z.number(),
  rows: z.array(z.object({ roster_id: z.number(), name: z.string(), rank: z.number(), record: z.string(), odds: z.number().nullable(), you: z.boolean() })),
});

export type LadderBlock = z.infer<typeof ladderBlockSchema>;

/* The odds of a row in words, such as "62% playoff odds", or "no odds". */
export const oddsWords = (odds: number | null): string => (odds === null ? "no odds" : `${odds}% playoff odds`);

/* The ladder as one short line of plain text, so the turn of the Answer carries it and a follow-up has context. */
export function ladderText(block: LadderBlock): string {
  const rows = block.rows.map((row) => `${row.rank}. ${row.name}, ${row.record}, ${oddsWords(row.odds)}`).join("; ");
  return `Standings: ${rows}. The top ${block.playoff_teams} make the playoffs.`;
}
