/**
 * The read of a finder card as an analyze document, so a tap on a card opens the trade in the analyzer already graded.
 * The find route sends the Lean, the Case, and the Bullets of each pick, so the open makes no second grade.
 */
import type { AnalyzeResponse, FindResponse, FinderTrade } from "./analyze-types";

/* The analyze document of one card. The Bullets of a pick speak to the asker, so they go on the side of the asker, and
   each other side keeps an empty read, so the stage still shows every team. A pick has no Week line and no fairness
   read, so the document has none. A trade of a fallback has no Lean, so it has no read, and the caller grades it. */
export function finderRead(trade: FinderTrade, doc: FindResponse): AnalyzeResponse | null {
  if (trade.lean === null || trade.case === null) return null;
  const asker = doc.trade_pair.asker.roster_id;
  return {
    trade: { asker, sides: trade.sides },
    lean: trade.lean,
    case: trade.case,
    sides: trade.sides.map((side) => ({ roster_id: side.roster_id, bullets: side.roster_id === asker ? trade.bullets : [], week_lines: [] })),
    as_of: doc.as_of,
    missing: doc.missing,
    stale: doc.stale,
  };
}
