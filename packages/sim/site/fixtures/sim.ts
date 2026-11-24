/**
 * The sim files as typed fixtures for the sim tests: the season file of CPC week 8, the week files of CPC and NorCal week 10,
 * and the playoff fixtures of CPC.
 * Each is a real run of the sim in the exact shape the pipeline writes, so a change to that shape breaks the tests.
 */
import json from "./sim.json";
import weekJson from "./week-sim.json";
import norcalWeekJson from "./week-sim-norcal.json";
import playoffsJson from "./week-sim-playoffs.json";
import roundTwoJson from "./week-sim-round-2.json";
import finalJson from "./week-sim-final.json";
import weekElevenJson from "./week-sim-week-11.json";
import { simSchema, weekSimSchema } from "../schema/sim";

/* The parse runs at import, so a stale fixture fails at once. */
export const sim = simSchema.parse(json);

/* CPC 2026 week 10, a league with the median game. */
export const weekSim = weekSimSchema.parse(weekJson);

/* CPC 2026 week 11, the week of The Race acceptance tests: 3 weeks left, and Bo Girds at 11-11. */
export const weekElevenSim = weekSimSchema.parse(weekElevenJson);

/* NorCal 2026 week 10, a league with no median game. */
export const norcalWeekSim = weekSimSchema.parse(norcalWeekJson);

/* The playoff fixtures of ACCEPTANCE.md, from `make sim-fixtures`: CPC week 10 with the later weeks played as stored run 1. */
/* After week 14: the bracket of week 15 set, and the top 2 seeds on a bye. */
export const playoffsWeekSim = weekSimSchema.parse(playoffsJson);

/* After week 15: round 1 played, and the games of week 16 set. */
export const roundTwoWeekSim = weekSimSchema.parse(roundTwoJson);

/* After week 17: the final bracket and the champion. */
export const finalWeekSim = weekSimSchema.parse(finalJson);
