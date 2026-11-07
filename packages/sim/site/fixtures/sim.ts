/**
 * The season sim file as a typed fixture for the sim tests.
 * It is a real run of the sim of CPC 2026 week 8 in the exact shape the pipeline writes, so a change to that shape breaks the tests.
 */
import json from "./sim.json";
import { simSchema } from "../schema/sim";

/* The parse runs at import, so a stale fixture fails at once. */
export const sim = simSchema.parse(json);
