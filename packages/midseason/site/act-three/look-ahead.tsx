/**
 * The look ahead, the first chapter of Act III: each team's games left in the regular season with the record of each
 * opponent, and the win rate of all its opponents. The softest schedule comes first. The list shows 5 teams first.
 */
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import { Tag } from "@cpc/design/parts/tag";
import { fullRecord } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import { ShowAll } from "../report/show-all";
import type { LookAheadChapter, TeamLookAhead } from "../schema/midseason-types";

/* A win rate in the box-score form, such as ".440", or "1.000" for a perfect rate. */
export const rateText = (rate: number) => (rate >= 1 ? "1.000" : `.${String(Math.round(rate * 1000)).padStart(3, "0")}`);

function Row({ team, end }: { team: TeamLookAhead; end: "Softest" | "Hardest" | null }) {
  return (
    <li className="flex flex-col gap-sp-2 border-b border-rule py-sp-3 last:border-b-0">
      <span className="flex flex-wrap items-baseline justify-between gap-x-sp-3">
        <span className="text-body leading-tight font-bold">
          {team.name}
          {end !== null && <Tag className="text-meta">{end}</Tag>}
        </span>
        {team.opponents_rate !== null && (
          <span className="font-mono text-meta text-ink-2 tabular-nums">
            Opponents <span className="font-bold text-ink">{rateText(team.opponents_rate)}</span>
          </span>
        )}
      </span>
      <ol
        aria-label={`Games left of ${team.name}`}
        className="m-0 grid list-none grid-cols-2 gap-sp-1 p-0 tablet:grid-cols-3 desktop:grid-cols-6"
      >
        {team.games.map((game) => {
          const good = game.wins > game.losses;
          return (
            <li
              key={game.week}
              data-week={game.week}
              className={cn(
                "flex flex-col rounded-sm border px-sp-2 py-sp-1 text-meta leading-tight",
                good ? "border-ink" : "border-rule",
              )}
            >
              <span className="font-mono text-mute">Week {game.week}</span>
              <span className="truncate font-semibold">{game.name}</span>
              <span className="font-mono text-ink-2 tabular-nums">{fullRecord(game.wins, game.losses, game.ties)}</span>
            </li>
          );
        })}
      </ol>
    </li>
  );
}

export function LookAhead({ chapter }: { chapter: LookAheadChapter }) {
  const { teams, softest, hardest } = chapter.facts;
  const endOf = (rosterId: number) => (rosterId === softest ? "Softest" : rosterId === hardest ? "Hardest" : null);
  const weeks = teams[0]?.games ?? [];
  const note = weeks.length > 0 ? `Weeks ${weeks[0].week} to ${weeks[weeks.length - 1].week}` : undefined;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} note={note} blurb={chapter.blurb} roast={chapter.roast}>
      <p className="m-0 max-w-measure text-lead text-ink-2">
        The rate is the win rate of the opponents so far. A lower rate is a softer path.
      </p>
      <Card className="py-sp-1">
        <ShowAll
          label="Schedules left"
          rows={teams.map((team) => (
            <Row key={team.roster_id} team={team} end={endOf(team.roster_id)} />
          ))}
        />
      </Card>
    </ReportChapter>
  );
}
