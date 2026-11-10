/**
 * Types for the analyze document that the site API returns from POST /analyze.
 * Each type is inferred from its schema in schemas/api.ts, which holds the comment of each field.
 */
import type { z } from "zod";
import type * as schema from "./schemas/api";

export type Player = z.infer<typeof schema.playerSchema>;
export type TradedPlayer = z.infer<typeof schema.tradedPlayerSchema>;
export type GivenPlayer = z.infer<typeof schema.givenPlayerSchema>;
export type GotPlayer = z.infer<typeof schema.gotPlayerSchema>;
export type TradeSide = z.infer<typeof schema.tradeSideSchema>;
export type Lean = z.infer<typeof schema.leanSchema>;
export type Mark = z.infer<typeof schema.markSchema>;
export type Bullet = z.infer<typeof schema.bulletSchema>;
export type WeekLine = z.infer<typeof schema.weekLineSchema>;
export type ReadSide = z.infer<typeof schema.readSideSchema>;
export type FairnessSide = z.infer<typeof schema.fairnessSideSchema>;
export type Fairness = z.infer<typeof schema.fairnessSchema>;
export type KnownGames = z.infer<typeof schema.knownGamesSchema>;
export type AsOf = z.infer<typeof schema.asOfSchema>;
export type AnalyzeResponse = z.infer<typeof schema.analyzeResponseSchema>;
export type FinderTrade = z.infer<typeof schema.finderTradeSchema>;
export type FindResponse = z.infer<typeof schema.findResponseSchema>;
