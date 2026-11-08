/**
 * The race group of a team for the chips of the Index list: In, Bubble, or Out, from its playoff odds and its status word.
 * In is clinched or odds of 75% or more. Bubble is 25% to 75%. Out is eliminated or under 25%.
 */
import type { JoinedOdds } from "../schema/manager-types";

export type RaceGroup = "in" | "bubble" | "out";

/* The race word of each group. The chips of the Index list and the eyebrow of the stage both use it, so they say one word. */
export const RACE_WORDS: Record<RaceGroup, string> = { in: "In", bubble: "Bubble", out: "Out" };

/* The lowest odds of In and of Bubble, in whole percents. 75% is In and 25% is Bubble, so each edge has one group. */
const IN_FROM = 75;
const BUBBLE_FROM = 25;

/* The status word wins over the odds: a clinched team is In and an eliminated team is Out at any percent.
   A team with no odds, as in a week before the odds engine runs, has no group and shows only under All. */
export function raceGroup(odds: Pick<JoinedOdds, "playoff" | "status"> | null): RaceGroup | null {
  if (odds === null) return null;
  if (odds.status === "in") return "in";
  if (odds.status === "out") return "out";
  if (odds.playoff >= IN_FROM) return "in";
  return odds.playoff >= BUBBLE_FROM ? "bubble" : "out";
}
