/**
 * The stage lines: the 12 short lines that cycle under the title while a grade runs.
 * One pure function builds them from the trade on the stage, so the lines never read a file, a clock, or the grade.
 */

/* A side of the trade on the stage: its team, its manager, and the players it gets. */
export type StageSide = {
  team: string;
  manager: string;
  gets: { name: string; position: string }[];
};

/* The sides of the trade in order. */
export type StageTrade = StageSide[];

/* The first and the last line are fixed. The last line closes the list once, and a loop starts again at line 2. */
const FIRST_LINE = "Weighing the sides";
const LAST_LINE = "Weighing it all together";

/* One line for each measure of the grade, in the order they show. No line says that a step is done: the analyze call
   reports no progress, so a line that claimed a step would be false. */
const GENERAL_LINES = [
  "Checking roster fit",
  "Reading the standings",
  "Looking at the schedule ahead",
  "Reading recent usage",
  "Checking the injury report",
  "Sizing up the upside",
  "Following the playoff race",
];

/* The middle ten lines hold general lines (G) and lines with a name (N). The pattern keeps a name near the top of the
   list, so a short wait still shows one, and it spreads the names so no two sit side by side. */
const PATTERN = "GNGGNGNGNG";

/* Each name shape takes the side and a counter, and gives a line or null when the side has no player to name. */
const NAME_SHAPES: ((side: StageSide, round: number) => string | null)[] = [
  (side, round) => (side.gets.length > 0 ? `Reading ${side.gets[round % side.gets.length].name}'s season` : null),
  (side, round) => (side.gets.length > 0 ? `Checking ${side.team}'s depth at ${side.gets[round % side.gets.length].position}` : null),
  (side) => `Weighing what ${side.manager} gives up`,
];

/* The lines with a name, in turn across the sides, so each side shows before one repeats. A shape with nothing to name
   is skipped, and a repeat is dropped, so a trade of two players still gives enough distinct lines. */
function namedLines(trade: StageTrade): string[] {
  const lines = new Set<string>();
  for (let k = 0; k < 4 * trade.length * NAME_SHAPES.length; k++) {
    const line = NAME_SHAPES[k % NAME_SHAPES.length](trade[k % trade.length], Math.floor(k / trade.length));
    if (line) lines.add(line);
  }
  return [...lines];
}

/* The 12 lines of a trade. Line 1 and line 12 are fixed, and the ten between mix general lines with named lines. */
export function stageLines(trade: StageTrade): string[] {
  const named = namedLines(trade).slice(0, PATTERN.split("N").length - 1);
  const general = [...GENERAL_LINES];
  const middle = [...PATTERN].map((slot) => {
    const line = slot === "N" ? (named.shift() ?? general.shift()) : (general.shift() ?? named.shift());
    return line ?? "";
  });
  return [FIRST_LINE, ...middle, LAST_LINE];
}
