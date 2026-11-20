/**
 * The injury toll, the second part of Quick hits in Act II: the starter games that each team lost, most first, with
 * its key starters who missed games and the count for each one.
 */
import { count } from "@cpc/design/format/format";
import { ReportCard } from "../report/report-card";
import { ReportChapter } from "../report/report-chapter";
import type { InjuryChapter } from "../schema/midseason-types";

export function Injuries({ chapter, level }: { chapter: InjuryChapter; level?: 3 | 4 }) {
  return (
    <ReportChapter
      id={chapter.key}
      title={chapter.title}
      level={level}
      note="Starter games lost"
      blurb={chapter.blurb}
    >
      <ReportCard className="py-sp-1">
        <ol aria-label="Injury toll" className="m-0 list-none p-0">
          {chapter.facts.teams.map((team) => (
            <li
              key={team.roster_id}
              className="gap-x-sp-3 border-rule py-sp-2 grid grid-cols-[auto_minmax(0,1fr)_auto] items-baseline border-b last:border-b-0"
            >
              <span className="text-meta text-mute font-mono tabular-nums">
                {String(team.rank).padStart(2, "0")}
              </span>
              <span className="min-w-0">
                <span className="text-body block leading-tight font-semibold">{team.name}</span>
                {team.players.length > 0 && (
                  <span className="text-meta text-ink-2 block leading-tight">
                    {team.players
                      .map((player) => `${player.name} (${player.position}) ${player.games}`)
                      .join(", ")}
                  </span>
                )}
              </span>
              <span className="text-body font-mono font-bold tabular-nums">
                {count(team.games, "game", "games")}
              </span>
            </li>
          ))}
        </ol>
      </ReportCard>
    </ReportChapter>
  );
}
