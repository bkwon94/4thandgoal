/**
 * Reads the season sim file from public/ at build time: the odds of all runs and the stored runs that the replay plays.
 * The file sits beside the midseason file, and the publish of the report puts both live together.
 */
import { join } from "node:path";
import { simSchema } from "@cpc/sim/schema/sim";
import type { Sim } from "@cpc/sim/schema/sim-types";
import { readPublished } from "./published-file";

/* The sim file layout version this site reads. It counts apart from the other published files. */
const SCHEMA_VERSION = 1;
const FILE = "sim.json";

/* A schema change must fail the build loud, the same rule as the week reader. A season with no file gives null. */
export function loadSim(season: string): Sim | null {
  return readPublished(join(process.cwd(), "public", season, FILE), SCHEMA_VERSION, simSchema);
}
