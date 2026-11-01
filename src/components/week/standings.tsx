/**
 * The standings: the dark chapter with one row per team, the playoff cut line after the sixth row, and the note.
 * Points always show two decimals, so the column lines up in tabular figures.
 */
import { Fragment, type ReactNode } from "react";
import { record } from "@/lib/format/format";
import { cn } from "@/lib/utils";
import type { AvatarMap, TableRow } from "@/lib/week-types";
import { avatarSrc } from "@/lib/avatar";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { managerHrefOrNull } from "@/lib/routes";
import { Who } from "@/components/parts/who";

/* Six teams make the playoffs, so the dashed cut line sits under the sixth row. */
const PLAYOFF_SPOTS = 6;

/* From the tablet tier the wide column tokens and a wider gap spread the numbers across the row. */
const GRID =
  "grid grid-cols-[var(--spacing-standings-rank)_1fr_var(--spacing-standings-record)_var(--spacing-standings-points)] tablet:grid-cols-[var(--spacing-standings-rank-wide)_1fr_var(--spacing-standings-record-wide)_var(--spacing-standings-points-wide)] items-center gap-sp-2 tablet:gap-sp-4 border-b border-rule-dark text-row leading-tight tabular-nums";

/* The W-L and points columns align right, so the numbers line up on the last digit.
   The grid draws the table, so the roles tell a screen reader it is one: a row of cells, or of column headers for the header. */
function Line({
  cells,
  header,
  className,
}: {
  cells: [ReactNode, ReactNode, ReactNode, ReactNode];
  header?: boolean;
  className?: string;
}) {
  const [rank, team, record, points] = cells;
  const role = header ? "columnheader" : "cell";
  return (
    <div role="row" className={cn(GRID, className)}>
      <span role={role}>{rank}</span>
      <span role={role}>{team}</span>
      <span role={role} className="text-right">
        {record}
      </span>
      <span role={role} className="text-right">
        {points}
      </span>
    </div>
  );
}

/* The managers href is the managers index of the season. With null the team names render as plain text. */
export function Standings({
  table,
  avatars,
  managersHref = null,
}: {
  table: TableRow[];
  avatars: AvatarMap;
  managersHref?: string | null;
}) {
  return (
    <Chapter dark reveal id="standings">
      <Label dark heading>Standings</Label>
      {/* A table holds only rows, so the cut line is a row too. Its one cell names the cut for a screen reader and shows to no one. */}
      <div role="table" aria-label="Standings">
        <Line
          header
          cells={["#", "Team", "W-L", "Pts"]}
          // cn drops the leading of the grid when a new text size follows, so the header sets it again.
          className="pt-0 pb-sp-2 text-label leading-tight tracking-caps text-on-dark-muted uppercase"
        />
        {table.map((row, i) => (
          <Fragment key={row.team.roster_id}>
            <Line
              className="py-sp-1"
              cells={[
                row.standing.rank,
                <Who
                  key="team"
                  src={avatarSrc(avatars, row.team.roster_id)}
                  name={row.team.name}
                  href={managerHrefOrNull(managersHref, row.team.roster_id)}
                />,
                record(row.standing.wins, row.standing.losses),
                // num would drop the trailing zero of 698.30, so the column keeps toFixed to line up the decimals.
                row.standing.points_for.toFixed(2),
              ]}
            />
            {i + 1 === PLAYOFF_SPOTS && (
              <div role="row" className={cn(GRID, "border-b-2 border-dashed border-red p-0")}>
                <span role="cell" className="sr-only">
                  Playoff cut
                </span>
              </div>
            )}
          </Fragment>
        ))}
      </div>
      <Blurb dark className="mt-sp-3 text-meta">
        Records include the weekly median game: every team plays its opponent and the league median each week.
      </Blurb>
    </Chapter>
  );
}
