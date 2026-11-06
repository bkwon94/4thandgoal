/**
 * Lineup choices, the first part of Quick hits in Act II: the Bench points of each team, most first, with each loss
 * that its best lineup would have won. The list shows 5 teams, then a "Show all" button.
 */
import { num } from "@cpc/design/format/format";
import { ReportCard } from "../report/report-card";
import { teamScore } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import { ShowAll } from "../report/show-all";
import type { LineupChapter, TeamLineup } from "../schema/midseason-types";

function Row({ team }: { team: TeamLineup }) {
  return (
    <li className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-baseline gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0">
      <span className="font-mono text-meta text-mute tabular-nums">{String(team.rank).padStart(2, "0")}</span>
      <span className="min-w-0">
        <span className="block text-body leading-tight font-semibold">{team.name}</span>
        {team.lost_with_better.map((lost) => (
          <span key={lost.week} className="block text-meta leading-tight text-ink-2">
            Week {lost.week}: lost to {lost.opponent} by {num(lost.margin)}. The best lineup scored {teamScore(lost.best)}.
          </span>
        ))}
      </span>
      <span className="font-mono text-body font-bold tabular-nums">{teamScore(team.bench_points)}</span>
    </li>
  );
}

export function Lineup({ chapter, level }: { chapter: LineupChapter; level?: 3 | 4 }) {
  return (
    <ReportChapter id={chapter.key} title={chapter.title} level={level} note="Bench points" blurb={chapter.blurb}>
      <ReportCard className="py-sp-1">
        <ShowAll
          label="Bench points"
          rows={chapter.facts.teams.map((team) => (
            <Row key={team.roster_id} team={team} />
          ))}
        />
      </ReportCard>
    </ReportChapter>
  );
}
