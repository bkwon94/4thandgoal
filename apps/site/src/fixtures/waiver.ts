/**
 * The waiver file as a typed fixture for the waiver tests.
 * It is in the exact shape the pipeline writes, with real Sleeper player ids, so a change to that shape breaks the tests.
 */
import json from "./waiver.json";
import { waiverBoardSchema } from "@cpc/waiver/schema";

/* The parse runs at import, so a stale fixture fails at once. */
export const waiver = waiverBoardSchema.parse(json);
