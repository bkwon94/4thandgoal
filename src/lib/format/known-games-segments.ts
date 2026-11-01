/**
 * The stats-through segments of the as-of line, shared by the analyze page and the finder page.
 * The first segment names the stats week, the known games, and the games in progress. Each pending count is its own segment.
 */
import type { AsOf } from "@/lib/analyze-types";

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/* A document with no block, or no games read, gets the stats week alone, so the line never claims games it lacks. */
export function knownGamesSegments(asOf: AsOf): string[] {
  const known = asOf.known_games;
  if (!known || known.games === 0) return [`Stats through week ${asOf.stats_through}`];

  // On a game day the stats cover the played games of the trade week, so the base stops one week earlier. Counting both would count that week twice.
  const stats = `Stats through week ${asOf.completed_through ?? asOf.stats_through - 1}`;

  const inProgress = known.in_progress > 0 ? `, ${known.in_progress} in progress` : "";
  const pending = Object.entries(known.pending).map(
    ([name, n]) => `${name.charAt(0).toUpperCase()}${name.slice(1)} pending for ${plural(n, "game")}`,
  );
  return [`${stats}, plus ${plural(known.games, `week ${known.week} game`)}${inProgress}`, ...pending];
}
