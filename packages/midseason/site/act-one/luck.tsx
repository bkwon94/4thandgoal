/**
 * Schedule luck with the Schedule swap, a chapter of Act I: the luck table, most luck first, with one plain sentence
 * on the All-play record, then the swap grid and the best schedule that each team missed.
 */
import { oneDecimal } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import { fullRecord, signedOne } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import type { LuckChapter, ScheduleSwap, TeamLuck } from "../schema/midseason-types";

/* The one plain sentence on the All-play record (AT-8). */
export const ALL_PLAY_SENTENCE =
  "All-play wins count each week as a game against every other team, so they show the wins your scores earned with an average schedule.";

const HEAD = "px-sp-2 py-sp-2 text-left font-mono text-meta font-bold tracking-caps text-mute uppercase";
const CELL = "px-sp-2 py-sp-2 font-mono text-body tabular-nums whitespace-nowrap";

/* The team column stays in place while a phone scrolls the luck table, so each row keeps its name. A long name wraps on a phone. */
const LUCK_TEAM = "sticky left-0 z-10 max-w-[9rem] bg-card md:max-w-none px-sp-2 py-sp-2 text-left text-body leading-tight font-semibold";

const closeText = (team: TeamLuck) => fullRecord(team.close_wins, team.close_losses, team.close_ties);

function LuckTable({ teams }: { teams: TeamLuck[] }) {
  return (
    <Card className="overflow-x-auto p-0">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-rule">
            <th scope="col" className={cn(HEAD, "sticky left-0 z-10 bg-card")}>Team</th>
            <th scope="col" className={cn(HEAD, "text-right")}>Wins</th>
            <th scope="col" className={cn(HEAD, "text-right")}>All-play</th>
            <th scope="col" className={cn(HEAD, "text-right")}>Luck</th>
            <th scope="col" className={cn(HEAD, "text-right")}>PA</th>
            <th scope="col" className={cn(HEAD, "text-right")}>Close</th>
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr key={team.roster_id} className="border-b border-rule last:border-b-0">
              <th scope="row" className={LUCK_TEAM}>
                {team.name}
              </th>
              <td className={cn(CELL, "text-right")}>{oneDecimal(team.head_to_head_wins)}</td>
              <td className={cn(CELL, "text-right")}>{oneDecimal(team.all_play_wins)}</td>
              <td className={cn(CELL, "text-right font-bold")}>{signedOne(team.schedule_luck)}</td>
              <td className={cn(CELL, "text-right text-ink-2")}>
                {Math.round(team.points_against)} <span className="text-meta text-mute">#{team.points_against_rank}</span>
              </td>
              <td className={cn(CELL, "text-right")}>{closeText(team)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

/* The cells of the swap grid keep a narrow pad, so all 12 columns fit the column of the report on a laptop. */
const SWAP_HEAD = "px-sp-1 py-sp-2 text-center font-mono text-meta font-bold tracking-caps text-mute uppercase";
const SWAP_CELL = "px-sp-1 py-sp-1 text-center font-mono text-meta tabular-nums whitespace-nowrap";
/* The team column stays in place while a phone scrolls the grid, so each row keeps its name. */
const SWAP_TEAM = "sticky left-0 z-10 bg-card";

/* The swap grid: a row is a team, a column is a schedule, both in standings order. The diagonal is the real record. */
function SwapGrid({ swap }: { swap: ScheduleSwap }) {
  const names = new Map(swap.rows.map((row) => [row.roster_id, row.name]));
  return (
    <>
      {/* The note sits outside the box that scrolls, so a phone shows the whole note. */}
      <span id="swap-note" className="text-meta leading-tight text-ink-2">
        Each row is a team. Each column is the schedule of the team at that place in the standings.
      </span>
      <Card className="overflow-x-auto p-0">
        <table aria-label="Schedule swap" aria-describedby="swap-note" className="w-full border-collapse">
          <thead>
            <tr className="border-b border-rule">
              <th scope="col" className={cn(HEAD, SWAP_TEAM)}>Team</th>
              {swap.rows.map((row, index) => (
                <th key={row.roster_id} scope="col" className={SWAP_HEAD}>
                  <abbr title={`The schedule of ${row.name}`} className="no-underline">
                    {index + 1}
                  </abbr>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {swap.rows.map((row, index) => (
              <tr key={row.roster_id} className="border-b border-rule last:border-b-0">
                <th
                  scope="row"
                  className={cn("max-w-[10rem] truncate px-sp-2 py-sp-1 text-left text-meta leading-tight font-semibold", SWAP_TEAM)}
                >
                  <span className="font-mono text-mute">{index + 1}</span> {row.name}
                </th>
                {row.cells.map((cell) => {
                  const own = cell.schedule_of === row.roster_id;
                  return (
                    <td
                      key={cell.schedule_of}
                      title={`${row.name} with the schedule of ${names.get(cell.schedule_of) ?? ""}`}
                      className={cn(SWAP_CELL, own ? "bg-ink font-bold text-page" : "text-ink")}
                    >
                      {fullRecord(cell.wins, cell.losses, cell.ties)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </>
  );
}

/* The best schedule that each team missed, with the record it would give. */
function BestMissed({ swap }: { swap: ScheduleSwap }) {
  const names = new Map(swap.rows.map((row) => [row.roster_id, row.name]));
  return (
    <ul aria-label="Best schedule missed" className="m-0 flex list-none flex-col p-0">
      {swap.best_missed.map((missed) => (
        <li key={missed.roster_id} className="border-b border-rule py-sp-2 text-body leading-tight last:border-b-0">
          <span className="font-semibold">{names.get(missed.roster_id)}</span>
          <span className="text-ink-2"> with the schedule of {names.get(missed.schedule_of)}: </span>
          <span className="font-mono font-bold tabular-nums">{fullRecord(missed.wins, missed.losses, missed.ties)}</span>
        </li>
      ))}
    </ul>
  );
}

export function Luck({ chapter }: { chapter: LuckChapter }) {
  const { teams, swap } = chapter.facts;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb} roast={chapter.roast}>
      <p data-all-play className="m-0 max-w-measure text-lead text-ink-2">
        {ALL_PLAY_SENTENCE} Schedule luck is the real wins minus the All-play wins.
      </p>
      <LuckTable teams={teams} />
      <h4 className="m-0 mt-sp-3 text-body leading-tight font-bold">The schedule swap</h4>
      <SwapGrid swap={swap} />
      <h4 className="m-0 mt-sp-3 text-body leading-tight font-bold">The best schedule each team missed</h4>
      <BestMissed swap={swap} />
    </ReportChapter>
  );
}
