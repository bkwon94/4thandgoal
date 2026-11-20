/**
 * Reads the shard of a Playwright run from the env value PLAYWRIGHT_SHARD, such as "2/4".
 * CI sets it in each job of the matrix, so each Playwright run of the browser check takes only its own part of the tests.
 */

/* The shard as { current, total }, or null when the value is not set, so a local run takes every test. A value that names
   no shard stops the run, because a bad value would make each job of the matrix run every test. */
export function shardOfEnv(value) {
  if (value === undefined || value === "") return null;
  const match = /^(\d+)\/(\d+)$/.exec(value);
  const current = match ? Number(match[1]) : 0;
  const total = match ? Number(match[2]) : 0;
  if (current < 1 || current > total) {
    throw new Error(`PLAYWRIGHT_SHARD must be <current>/<total>, with 1 <= current <= total, not "${value}".`);
  }
  return { current, total };
}
