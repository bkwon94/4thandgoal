/**
 * The injury toll, a chapter of Act I: the starter games that each team lost, most first, with its key starters
 * who missed games and the count for each one.
 */
import { count } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { ReportChapter } from "../report/report-chapter";
import type { InjuryChapter } from "../schema/midseason-types";

export function Injuries({ chapter }: { chapter: InjuryChapter }) {
  return (
    <ReportChapter id={chapter.key} title={chapter.title} note="Starter games lost" blurb={chapter.blurb}>
      <Card className="py-sp-1">
        <ol aria-label="Injury toll" className="m-0 list-none p-0">
          {chapter.facts.teams.map((team) => (
            <li
              key={team.roster_id}
              className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-baseline gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0"
            >
              <span className="font-mono text-meta text-mute tabular-nums">{String(team.rank).padStart(2, "0")}</span>
              <span className="min-w-0">
                <span className="block text-body leading-tight font-semibold">{team.name}</span>
                {team.players.length > 0 && (
                  <span className="block text-meta leading-tight text-ink-2">
                    {team.players.map((player) => `${player.name} (${player.position}) ${player.games}`).join(", ")}
                  </span>
                )}
              </span>
              <span className="font-mono text-body font-bold tabular-nums">{count(team.games, "game", "games")}</span>
            </li>
          ))}
        </ol>
      </Card>
    </ReportChapter>
  );
}
