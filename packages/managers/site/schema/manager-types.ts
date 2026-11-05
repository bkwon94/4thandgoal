/**
 * The types of the season managers file that the Python build writes beside the rankings file.
 * Each file type is inferred from its schema in managers.ts.
 * The file holds one entry per roster. The odds and the power rank stay in the rankings file, and the site joins them.
 * The joined Manager and Managers types are not a published file. The loader builds them, so they stay hand-typed here.
 */
import type { z } from "zod";
import type * as schema from "./managers";

export type ManagerTeam = z.infer<typeof schema.managerTeamSchema>;
export type ManagerPlayer = z.infer<typeof schema.managerPlayerSchema>;
export type MoveAdd = z.infer<typeof schema.moveAddSchema>;
export type MoveTrade = z.infer<typeof schema.moveTradeSchema>;
export type MoveWeek = z.infer<typeof schema.moveWeekSchema>;
export type Moves = z.infer<typeof schema.movesSchema>;
export type BestAdd = z.infer<typeof schema.bestAddSchema>;
export type TopPerformer = z.infer<typeof schema.topPerformerSchema>;
export type SeasonWeek = z.infer<typeof schema.seasonWeekSchema>;
export type BenchWorst = z.infer<typeof schema.benchWorstSchema>;
export type Bench = z.infer<typeof schema.benchSchema>;
export type AwardCounts = z.infer<typeof schema.awardCountsSchema>;
export type SlotRank = z.infer<typeof schema.slotRankSchema>;
export type GradePart = z.infer<typeof schema.gradePartSchema>;
export type ManagerGrade = z.infer<typeof schema.managerGradeSchema>;
export type ManagerEntry = z.infer<typeof schema.managerEntrySchema>;
export type ManagersFile = z.infer<typeof schema.managersFileSchema>;

/* The playoff odds of a roster as the site app joins them from the rankings file. The manager page reads only the
   playoff percent, so the managers package holds no rankings type. */
export type JoinedOdds = { playoff: number };

/* One entry joined with the last week of the rankings file.
   Standing is the place in the standings, 1 to 12. Rank and movement are the power rank and its move, null with no rankings row.
   Odds is null when no week has odds. Odds change is the playoff percent minus that of the week before, null when the week before has no odds. */
export type Manager = ManagerEntry & {
  standing: number;
  rank: number | null;
  movement: number | null;
  odds: JoinedOdds | null;
  odds_change: number | null;
};

/* The managers are in standings order. */
export type Managers = { season: number; through: number; managers: Manager[] };
