/**
 * The weight of each part of the roster grade, in percent of the grade, for the Grade dial.
 * managers.json does not carry the weights, so the site holds a copy, and grade-weights.test.ts compares it to the pipeline.
 */
import type { GradePart } from "../schema/manager-types";

/* The same values as GRADE_WEIGHTS in packages/managers/python/src/managers/tunables.py. They sum to 100. */
export const GRADE_WEIGHTS: Record<GradePart["key"], number> = {
  projection: 45,
  production: 30,
  trade_value: 10,
  depth: 15,
};
