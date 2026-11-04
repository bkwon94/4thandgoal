/**
 * The position leaders: one card per position with the top started players, then the blurb.
 * At phone width each row keeps one line; the tablet tier and up put two cards per row.
 */
import { num } from "@/lib/format/format";
import { cn } from "@/lib/utils";
import type { HeadshotMap, LeaderBoard, LeaderRow } from "@/lib/week-types";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Headshot } from "@/components/parts/headshot";
import { headshotSrc } from "@/lib/headshot";
import { Label } from "@/components/parts/label";

/* One line per row: rank, player, fantasy team, points. The player keeps its width first; the team takes what is left
   and truncates, so the points never leave the row. On a wide screen a half-width card drops the team under the player,
   but a spanned card is as wide as a phone card, so it keeps the one-line row. */
function Row({ row, headshots, wide }: { row: LeaderRow; headshots: HeadshotMap; wide: boolean }) {
  return (
    <li
      className={cn(
        "flex items-baseline gap-sp-2 border-t border-rule py-sp-1 tabular-nums first:border-t-0",
        wide && "tablet:grid tablet:grid-cols-[auto_minmax(0,1fr)_auto] tablet:gap-x-sp-2 tablet:gap-y-sp-0",
      )}
    >
      <span className="flex-none text-meta font-bold text-mute">{row.rank}</span>
      <span
        className={cn(
          "min-w-0 flex-[0_1_auto] overflow-hidden text-ellipsis whitespace-nowrap",
          wide && "tablet:col-start-2 tablet:row-start-1",
        )}
      >
        {/* The row headshot stays near the text height, so the row keeps about the height of a plain text row. */}
        <Headshot
          src={headshotSrc(headshots, row.player_id)}
          lazy
          className="flex-none object-cover mr-sp-2 inline-block size-sp-5 rounded-full align-middle"
        />
        <b>{row.player}</b>
        {row.nfl_team && (
          <>
            {" "}
            <small className="text-meta text-mute">{row.nfl_team}</small>
          </>
        )}
      </span>
      <span
        className={cn(
          "min-w-0 flex-[1_1_0] overflow-hidden text-meta text-ellipsis whitespace-nowrap text-mute",
          wide && "tablet:col-start-2 tablet:row-start-2",
        )}
      >
        {row.team}
      </span>
      {/* The points are the stat a reader scans for, so they take the body size and the heaviest weight in the row. */}
      <span className={cn("flex-none text-body font-extrabold", wide && "tablet:col-start-3 tablet:row-start-1")}>
        {num(row.points)}
      </span>
    </li>
  );
}

/* A lone last card on a wide screen spans the row, so the row has no empty half. */
function Board({ board, headshots, spans }: { board: LeaderBoard; headshots: HeadshotMap; spans: boolean }) {
  return (
    <div className={cn("rounded-card bg-card p-sp-3", spans && "tablet:col-span-full")}>
      <Label className="mb-sp-1">{board.position}</Label>
      {board.rows.length > 0 ? (
        <ol className="m-0 list-none p-0 text-row leading-tight">
          {board.rows.map((row) => (
            <Row key={row.rank} row={row} headshots={headshots} wide={!spans} />
          ))}
        </ol>
      ) : (
        <p className="m-0 text-meta text-mute">No starters this week</p>
      )}
    </div>
  );
}

export function PositionLeaders({
  leaders,
  headshots,
  blurb,
}: {
  leaders: LeaderBoard[];
  headshots: HeadshotMap;
  blurb?: string;
}) {
  const lastSpans = leaders.length % 2 === 1;
  return (
    <Chapter id="leaders" reveal>
      <Label heading>Position Leaders</Label>
      {/* minmax(0,1fr) caps the column at the section width, so a one-line row cannot grow past the gutter. */}
      <div className="grid grid-cols-[minmax(0,1fr)] gap-sp-2 tablet:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        {leaders.map((board, i) => (
          <Board
            key={board.position}
            board={board}
            headshots={headshots}
            spans={lastSpans && i === leaders.length - 1}
          />
        ))}
      </div>
      {blurb && <Blurb className="mt-sp-3">{blurb}</Blurb>}
    </Chapter>
  );
}
