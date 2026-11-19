/**
 * The types of the sim files that the Python build writes: the season file and the week file with its pages.
 * Each type is inferred from its schema in sim.ts.
 */
import type { z } from "zod";
import type * as schema from "./sim";

export type SimRun = z.infer<typeof schema.simRunSchema>;
export type TeamSim = z.infer<typeof schema.teamSimSchema>;
export type Sim = z.infer<typeof schema.simSchema>;
export type SimPage = z.infer<typeof schema.simPageSchema>;
export type WeekSim = z.infer<typeof schema.weekSimSchema>;
export type Playoffs = z.infer<typeof schema.playoffsSchema>;
