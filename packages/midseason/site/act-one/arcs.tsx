/**
 * The arcs chapter of Act I: each team's arcs, such as a Turnaround or a Collapse, with the numbers behind each one.
 * A team has at most 2 arcs, the biggest swing first, and a team with no arc says so.
 */
import { Card } from "@cpc/design/parts/card";
import { Tag } from "@cpc/design/parts/tag";
import { fullRecord, signedOne } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import type { Arc, ArcsChapter, WindowRecord } from "../schema/midseason-types";

const windowText = (label: string, window: WindowRecord) =>
  `${label} weeks ${window.first_week} to ${window.last_week}: ${fullRecord(window.wins, window.losses, window.ties)}`;

/* The numbers behind one arc. Each arc fills only the numbers that it reads, so each line shows only when it is there. */
export function arcNumbers(arc: Arc): string[] {
  const lines: string[] = [];
  if (arc.start) lines.push(windowText("Start,", arc.start));
  if (arc.now) lines.push(windowText("Now,", arc.now));
  if (arc.win_streak !== null) lines.push(`Longest win streak: ${arc.win_streak}`);
  if (arc.loss_streak !== null) lines.push(`Longest loss streak: ${arc.loss_streak}`);
  if (arc.schedule_luck !== null) lines.push(`Schedule luck: ${signedOne(arc.schedule_luck)} wins`);
  return lines;
}

export function Arcs({ chapter }: { chapter: ArcsChapter }) {
  return (
    <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb} roast={chapter.roast}>
      <ul aria-label="Arcs" className="m-0 grid list-none grid-cols-1 gap-sp-2 p-0 desktop:grid-cols-2">
        {chapter.facts.teams.map((team) => (
          <Card as="li" key={team.roster_id} className="flex flex-col gap-sp-2">
            <span className="text-body leading-tight font-bold">{team.name}</span>
            {team.arcs.length === 0 && <span className="text-meta text-mute">No arc yet</span>}
            {team.arcs.map((arc) => (
              <div key={arc.kind} className="flex flex-col gap-sp-1">
                <Tag className="ml-0 w-fit text-meta">{arc.kind}</Tag>
                {arcNumbers(arc).map((line) => (
                  <span key={line} className="font-mono text-meta leading-tight text-ink-2 tabular-nums">
                    {line}
                  </span>
                ))}
              </div>
            ))}
          </Card>
        ))}
      </ul>
    </ReportChapter>
  );
}
