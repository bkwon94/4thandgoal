/**
 * The types of the season sim file that the Python build writes beside the week folders.
 * Each type is inferred from its schema in sim.ts.
 */
import type { z } from "zod";
import type * as schema from "./sim";

export type SimRun = z.infer<typeof schema.simRunSchema>;
export type TeamSim = z.infer<typeof schema.teamSimSchema>;
export type Sim = z.infer<typeof schema.simSchema>;
