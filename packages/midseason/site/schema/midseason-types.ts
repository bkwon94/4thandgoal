/**
 * The types of the season midseason file that the Python build writes beside the week folders.
 * Each type is inferred from its schema in midseason.ts.
 */
import type { z } from "zod";
import type * as schema from "./midseason";

export type Blurb = z.infer<typeof schema.blurbSchema>;
export type Opener = z.infer<typeof schema.openerSchema>;
export type TeamState = z.infer<typeof schema.teamStateSchema>;
export type StateChapter = z.infer<typeof schema.stateChapterSchema>;
export type WindowRecord = z.infer<typeof schema.windowRecordSchema>;
export type Arc = z.infer<typeof schema.arcSchema>;
export type ArcsChapter = z.infer<typeof schema.arcsChapterSchema>;
export type TeamLuck = z.infer<typeof schema.teamLuckSchema>;
export type ScheduleSwap = z.infer<typeof schema.scheduleSwapSchema>;
export type LuckChapter = z.infer<typeof schema.luckChapterSchema>;
export type InjuryChapter = z.infer<typeof schema.injuryChapterSchema>;
export type TopPlayer = z.infer<typeof schema.topPlayerSchema>;
export type PositionBoard = z.infer<typeof schema.positionBoardSchema>;
export type Top10Chapter = z.infer<typeof schema.top10ChapterSchema>;
export type DraftRow = z.infer<typeof schema.draftRowSchema>;
export type DraftChapter = z.infer<typeof schema.draftChapterSchema>;
export type Pickup = z.infer<typeof schema.pickupSchema>;
export type WaiversChapter = z.infer<typeof schema.waiversChapterSchema>;
export type TradeCard = z.infer<typeof schema.tradeCardSchema>;
export type TradesChapter = z.infer<typeof schema.tradesChapterSchema>;
export type TeamLineup = z.infer<typeof schema.teamLineupSchema>;
export type LineupChapter = z.infer<typeof schema.lineupChapterSchema>;
export type Game = z.infer<typeof schema.gameSchema>;
export type Award = z.infer<typeof schema.awardSchema>;
export type RecordsChapter = z.infer<typeof schema.recordsChapterSchema>;
export type TeamLookAhead = z.infer<typeof schema.teamLookAheadSchema>;
export type LookAheadChapter = z.infer<typeof schema.lookAheadChapterSchema>;
export type GapPlayer = z.infer<typeof schema.gapPlayerSchema>;
export type GrabPlayer = z.infer<typeof schema.grabPlayerSchema>;
export type WatchChapter = z.infer<typeof schema.watchChapterSchema>;
export type MidseasonChapter =z.infer<typeof schema.chapterSchema>;
export type Act = z.infer<typeof schema.actSchema>;
export type Midseason = z.infer<typeof schema.midseasonSchema>;
