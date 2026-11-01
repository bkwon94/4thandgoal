/**
 * The managers file as a typed fixture for the manager tests.
 * It is in the exact shape the pipeline writes, so a change to that shape breaks the tests.
 */
import json from "./managers.json";
import { managersFileSchema } from "@/lib/schemas/managers";

/* The parse runs at import, so a stale fixture fails at once. */
export const managers = managersFileSchema.parse(json);
