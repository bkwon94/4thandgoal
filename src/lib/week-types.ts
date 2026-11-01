/**
 * The types of the week page JSON that the Python build writes beside each week's images.
 * Each type is inferred from its schema in schemas/week.ts, which covers the whole file.
 * The JSON turns int keys into strings, so maps take string roster ids.
 */
import type { z } from "zod";
import type * as schema from "./schemas/week";

export type ByePlayer = z.infer<typeof schema.byePlayerSchema>;
export type Team = z.infer<typeof schema.teamSchema>;
export type PlayerLine = z.infer<typeof schema.playerLineSchema>;
export type MatchupSide = z.infer<typeof schema.matchupSideSchema>;
export type Pick = z.infer<typeof schema.pickSchema>;
export type GameChanger = z.infer<typeof schema.gameChangerSchema>;
export type Award = z.infer<typeof schema.awardSchema>;
export type LeaderRow = z.infer<typeof schema.leaderRowSchema>;
export type LeaderBoard = z.infer<typeof schema.leaderBoardSchema>;
export type TradeSide = z.infer<typeof schema.tradeSideSchema>;
export type Trade = z.infer<typeof schema.tradeSchema>;
export type Matchup = z.infer<typeof schema.matchupSchema>;
export type Median = z.infer<typeof schema.medianSchema>;
export type TableRow = z.infer<typeof schema.tableRowSchema>;
export type NextGame = z.infer<typeof schema.nextGameSchema>;
export type Blurbs = z.infer<typeof schema.blurbsSchema>;
export type AvatarMap = z.infer<typeof schema.avatarMapSchema>;
export type HeadshotMap = z.infer<typeof schema.headshotMapSchema>;
export type WeekPage = z.infer<typeof schema.weekPageSchema>;
