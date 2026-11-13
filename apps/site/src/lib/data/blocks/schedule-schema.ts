/**
 * The Zod schema of the schedule strip, the block of Your season, and its line of plain text for the Thread.
 * The pipeline owns the shape (ADR 0013), in apps/pipeline/src/cornerstone/topic_blocks.py.
 */
import { z } from "zod";
import { ordinal } from "@cpc/design/format/format";

/* The schedule strip: one row per week left, with the opponent of that week and its standing and record now. The
   playoff line is the rank `playoff_teams` out of `teams`. */
export const scheduleBlockSchema = z.object({
  kind: z.literal("schedule"),
  playoff_teams: z.number(),
  teams: z.number(),
  rows: z.array(z.object({ week: z.number(), roster_id: z.number(), opponent: z.string(), rank: z.number(), record: z.string() })),
});

export type ScheduleBlock = z.infer<typeof scheduleBlockSchema>;

/* The strip as one short line of plain text, so the turn of the Answer carries it and a follow-up has context. */
export function scheduleText(block: ScheduleBlock): string {
  const rows = block.rows.map((row) => `week ${row.week}, ${row.opponent} (${ordinal(row.rank)}, ${row.record})`).join("; ");
  return `Weeks left: ${rows}. The top ${block.playoff_teams} of ${block.teams} make the playoffs.`;
}
