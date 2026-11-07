/**
 * The season midseason file as a typed fixture for the midseason tests.
 * It is a real build of CPC 2026 week 8 in the exact shape the pipeline writes, so a change to that shape breaks the tests.
 */
import json from "./midseason.json";
import { midseasonSchema } from "../schema/midseason";

/* The parse runs at import, so a stale fixture fails at once. */
export const midseason = midseasonSchema.parse(json);
