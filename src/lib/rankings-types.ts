/**
 * The types of the season rankings file that the Python build writes beside the week folders.
 * Each type is inferred from its schema in schemas/rankings.ts.
 */
import type { z } from "zod";
import type * as s from "./schemas/rankings";

export type BlurbSentence = z.infer<typeof s.blurbSentenceSchema>;
export type Components = z.infer<typeof s.componentsSchema>;
export type Odds = z.infer<typeof s.oddsSchema>;
export type RankingsRow = z.infer<typeof s.rankingsRowSchema>;
export type RankingsWeek = z.infer<typeof s.rankingsWeekSchema>;
export type Rankings = z.infer<typeof s.rankingsSchema>;
