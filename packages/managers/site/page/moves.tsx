/**
 * The Moves chapter of a manager page: the season totals of adds, drops, and trades, then the moves of each week.
 * The weeks come newest first, in the order of the managers file. A week with no moves reads one quiet line.
 */
import { Fragment } from "react";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { Tile, type TileTrend, type TrendPoint } from "@cpc/design/parts/tile";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import type { Manager, ManagerEntry, ManagerPlayer, MoveAdd, MoveTrade, MoveWeek } from "../schema/manager-types";
import { cn } from "@cpc/design/lib/utils";
import { Headshot } from "@cpc/league/headshot";
import { sleeperHeadshot } from "@cpc/league/images";

/* The quiet label of a group: small, uppercase, and mute, as the Gets label of the week page trade card. */
const QUIET_LABEL = "text-meta leading-tight font-bold tracking-wide text-mute uppercase";

/* The position, then the detail. The players file can lack a player, so a null position drops out of the line.
   A trade row has no detail past the position, so an empty detail drops out too. */
function moveMetaLine(position: string | null, detail: string) {
  return [position, detail].filter(Boolean).join(" · ");
}

/* A free agent pickup has no bid. A waiver claim with no saved bid reads as a plain waiver claim. */
function addDetail(add: MoveAdd) {
  if (add.kind === "free_agent") return "Free agent";
  return add.bid === null ? "Waiver" : `$${add.bid} bid`;
}

/* One player row: the headshot, the name as the one emphasis, and one quiet line under it. */
function PlayerRow({ player, detail }: { player: ManagerPlayer; detail: string }) {
  return (
    <li className="flex items-center gap-sp-2">
      <Headshot src={sleeperHeadshot(player.player_id)} size="avatar" lazy className="flex-none rounded-full bg-card object-cover object-top" />
      <span className="flex min-w-0 flex-col">
        <b className="text-row leading-tight font-extrabold tracking-snug">{player.name}</b>
        <span className="text-meta text-mute">{moveMetaLine(player.position, detail)}</span>
      </span>
    </li>
  );
}

/* One side of a trade: the quiet label, then the players with their positions. */
function TradeSide({ label, players }: { label: string; players: ManagerPlayer[] }) {
  return (
    <div className="min-w-0">
      <div className={cn(QUIET_LABEL, "mb-sp-2")}>{label}</div>
      <ul aria-label={label} className="m-0 flex list-none flex-col gap-sp-2 p-0">
        {players.map((player) => (
          <PlayerRow key={player.player_id} player={player} detail="" />
        ))}
      </ul>
    </div>
  );
}

/* The name of the other team of a trade, as a link to its manager page when the season has one.
   The link is a full tap target, so it stands in a line of its own height and keeps the color of the label. */
function TradeTeam({ name, href }: { name: string; href: string | null }) {
  if (href === null) return name;
  return (
    <a href={href} className="inline-flex min-h-touch items-center text-inherit underline underline-offset-2">
      {name}
    </a>
  );
}

/* A trade as a grey card with both sides, as the week page trade card sets it.
   The file carries the roster ids of the other sides, so the card looks each id up in the managers of the season.
   It names each team and links the name to its manager page. The group label is the same text as the visible one. */
function TradeRow({ trade, managers, managersHref }: { trade: MoveTrade; managers: ManagerEntry[]; managersHref: string | null }) {
  const others = trade.with.flatMap((id) => managers.find((entry) => entry.roster_id === id) ?? []);
  const label = `Trade With ${others.map((entry) => entry.team.name).join(" And ")}`;
  return (
    <li>
      <div role="group" aria-label={label} className="rounded-card bg-card p-sp-3">
        <div className={cn(QUIET_LABEL, "mb-sp-3")}>
          Trade With{" "}
          {others.map((entry, i) => (
            <Fragment key={entry.roster_id}>
              {i > 0 && " And "}
              <TradeTeam name={entry.team.name} href={managerHrefOrNull(managersHref, entry.roster_id)} />
            </Fragment>
          ))}
        </div>
        <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-x-sp-3">
          <TradeSide label="Gave" players={trade.gave} />
          <TradeSide label="Got" players={trade.got} />
        </div>
      </div>
    </li>
  );
}

/* One week: the quiet label, then the adds, the drops, and the trades in that order. */
function Week({ week, first, managers, managersHref }: { week: MoveWeek; first: boolean; managers: ManagerEntry[]; managersHref: string | null }) {
  const label = `Week ${week.week}`;
  const empty = week.adds.length + week.drops.length + week.trades.length === 0;
  return (
    <div role="group" aria-label={label} className={cn(!first && "mt-sp-6")}>
      <div className={cn(QUIET_LABEL, "mb-sp-2")}>{label}</div>
      {empty ? (
        <div className="m-0 text-body text-mute">No moves.</div>
      ) : (
        <ul className="m-0 flex list-none flex-col gap-sp-3 p-0">
          {week.adds.map((add) => (
            <PlayerRow key={`add-${add.player_id}`} player={add} detail={addDetail(add)} />
          ))}
          {week.drops.map((drop) => (
            <PlayerRow key={`drop-${drop.player_id}`} player={drop} detail="Dropped" />
          ))}
          {week.trades.map((trade, i) => (
            <TradeRow key={`trade-${i}`} trade={trade} managers={managers} managersHref={managersHref} />
          ))}
        </ul>
      )}
    </div>
  );
}

/* The weeks as a list for a sentence: "week 7", "week 1 and week 4", or "week 1, week 4, and week 6". */
function weekList(weeks: number[]) {
  const names = weeks.map((week) => `week ${week}`);
  if (names.length <= 2) return names.join(" and ");
  return `${names.slice(0, -1).join(", ")}, and ${names.at(-1)}`;
}

/* One count of each week from week 1 to the newest week of the file. The file holds a week with no moves as empty
   lists, and a week it lacks counts as zero, so each chart has one slot per week. */
function weekCounts(weeks: MoveWeek[], count: (week: MoveWeek) => number): TrendPoint[] {
  const newest = Math.max(0, ...weeks.map((week) => week.week));
  return Array.from({ length: newest }, (_, index) => {
    const saved = weeks.find((week) => week.week === index + 1);
    return { week: index + 1, value: saved ? count(saved) : 0 };
  });
}

/* Bars of the adds or the drops of each week. The text names the busiest week, the news of a run of moves. */
function barsTrend(points: TrendPoint[], noun: string): TileTrend {
  const high = Math.max(0, ...points.map((point) => point.value));
  const text =
    high === 0
      ? `No ${noun} this season.`
      : `The most ${noun} in one week: ${high}, in ${weekList(points.filter((point) => point.value === high).map((point) => point.week))}.`;
  return { points, week: points.length, kind: "bars", text };
}

/* A dot for each week with a trade. A trade is rare, so the text names each week that had one. */
function dotsTrend(points: TrendPoint[]): TileTrend {
  const weeks = points.filter((point) => point.value > 0).map((point) => point.week);
  const text = weeks.length === 0 ? "No trades this season." : `${weeks.length === 1 ? "A trade" : "Trades"} in ${weekList(weeks)}.`;
  return { points, week: points.length, kind: "dots", text };
}

/* The three season totals, a tile each, in one row. A zero is a count too, so it shows as a plain 0.
   Each tile is a Trend tile of its count in each week. A file with no weeks has no trend. */
function Totals({ moves }: { moves: Manager["moves"] }) {
  const trend = (make: () => TileTrend) => (moves.weeks.length === 0 ? undefined : make());
  return (
    <div role="group" aria-label="Move Totals" className="mb-sp-6 grid grid-cols-3 gap-sp-2">
      <Tile label="Adds" value={moves.adds} trend={trend(() => barsTrend(weekCounts(moves.weeks, (week) => week.adds.length), "adds"))} />
      <Tile label="Drops" value={moves.drops} trend={trend(() => barsTrend(weekCounts(moves.weeks, (week) => week.drops.length), "drops"))} />
      <Tile label="Trades" value={moves.trades} trend={trend(() => dotsTrend(weekCounts(moves.weeks, (week) => week.trades.length)))} />
    </div>
  );
}

/* The chapter stays whole, so a long season lists every week with no collapse. */
export function Moves({ manager, managers, managersHref }: { manager: Manager; managers: ManagerEntry[]; managersHref: string | null }) {
  const { moves } = manager;
  return (
    <Chapter reveal id="moves">
      {/* The meta size keeps the heading over the text floor of 11px on a phone. */}
      <Label heading className="text-meta">Moves</Label>
      <Totals moves={moves} />
      {moves.weeks.map((week, i) => (
        <Week key={week.week} week={week} first={i === 0} managers={managers} managersHref={managersHref} />
      ))}
    </Chapter>
  );
}
