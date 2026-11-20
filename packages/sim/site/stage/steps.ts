/**
 * The timeline of the replay of the sim page: the steps of "Sim the season" and of "Sim week N", each with its hold,
 * and the result of each team in one week, which the standings flash beside a row that moves.
 */
import type { ReplaySeason, ReplayWeek } from "../replay/season";

/* One step of the replay. A step holds for `ms`, then the next step starts. The last step holds until a press. */
export type Step =
  // `index` is the week in `season.weeks` whose standings show; -1 shows the standings at the start of the sim.
  | { screen: "season"; kind: "start" | "week" | "cut"; index: number; ms: number }
  | { screen: "bracket"; round: number; decided: boolean; ms: number }
  | { screen: "champion"; ms: number }
  | { screen: "week"; kind: "before" | "games" | "after"; ms: number };

export type Screen = Step["screen"];

/* The holds in ms. A week holds long enough to read the reorder. The first bracket step holds longer, so the seeds
   land before the first round plays. A result holds through the count-up, the winner bar, and the move to the next seat. */
export const HOLD = {
  start: 900,
  week: 1500,
  cut: 1800,
  firstDraw: 1500,
  draw: 800,
  result: 2000,
  before: 700,
  games: 3400,
};

export function stepsOf(season: ReplaySeason, mode: "season" | "week"): Step[] {
  if (mode === "week") {
    return [
      { screen: "week", kind: "before", ms: HOLD.before },
      { screen: "week", kind: "games", ms: HOLD.games },
      { screen: "week", kind: "after", ms: 0 },
    ];
  }
  // With no regular week left, the playoff field is already set, so the replay starts on the bracket.
  const regular: Step[] =
    season.weeks.length === 0
      ? []
      : [
          { screen: "season", kind: "start", index: -1, ms: HOLD.start },
          ...season.weeks.map((_, index) => ({
            screen: "season" as const,
            kind: "week" as const,
            index,
            ms: HOLD.week,
          })),
          { screen: "season", kind: "cut", index: season.weeks.length - 1, ms: HOLD.cut },
        ];
  return [
    ...regular,
    ...season.rounds.flatMap((_, round) => [
      {
        screen: "bracket" as const,
        round,
        decided: false,
        ms: round === 0 ? HOLD.firstDraw : HOLD.draw,
      },
      { screen: "bracket" as const, round, decided: true, ms: HOLD.result },
    ]),
    { screen: "champion", ms: 0 },
  ];
}

/* The result of one team in one week: the head-to-head game, and the median game when the league has one. */
export type Mark = { game: "W" | "L" | "T"; median: "above" | "below" | "even" | null };

export function marksOf(week: ReplayWeek): Map<number, Mark> {
  const marks = new Map<number, Mark>();
  for (const { teams } of week.games) {
    const [a, b] = teams;
    for (const [me, them] of [
      [a, b],
      [b, a],
    ]) {
      const game = me.score === them.score ? "T" : me.score > them.score ? "W" : "L";
      const median =
        week.median === null
          ? null
          : me.score > week.median
            ? "above"
            : me.score < week.median
              ? "below"
              : "even";
      marks.set(me.roster_id, { game, median });
    }
  }
  return marks;
}
