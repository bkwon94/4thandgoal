/**
 * The types of the waiver.json file that the Python build writes beside page.json in a week folder.
 * Each type is inferred from its schema in schemas/waiver.ts. The bucket keys sit here because they are not a file shape.
 */
import type { z } from "zod";
import type * as s from "./schemas/waiver";

export type BoardScores = z.infer<typeof s.boardScoresSchema>;
export type WaiverFact = z.infer<typeof s.waiverFactSchema>;
export type LastLike = z.infer<typeof s.lastLikeSchema>;
export type WaiverPrice = z.infer<typeof s.waiverPriceSchema>;
export type ClaimStance = z.infer<typeof s.claimStanceSchema>;
export type ResearchClaim = z.infer<typeof s.researchClaimSchema>;
export type DropInfo = z.infer<typeof s.dropInfoSchema>;
export type WaiverPlayer = z.infer<typeof s.waiverPlayerSchema>;
export type BudgetRow = z.infer<typeof s.budgetRowSchema>;
export type WaiverBoard = z.infer<typeof s.waiverBoardSchema>;

/* The best adds bucket is the one key every file has. Later builds add more buckets by key. */
export const BEST_ADDS = "best_adds";

/* The five bucket keys in tab order, with the tab names. A file can lack any bucket but best adds.
   The names are short, so the five tabs fit in one row at 390. */
export const BUCKETS = [
  { key: BEST_ADDS, name: "Best" },
  { key: "trending", name: "Trending" },
  { key: "sneaky", name: "Sneaky" },
  { key: "stashes", name: "Stash" },
  { key: "drops", name: "Drops" },
] as const;

/* The key of one of the five buckets. */
export type BucketKey = (typeof BUCKETS)[number]["key"];
