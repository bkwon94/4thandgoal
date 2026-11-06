/**
 * The beats of a replay in the Broadcast motion (decision 13 of midseason-report): each regular week, the split,
 * the final standings, the draw and the result of each bracket round, then the champion. Each beat holds for its time.
 */
import type { ReplaySeason } from "./season";

export type Beat =
  | { kind: "week"; index: number; ms: number }
  | { kind: "split"; index: 0; ms: number }
  | { kind: "final"; index: 0; ms: number }
  | { kind: "draw"; index: number; ms: number }
  | { kind: "result"; index: number; ms: number }
  | { kind: "champion"; index: 0; ms: number };

/* The hold of each beat in ms. Six weeks, the split, three rounds, and the champion give a run of about 20 s.
   A beat runs longer than a control may, because the replay explains and the reader watches it (decision 13). */
const HOLD = { week: 1500, split: 1800, final: 1400, draw: 1000, result: 1800, champion: 0 } as const;

export function beatsOf(season: ReplaySeason): Beat[] {
  return [
    ...season.weeks.map((_, index) => ({ kind: "week" as const, index, ms: HOLD.week })),
    { kind: "split", index: 0, ms: HOLD.split },
    { kind: "final", index: 0, ms: HOLD.final },
    ...season.rounds.flatMap((_, index) => [
      { kind: "draw" as const, index, ms: HOLD.draw },
      { kind: "result" as const, index, ms: HOLD.result },
    ]),
    { kind: "champion", index: 0, ms: HOLD.champion },
  ];
}

/* The time from the press to the champion, in ms. */
export function runLength(beats: Beat[]): number {
  return beats.reduce((total, beat) => total + beat.ms, 0);
}
