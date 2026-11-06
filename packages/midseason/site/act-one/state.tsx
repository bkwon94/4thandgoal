/**
 * The state of the league, the first chapter of Act I: each team's full record, points for and against, the streak,
 * and the playoff odds, in standings order. The table scrolls inside its own box on a phone.
 */
import { num } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import { fullRecord } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import type { StateChapter, TeamState } from "../schema/midseason-types";

/* Six teams make the playoffs, so the brand line sits under the sixth row. */
const PLAYOFF_SPOTS = 6;

const HEAD = "px-sp-2 py-sp-2 text-left font-mono text-meta font-bold tracking-caps text-mute uppercase";
const CELL = "px-sp-2 py-sp-2 font-mono text-body tabular-nums whitespace-nowrap";

const streakText = (team: TeamState) => (team.streak ? `${team.streak.kind}${team.streak.length}` : "–");

export function State({ chapter }: { chapter: StateChapter }) {
  return (
    <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb} roast={chapter.roast}>
      <Card className="overflow-x-auto p-0">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-rule">
              <th scope="col" className={HEAD}>#</th>
              <th scope="col" className={HEAD}>Team</th>
              <th scope="col" className={cn(HEAD, "text-right")}>Record</th>
              <th scope="col" className={cn(HEAD, "text-right")}>PF</th>
              <th scope="col" className={cn(HEAD, "text-right")}>PA</th>
              <th scope="col" className={cn(HEAD, "text-right")}>Streak</th>
              <th scope="col" className={cn(HEAD, "text-right")}>Playoff</th>
            </tr>
          </thead>
          <tbody>
            {chapter.facts.teams.map((team) => (
              <tr
                key={team.roster_id}
                className={cn("border-b last:border-b-0", team.rank === PLAYOFF_SPOTS ? "border-b-2 border-accent" : "border-rule")}
              >
                <td className={cn(CELL, "text-meta text-mute")}>{String(team.rank).padStart(2, "0")}</td>
                <th scope="row" className="px-sp-2 py-sp-2 text-left text-body leading-tight font-semibold">
                  {team.name}
                </th>
                <td className={cn(CELL, "text-right font-bold")}>{fullRecord(team.wins, team.losses, team.ties)}</td>
                <td className={cn(CELL, "text-right")}>{num(team.points_for)}</td>
                <td className={cn(CELL, "text-right text-ink-2")}>{num(team.points_against)}</td>
                <td className={cn(CELL, "text-right")}>{streakText(team)}</td>
                <td className={cn(CELL, "text-right")}>{team.playoff_odds === null ? "–" : `${team.playoff_odds}%`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </ReportChapter>
  );
}
