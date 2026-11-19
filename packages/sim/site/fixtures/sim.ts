/**
 * The sim files as typed fixtures for the sim tests: the season file of CPC week 8, and the week files of CPC and NorCal week 10.
 * Each is a real run of the sim in the exact shape the pipeline writes, so a change to that shape breaks the tests.
 */
import json from "./sim.json";
import weekJson from "./week-sim.json";
import norcalWeekJson from "./week-sim-norcal.json";
import { simSchema, weekSimSchema } from "../schema/sim";

/* The parse runs at import, so a stale fixture fails at once. */
export const sim = simSchema.parse(json);

/* CPC 2026 week 10, a league with the median game. */
export const weekSim = weekSimSchema.parse(weekJson);

/* NorCal 2026 week 10, a league with no median game. */
export const norcalWeekSim = weekSimSchema.parse(norcalWeekJson);
