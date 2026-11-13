/**
 * The Zod schema of the matchup card, the block of Your last matchup and Your next matchup, and its line of plain text.
 * The live card of the API shares the shape of the card.
 */
import { z } from "zod";
import { gap, num } from "@cpc/design/format/format";

/* The pipeline owns the shape (ADR 0013), in packages/league/python/src/league/matchup_card.py. */

/* The player of one side in one slot. The points are final for a played game and the projection for a game ahead. */
const matchupPlayerSchema = z.object({ name: z.string(), position: z.string(), nfl_team: z.string().nullable(), points: z.number() });

/* One team of the card with its total: the final score or the projected score. */
const matchupTeamSchema = z.object({ roster_id: z.number(), name: z.string(), score: z.number() });

/* The matchup card: the two teams, their scores, and the starting slots in the Sleeper order of the league. A side with
   an empty slot has null there. `final` tells final scores from projected ones. `odds` is the win chance of Your team
   from 0 to 1, or null when no odds are known, such as for a played game. `read_at` is the time of the live read of
   Sleeper in ISO 8601, on the live card of the API only. */
export const matchupBlockSchema = z.object({
  kind: z.literal("matchup"),
  final: z.boolean(),
  you: matchupTeamSchema,
  them: matchupTeamSchema,
  odds: z.number().nullable(),
  slots: z.array(z.object({ slot: z.string(), you: matchupPlayerSchema.nullable(), them: matchupPlayerSchema.nullable() })),
  read_at: z.string().optional(),
});

export type MatchupBlock = z.infer<typeof matchupBlockSchema>;
export type MatchupSlot = MatchupBlock["slots"][number];

/* The gap of one slot from the side of Your team: positive when Your player scored more. An empty side counts 0. */
export const slotGap = (slot: MatchupSlot): number => (slot.you?.points ?? 0) - (slot.them?.points ?? 0);

/* The card as one short line of plain text, so the turn of the Answer carries it and a follow-up has context. */
export function matchupText(block: MatchupBlock): string {
  const kind = block.final ? "Final" : "Projected";
  const odds = block.odds === null ? "" : ` Win odds ${Math.round(block.odds * 100)}%.`;
  const slots = block.slots.map((slot) => `${slot.slot} ${slot.you?.name ?? "empty"} ${num(slot.you?.points ?? 0)} vs ${slot.them?.name ?? "empty"} ${num(slot.them?.points ?? 0)} (${gap(slotGap(slot))})`);
  return `${kind}: ${block.you.name} ${num(block.you.score)}, ${block.them.name} ${num(block.them.score)}.${odds} ${slots.join("; ")}.`;
}
