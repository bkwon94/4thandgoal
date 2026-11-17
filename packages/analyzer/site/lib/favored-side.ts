/**
 * The favored side of a grade: the roster that the Lean says comes out ahead, which the mesh flashes and dips toward at
 * the reveal. It reads only the Lean and the sides of the analyze document, so the motion always agrees with the call.
 */
import type { AnalyzeResponse, Lean } from "./analyze-types";

/* The Lean is the call for the asker. A yes says the asker comes out ahead, and a no says the other side does. A Gut
   call is a coin flip, so it favors no side. */
const LEANS_FOR_ASKER: Record<Lean, boolean | null> = {
  "Send it": true,
  "Lean yes": true,
  "Gut call": null,
  "Lean no": false,
  Pass: false,
};

/* The roster id of the favored side, or null when no one side is favored. A no on a trade of three or more sides says
   only that the asker loses, not which other side wins, so it favors no one side. The fairness block does not pick the
   side either, because a side that gives more can still come out ahead on the call. */
export function favoredSide(doc: AnalyzeResponse): number | null {
  const forAsker = LEANS_FOR_ASKER[doc.lean];
  if (forAsker === null) return null;
  if (forAsker) return doc.trade.asker;
  const others = doc.trade.sides.filter((side) => side.roster_id !== doc.trade.asker);
  return others.length === 1 ? others[0].roster_id : null;
}
