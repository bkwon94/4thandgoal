/**
 * The types of the week page JSON that the Python build writes beside each week's images.
 * Each type is inferred from its schema in schemas/week.ts. The JSON turns int keys into strings, so maps take string roster ids.
 */
import type { z } from "zod";
import type * as s from "./schemas/week";

export type ByePlayer = z.infer<typeof s.byePlayerSchema>;
export type Team = z.infer<typeof s.teamSchema>;
export type PlayerLine = z.infer<typeof s.playerLineSchema>;
export type MatchupSide = z.infer<typeof s.matchupSideSchema>;
export type Pick = z.infer<typeof s.pickSchema>;
export type GameChanger = z.infer<typeof s.gameChangerSchema>;
export type Award = z.infer<typeof s.awardSchema>;
export type LeaderRow = z.infer<typeof s.leaderRowSchema>;
export type LeaderBoard = z.infer<typeof s.leaderBoardSchema>;
export type TradeSide = z.infer<typeof s.tradeSideSchema>;
export type Trade = z.infer<typeof s.tradeSchema>;
export type Matchup = z.infer<typeof s.matchupSchema>;
export type Median = z.infer<typeof s.medianSchema>;
export type TableRow = z.infer<typeof s.tableRowSchema>;
export type NextGame = z.infer<typeof s.nextGameSchema>;
export type Blurbs = z.infer<typeof s.blurbsSchema>;
export type AvatarMap = z.infer<typeof s.avatarMapSchema>;
export type HeadshotMap = z.infer<typeof s.headshotMapSchema>;
export type WeekPage = z.infer<typeof s.weekPageSchema>;
