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
export type Decision = z.infer<typeof schema.decisionSchema>;
export type Factor = z.infer<typeof schema.factorSchema>;
export type DecidedSide = z.infer<typeof schema.decidedSideSchema>;
export type FairnessSide = z.infer<typeof schema.fairnessSideSchema>;
export type Fairness = z.infer<typeof schema.fairnessSchema>;
export type KnownGames = z.infer<typeof schema.knownGamesSchema>;
export type AsOf = z.infer<typeof schema.asOfSchema>;
export type AnalyzeResponse = z.infer<typeof schema.analyzeResponseSchema>;
export type FinderTrade = z.infer<typeof schema.finderTradeSchema>;
export type FindResponse = z.infer<typeof schema.findResponseSchema>;
