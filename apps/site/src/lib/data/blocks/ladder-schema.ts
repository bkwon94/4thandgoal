/**
 * The Zod schema of the standings ladder, the block of Playoff race, with the top Finishes and the status pill of Your
 * team, and its line of plain text for the Thread.
 * The pipeline owns the shape (ADR 0013), in apps/pipeline/src/cornerstone/topic_blocks.py.
 */
import { z } from "zod";

/* The standings ladder: one row per team by standing, with its record and its playoff odds in percent. The odds are
   null when the week has no odds for a team. The playoff line sits under the row of rank `playoff_teams`. */
export const ladderBlockSchema = z.object({
  kind: z.literal("ladder"),
  playoff_teams: z.number(),
  rows: z.array(
    z.object({
      roster_id: z.number(),
      name: z.string(),
      rank: z.number(),
      record: z.string(),
      odds: z.number().nullable(),
      you: z.boolean(),
    }),
  ),
  // The likeliest Finishes of Your team for a playoff spot, best Finish first, from the sim page of the week. A week
  // or a client with no sim file has none.
  finishes: z
    .array(
      z.object({
        name: z.string(),
        record: z.string(),
        chance: z.number(),
        odds: z.number(),
        about: z.boolean(),
      }),
    )
    .default([]),
  // The status pill of The Race for a spot. Null for a team In the hunt.
  pill: z
    .object({ kind: z.enum(["clinched", "out"]), label: z.string() })
    .nullable()
    .default(null),
});

export type LadderBlock = z.infer<typeof ladderBlockSchema>;
export type LadderFinish = LadderBlock["finishes"][number];

/* The odds of a row in words, such as "62% playoff odds", or "no odds". */
export const oddsWords = (odds: number | null): string =>
  odds === null ? "no odds" : `${odds}% playoff odds`;

/* The odds of a Finish, such as "80%" or "about 75%". */
export const finishOdds = (finish: LadderFinish): string =>
  `${finish.about ? "about " : ""}${finish.odds}%`;

/* One Finish in words, such as "4-2, ends 15-13, 26% likely: 80% playoff odds". */
export const finishWords = (finish: LadderFinish): string =>
  `${finish.name}, ends ${finish.record}, ${Math.round(finish.chance)}% likely: ${finishOdds(finish)} playoff odds`;

/* The ladder as one short line of plain text, so the turn of the Answer carries it and a follow-up has context. */
export function ladderText(block: LadderBlock): string {
  const rows = block.rows
    .map((row) => `${row.rank}. ${row.name}, ${row.record}, ${oddsWords(row.odds)}`)
    .join("; ");
  const status = block.pill ? ` Status: ${block.pill.label}.` : "";
  const finishes = block.finishes.length
    ? ` Rest of season: ${block.finishes.map(finishWords).join("; ")}.`
    : "";
  return `Standings: ${rows}. The top ${block.playoff_teams} make the playoffs.${status}${finishes}`;
}
