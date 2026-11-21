/**
 * The Ledger of a finder offer: a "You get" and a "You give" column, a row per player with his rank, a trade value
 * total under each column, and one plain line on the gap (decision 17). The near ideas fold under the picks.
 */
import { ChevronDown } from "lucide-react";
import { Collapsible, CollapsiblePanel, CollapsibleTrigger } from "@cpc/design/ui/collapsible";
import { SMOOTH_OUT } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import { Headshot } from "@cpc/league/headshot";
import type { NearIdea } from "../lib/analyze-types";

type Offer = Pick<NearIdea, "sides" | "totals">;
type Player = Offer["sides"][number]["gives"][number];

/* A gap under this share of the smaller total reads as even, so a trade of 10.2 for 10.0 does not claim a winner. */
const EVEN_UNDER = 3;

/* The two sides of an offer from the view of the asker: the players he gets and gives, and the trade value total of
   each, the chart sum of the players that each side gives. A total is null for a week with no chart. */
export function ledgerOf(offer: Offer, asker: number) {
  const mine = offer.sides.find((side) => side.roster_id === asker) ?? offer.sides[0];
  const theirs = offer.sides.find((side) => side !== mine) ?? offer.sides[1];
  const total = (rosterId: number) =>
    offer.totals.find((t) => t.roster_id === rosterId)?.trade_value ?? null;
  return {
    partner: theirs.team,
    get: mine.gets,
    give: mine.gives,
    getValue: total(theirs.roster_id),
    giveValue: total(mine.roster_id),
  };
}

/* One plain line on the gap of the two totals, as a whole percent of the smaller one, such as "You get 9% more trade
   value" for 68.0 against 62.5. No line when a total is missing or 0, because a percent of nothing says nothing. */
export function gapLine(giveValue: number | null, getValue: number | null): string | null {
  if (giveValue === null || getValue === null || giveValue <= 0 || getValue <= 0) return null;
  const more = Math.round(
    (Math.max(giveValue, getValue) / Math.min(giveValue, getValue) - 1) * 100,
  );
  if (more < EVEN_UNDER) return "Even in trade value";
  return getValue > giveValue
    ? `You get ${more}% more trade value`
    : `You give ${more}% more trade value`;
}

/* One player row: the face, the name, then the position, the NFL team, and the rank. The row shows no trade value, so
   the card stays calm. The full result shows each value. */
function LedgerRow({ player }: { player: Player }) {
  return (
    <li className="gap-sp-2 flex min-w-0 items-center">
      <Headshot
        src={player.headshot}
        lazy
        className="size-avatar bg-page flex-none rounded-full object-cover object-top outline-1 -outline-offset-1 outline-black/10"
      />
      <span className="flex min-w-0 flex-col">
        <b className="text-row leading-tight font-bold text-pretty">{player.name}</b>
        <span className="text-meta text-mute tabular-nums">
          {player.position} · {player.nfl_team}
          {player.season_rank ? ` · ${player.season_rank}` : ""}
        </span>
      </span>
    </li>
  );
}

/* One column: the label with its count, the rows, and the total at the foot. The foot sits at the bottom of the grid
   cell, so the two totals line up when one column has more rows. */
function LedgerColumn({
  label,
  players,
  value,
  lead,
}: {
  label: string;
  players: Player[];
  value: number | null;
  lead: boolean;
}) {
  return (
    <div className="gap-sp-3 flex min-w-0 flex-col">
      <span
        className={cn(
          "text-label tracking-caps font-bold uppercase",
          lead ? "text-accent-ink" : "text-mute",
        )}
      >
        {label} · {players.length}
      </span>
      <ul aria-label={label} className="gap-sp-3 m-0 flex list-none flex-col p-0">
        {players.map((player) => (
          <LedgerRow key={player.player_id} player={player} />
        ))}
      </ul>
      {value !== null && (
        <span
          data-total
          className="border-divider pt-sp-2 text-meta text-mute mt-auto border-t tabular-nums"
        >
          Trade value <b className="text-ink">{value.toFixed(1)}</b>
        </span>
      )}
    </div>
  );
}

/* The Ledger block of a card. "You get" leads on the left in the accent, so the gain reads first. */
export function Ledger({ offer, asker }: { offer: Offer; asker: number }) {
  const view = ledgerOf(offer, asker);
  const gap = gapLine(view.giveValue, view.getValue);
  return (
    <div className="gap-x-sp-4 gap-y-sp-3 rounded-card bg-card p-sp-3 grid grid-cols-2">
      <LedgerColumn label="You get" players={view.get} value={view.getValue} lead />
      <LedgerColumn label="You give" players={view.give} value={view.giveValue} lead={false} />
      {gap !== null && (
        <p data-gap className="text-meta text-ink col-span-2 m-0 font-bold">
          {gap}
        </p>
      )}
    </div>
  );
}

/* The count words of a shape for the reader: "You give 2, get 1". */
function countLine(give: number, get: number): string {
  return `You give ${give}, get ${get}`;
}

/* One near idea: the shape, the partner, the names of each side, and the one reason it fell short. */
function NearRow({ idea, asker }: { idea: NearIdea; asker: number }) {
  const view = ledgerOf(idea, asker);
  const names = (players: Player[]) => players.map((player) => player.name).join(", ");
  return (
    <li className="gap-sp-1 border-divider py-sp-3 flex flex-col border-t first:border-t-0">
      <div className="gap-sp-3 flex items-baseline justify-between">
        <b className="text-row leading-tight">{countLine(view.give.length, view.get.length)}</b>
        <span className="text-meta text-mute min-w-0 truncate">With {view.partner}</span>
      </div>
      <p className="text-meta text-ink-2 m-0 text-pretty">
        <span className="text-accent-ink font-bold">Get</span> {names(view.get)}{" "}
        <span className="text-mute">·</span> <span className="font-bold">Give</span>{" "}
        {names(view.give)}
      </p>
      <p className="text-meta text-mute m-0 text-pretty">{idea.reason}</p>
    </li>
  );
}

/* The near ideas, folded under the picks as "Close, but not sent · N". The shared Collapsible fades the panel in
   with a small rise, and the chevron flips, as the Bullets of a card do. The closed panel is hidden, so a keyboard
   skips its rows. With motion off it opens at once. */
export function NearIdeas({ near, asker }: { near: NearIdea[]; asker: number }) {
  if (near.length === 0) return null;
  return (
    <Collapsible className="rounded-card border-rule bg-page px-sp-4 py-sp-1 flex flex-col border">
      <CollapsibleTrigger className="press group min-h-touch gap-sp-2 text-row text-ink focus-visible:outline-accent flex w-full cursor-pointer items-center justify-between font-bold focus-visible:outline-2">
        Close, but not sent · {near.length}
        <ChevronDown
          aria-hidden="true"
          style={{ transitionTimingFunction: `cubic-bezier(${SMOOTH_OUT.join(",")})` }}
          className="size-sp-4 transition-transform duration-250 group-data-open:-scale-y-100 motion-reduce:transition-none"
        />
      </CollapsibleTrigger>
      <CollapsiblePanel>
        <ul className="pb-sp-2 m-0 list-none p-0">
          {near.map((idea) => (
            <NearRow key={idea.offer_id} idea={idea} asker={asker} />
          ))}
        </ul>
      </CollapsiblePanel>
    </Collapsible>
  );
}
