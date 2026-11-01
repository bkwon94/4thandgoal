/**
 * The types of the season rankings file that the Python build writes beside the week folders.
 * Each type is inferred from its schema in schemas/rankings.ts.
 * The file holds every week of the season, so a later trend chart needs no new file.
 */
import type { z } from "zod";
import type * as schema from "./schemas/rankings";

export type BlurbSentence = z.infer<typeof schema.blurbSentenceSchema>;
export type Components = z.infer<typeof schema.componentsSchema>;
export type Odds = z.infer<typeof schema.oddsSchema>;
export type RankingsRow = z.infer<typeof schema.rankingsRowSchema>;
export type RankingsWeek = z.infer<typeof schema.rankingsWeekSchema>;
export type Rankings = z.infer<typeof schema.rankingsSchema>;
