/**
 * The name of each part of the roster grade, for the grade popover and the Roster chapter.
 * It is a plain module, not a client module, so a server component reads the names as data.
 */
import type { GradePart } from "../schema/manager-types";

/* The name of each part of the grade, keyed by the key in the file. A new part is one more line here. */
export const PART_NAMES: Record<GradePart["key"], string> = {
  projection: "Projection Ahead",
  production: "Season Production",
  trade_value: "Trade Value",
  depth: "Depth And Holes",
};
