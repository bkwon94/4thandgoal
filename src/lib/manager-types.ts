/**
 * The types of the season managers file that the Python build writes beside the rankings file.
 * Each file type is inferred from its schema in schemas/managers.ts. The joined Manager type is built by the loader.
 */
import type { z } from "zod";
import type { Odds } from "@/lib/rankings-types";
import type * as s from "./schemas/managers";

export type ManagerTeam = z.infer<typeof s.managerTeamSchema>;
export type ManagerPlayer = z.infer<typeof s.managerPlayerSchema>;
export type MoveAdd = z.infer<typeof s.moveAddSchema>;
export type MoveTrade = z.infer<typeof s.moveTradeSchema>;
export type MoveWeek = z.infer<typeof s.moveWeekSchema>;
export type Moves = z.infer<typeof s.movesSchema>;
export type BestAdd = z.infer<typeof s.bestAddSchema>;
export type TopPerformer = z.infer<typeof s.topPerformerSchema>;
export type SeasonWeek = z.infer<typeof s.seasonWeekSchema>;
export type BenchWorst = z.infer<typeof s.benchWorstSchema>;
export type Bench = z.infer<typeof s.benchSchema>;
export type AwardCounts = z.infer<typeof s.awardCountsSchema>;
export type SlotRank = z.infer<typeof s.slotRankSchema>;
export type GradePart = z.infer<typeof s.gradePartSchema>;
export type ManagerGrade = z.infer<typeof s.managerGradeSchema>;
export type ManagerEntry = z.infer<typeof s.managerEntrySchema>;
export type ManagersFile = z.infer<typeof s.managersFileSchema>;

/* One entry joined with the last week of the rankings file.
   Standing is the place in the standings, 1 to 12. Rank and movement are the power rank and its move, null with no rankings row.
   Odds is null when no week has odds. Odds change is the playoff percent minus that of the week before, null when the week before has no odds. */
export type Manager = ManagerEntry & {
  standing: number;
  rank: number | null;
  movement: number | null;
  odds: Odds | null;
  odds_change: number | null;
};

/* The managers are in standings order. */
export type Managers = { season: number; through: number; managers: Manager[] };
