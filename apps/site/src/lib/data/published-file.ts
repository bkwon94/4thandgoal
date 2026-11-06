/**
 * The shared read of a published file under public/: the check of its schema version, then the parse with its schema.
 * Each loader of lib/data/ names its own file, version, and schema, and reads through it.
 */
import { existsSync, readFileSync } from "node:fs";

/* The one method of a Zod schema that the read needs. */
type Schema<T> = { parse: (data: unknown) => T };

/* A schema change must fail the build loud, so a page never renders from keys it misreads. The version check runs
   first, so a layout change reads as a version error and not as a list of bad fields. */
export function parseVersioned<T>(file: string, version: number, schema: Schema<T>): T {
  const data = JSON.parse(readFileSync(file, "utf8")) as { schema_version?: unknown };
  if (data.schema_version !== version) {
    throw new Error(`${file} has schema_version ${String(data.schema_version)}, but this site reads schema_version ${version}.`);
  }
  return schema.parse(data);
}

/* The parsed file, or null when the file is missing. A missing file is not an error: the site ships before the pipeline
   writes the file, and a season or a week may never have one. */
export function readPublished<T>(file: string, version: number, schema: Schema<T>): T | null {
  return existsSync(file) ? parseVersioned(file, version, schema) : null;
}
