/**
 * The types of the waiver.json file that the Python build writes beside page.json in a week folder.
 * Each type is inferred from its schema in schemas/waiver.ts. The bucket keys sit here because they are not a file shape.
 * A key that an older build may leave out is optional, so the site reads every file the pipeline wrote.
 */
import type { z } from "zod";
import type * as schema from "./schemas/waiver";

export type BoardScores = z.infer<typeof schema.boardScoresSchema>;
export type WaiverFact = z.infer<typeof schema.waiverFactSchema>;
export type LastLike = z.infer<typeof schema.lastLikeSchema>;
export type WaiverPrice = z.infer<typeof schema.waiverPriceSchema>;
export type ClaimStance = z.infer<typeof schema.claimStanceSchema>;
export type ResearchClaim = z.infer<typeof schema.researchClaimSchema>;
export type DropInfo = z.infer<typeof schema.dropInfoSchema>;
export type WaiverPlayer = z.infer<typeof schema.waiverPlayerSchema>;
export type BudgetRow = z.infer<typeof schema.budgetRowSchema>;
export type WaiverBoard = z.infer<typeof schema.waiverBoardSchema>;

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
