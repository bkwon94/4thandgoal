/**
 * The standings: one row per team with its avatar, a playoff tick, the record, and the points, and a brand line under
 * the last playoff spot. Points always show two decimals, so the column lines up in tabular figures.
 */
import { record } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import type { AvatarMap, TableRow } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import { WeekChapter } from "../parts/week-chapter";

/* Six teams make the playoffs, so the brand line sits under the sixth row. */
const PLAYOFF_SPOTS = 6;

/* The columns of a row: the tick, the rank, the avatar, the name, the record, and the points. */
const ROW =
  "grid min-h-touch grid-cols-[auto_auto_auto_minmax(0,1fr)_auto_auto] items-center gap-sp-2 py-sp-1 text-inherit no-underline";

function Row({ row, avatars, href }: { row: TableRow; avatars: AvatarMap; href: string | null }) {
  const playoff = row.standing.rank <= PLAYOFF_SPOTS;
  const content = (
    <>
      {/* The tick is a graphic. The words after the name say it for a screen reader. */}
      <span aria-hidden="true" className={cn("h-sp-5 w-sp-1 rounded-pill", playoff ? "bg-accent" : "bg-raised")} />
      <span className="font-mono text-meta text-mute tabular-nums">{String(row.standing.rank).padStart(2, "0")}</span>
      <Avatar src={avatarSrc(avatars, row.team.roster_id)} />
      <span className="truncate text-body leading-tight font-semibold">
        {row.team.name}
        {playoff && <span className="sr-only">, playoff spot</span>}
      </span>
      <span className="text-right font-mono text-body font-bold tabular-nums">
        {record(row.standing.wins, row.standing.losses)}
      </span>
      {/* num would drop the trailing zero of 698.30, so the column keeps toFixed to line up the decimals. */}
      <span className="min-w-[7ch] text-right font-mono text-meta text-mute tabular-nums">
        {row.standing.points_for.toFixed(2)}
      </span>
    </>
  );
  return href === null ? (
    <div className={ROW}>{content}</div>
  ) : (
    <a href={href} className={cn(ROW, "press")}>
      {content}
    </a>
  );
}

/* The managers href is the managers index of the season. With null the rows are plain text.
   The note about the median game shows only for a league that plays one, so a league without it has no false note. */
export function Standings({
  table,
  avatars,
  managersHref = null,
  hasMedianGame = true,
}: {
  table: TableRow[];
  avatars: AvatarMap;
  managersHref?: string | null;
  hasMedianGame?: boolean;
}) {
  return (
    <WeekChapter id="standings" title="Standings" note={`Playoff line after ${PLAYOFF_SPOTS}th`}>
      <Card className="py-sp-1">
        <ol aria-label="Standings" className="m-0 list-none p-0">
          {table.map((row) => {
            const cut = row.standing.rank === PLAYOFF_SPOTS;
            return (
              <li
                key={row.team.roster_id}
                data-cut={cut ? "" : undefined}
                className={cn("border-b last:border-b-0", cut ? "border-b-2 border-accent" : "border-rule")}
              >
                <Row row={row} avatars={avatars} href={managerHrefOrNull(managersHref, row.team.roster_id)} />
              </li>
            );
          })}
        </ol>
      </Card>
      {hasMedianGame && (
        <div className="text-meta leading-body text-mute">
          Records include the weekly median game: every team plays its opponent and the league median each week.
        </div>
      )}
    </WeekChapter>
  );
}
