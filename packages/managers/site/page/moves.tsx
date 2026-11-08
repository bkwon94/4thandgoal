/**
 * The Moves chapter of a manager page: the season totals of adds, drops, and trades, then the moves of each week.
 * The weeks come newest first, in the order of the managers file. A week with no moves reads one quiet line.
 */
import { Fragment } from "react";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { Tile } from "@cpc/design/parts/tile";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import type { Manager, ManagerEntry, ManagerPlayer, MoveAdd, MoveTrade, MoveWeek } from "../schema/manager-types";
import { cn } from "@cpc/design/lib/utils";
import { Headshot } from "@cpc/league/headshot";
import { sleeperHeadshot } from "@cpc/league/images";
import { stableId, stableKey } from "@cpc/design/lib/stable-id";

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
function PlayerRow({ player, detail, stable }: { player: ManagerPlayer; detail: string; stable: string }) {
  return (
    <li className="flex items-center gap-sp-2" {...stableId(stable)}>
      <Headshot src={sleeperHeadshot(player.player_id)} size="avatar" lazy className="flex-none rounded-full bg-card object-cover object-top" />
      <span className="flex min-w-0 flex-col">
        <b className="text-row leading-tight font-extrabold tracking-snug">{player.name}</b>
        <span className="text-meta text-mute">{moveMetaLine(player.position, detail)}</span>
      </span>
    </li>
  );
}

/* One side of a trade: the quiet label, then the players with their positions. */
function TradeSide({ label, week, players }: { label: string; week: number; players: ManagerPlayer[] }) {
  return (
    <div className="min-w-0">
      <div className={cn(QUIET_LABEL, "mb-sp-2")}>{label}</div>
      <ul aria-label={label} className="m-0 flex list-none flex-col gap-sp-2 p-0">
        {players.map((player) => (
          <PlayerRow key={player.player_id} player={player} detail="" stable={stableKey("move", week, label, player.player_id)} />
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
function TradeRow({ trade, week, managers, managersHref }: { trade: MoveTrade; week: number; managers: ManagerEntry[]; managersHref: string | null }) {
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
          <TradeSide label="Gave" week={week} players={trade.gave} />
          <TradeSide label="Got" week={week} players={trade.got} />
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
            <PlayerRow key={`add-${add.player_id}`} player={add} detail={addDetail(add)} stable={stableKey("move", week.week, "add", add.player_id)} />
          ))}
          {week.drops.map((drop) => (
            <PlayerRow key={`drop-${drop.player_id}`} player={drop} detail="Dropped" stable={stableKey("move", week.week, "drop", drop.player_id)} />
          ))}
          {week.trades.map((trade, i) => (
            <TradeRow key={`trade-${i}`} trade={trade} week={week.week} managers={managers} managersHref={managersHref} />
          ))}
        </ul>
      )}
    </div>
  );
}

/* The three season totals, a tile each, in one row. A zero is a count too, so it shows as a plain 0. */
function Totals({ adds, drops, trades }: { adds: number; drops: number; trades: number }) {
  return (
    <div role="group" aria-label="Move Totals" className="mb-sp-6 grid grid-cols-3 gap-sp-2">
      <Tile label="Adds" value={adds} />
      <Tile label="Drops" value={drops} />
      <Tile label="Trades" value={trades} />
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
      <Totals adds={moves.adds} drops={moves.drops} trades={moves.trades} />
      {moves.weeks.map((week, i) => (
        <Week key={week.week} week={week} first={i === 0} managers={managers} managersHref={managersHref} />
      ))}
    </Chapter>
  );
}
