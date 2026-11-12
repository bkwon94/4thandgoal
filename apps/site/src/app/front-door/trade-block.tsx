/**
 * The trade card: the two sides of a trade, a bar of the projected points for the rest of the season for each player,
 * a tug bar of the two totals, and the Lean at the close. Trade ideas hold one row per offer, and the first one opens.
 */
"use client";

import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { useId, useState, type ReactNode } from "react";
import { z } from "zod";
import { BulletRows } from "@cpc/analyzer/form/bullet-rows";
import { bulletSchema, leanSchema } from "@cpc/analyzer/lib/schemas/api";
import type { Lean } from "@cpc/analyzer/lib/analyze-types";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { FAST, fadeIn, staggerOf } from "./motion";

const cardPlayerSchema = z.object({ player_id: z.string(), name: z.string(), position: z.string(), nfl_team: z.string(), points: z.number() });
const cardSideSchema = z.object({ roster_id: z.number(), team: z.string(), yours: z.boolean(), gets: z.array(cardPlayerSchema), total: z.number() });
const tradeOfferSchema = z.object({
  id: z.string(),
  partner: z.string(),
  gist: z.string(),
  lean: leanSchema.nullable(),
  case: z.string().nullable(),
  bullets: z.array(bulletSchema),
  sides: z.array(cardSideSchema),
});

/* The trade card as the API sends it. The analyzer gives the Lean, the Case, and the Bullets. The card adds no grade. */
export const tradeBlockSchema = z.object({ kind: z.literal("trade"), offers: z.array(tradeOfferSchema) });
export type TradeBlock = z.infer<typeof tradeBlockSchema>;
export type TradeOffer = z.infer<typeof tradeOfferSchema>;
type CardSide = z.infer<typeof cardSideSchema>;

/* A yes leans in the accent and a no in the plain ink, as on the Trade page. */
const LEAN_COLOR: Record<Lean, string> = {
  "Send it": "text-accent-ink",
  "Lean yes": "text-accent-ink",
  "Gut call": "text-ink-2",
  "Lean no": "text-ink",
  Pass: "text-ink",
};

const points = (value: number) => value.toFixed(1);
/* The side that gets more points wins the red. A tie lights neither side. */
const wins = (side: CardSide, sides: CardSide[]) => sides.every((other) => other === side || side.total > other.total);
const sideLabel = (side: CardSide) => (side.yours ? "You get" : `${side.team} gets`);

/* The card as one short line of plain text, so the turn of the Answer carries it. */
export function tradeBlockText(block: TradeBlock): string {
  const offers = block.offers.map((offer) => {
    const sides = offer.sides.map((side) => `${sideLabel(side)} ${side.gets.map((p) => p.name).join(", ")} (${points(side.total)})`).join(", ");
    return `${offer.gist}: ${sides}${offer.lean ? `. ${offer.lean}` : ""}`;
  });
  return `Trade: ${offers.join("; ")}.`;
}

function Caps({ children }: { children: ReactNode }) {
  return <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{children}</span>;
}

/* A bar that grows from its left end. A live card grows each bar on the stagger of its rows. Reduced motion and a kept
   card show the bar at its size. */
function Bar({ share, lit, live, index, className = "" }: { share: number; lit: boolean; live: boolean; index: number; className?: string }) {
  const off = useMotionOff();
  const grow = live && !off;
  return (
    <motion.span
      aria-hidden
      className={`block h-full origin-left rounded-pill ${lit ? "bg-accent" : "bg-mute"} ${className}`}
      style={{ width: `${Math.max(share, 0) * 100}%` }}
      initial={grow ? { scaleX: 0 } : false}
      animate={{ scaleX: 1 }}
      transition={fadeIn(FAST, 0.1 + staggerOf(index))}
    />
  );
}

/* One side: the players it gets, each with a bar of his points against the most points on the card. */
function SideList({ side, lit, max, live, from }: { side: CardSide; lit: boolean; max: number; live: boolean; from: number }) {
  return (
    <div className="flex min-w-0 flex-col gap-sp-1">
      <Caps>{sideLabel(side)}</Caps>
      <ul aria-label={sideLabel(side)} className="m-0 flex list-none flex-col gap-sp-2 p-0">
        {side.gets.map((player, index) => (
          <li key={player.player_id} className="flex min-w-0 flex-col gap-sp-1">
            <span className="flex min-w-0 items-baseline gap-sp-2">
              <span className="truncate text-row leading-tight font-semibold text-ink">{player.name}</span>
              <span className="flex-none font-mono text-meta leading-tight text-mute">
                {player.position} · {player.nfl_team}
              </span>
              <span className="ml-auto flex-none font-mono text-row leading-tight text-ink-2 tabular-nums">{points(player.points)}</span>
            </span>
            <span className="block h-sp-1 overflow-hidden rounded-pill bg-bar-off">
              <Bar share={max > 0 ? player.points / max : 0} lit={lit} live={live} index={from + index} />
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* The tug bar of the two totals: Your side pulls from the left and the other side from the right. */
function Tug({ sides, live }: { sides: CardSide[]; live: boolean }) {
  const [left, right] = sides;
  const sum = sides.reduce((total, side) => total + side.total, 0);
  const label = `Projected points for the rest of the season: ${sides.map((side) => `${side.yours ? "you get" : `${side.team} gets`} ${points(side.total)}`).join(", ")}.`;
  return (
    <div role="img" aria-label={label} className="flex flex-col gap-sp-1 border-t border-rule pt-sp-3">
      <span aria-hidden className="flex items-baseline justify-between gap-sp-2">
        <Caps>Rest of season</Caps>
      </span>
      <span aria-hidden className="flex items-baseline justify-between font-mono text-row leading-tight font-semibold tabular-nums">
        <span className={wins(left, sides) ? "text-accent-ink" : "text-ink-2"}>{points(left.total)}</span>
        {right && <span className={wins(right, sides) ? "text-accent-ink" : "text-ink-2"}>{points(right.total)}</span>}
      </span>
      <span aria-hidden className="flex h-sp-2 gap-sp-0">
        {sides.map((side, index) => (
          <span key={side.roster_id} className={`flex h-full ${index > 0 ? "justify-end" : ""}`} style={{ width: `${sum > 0 ? (side.total / sum) * 100 : 100 / sides.length}%` }}>
            <Bar share={1} lit={wins(side, sides)} live={live} index={index} className={index > 0 ? "origin-right" : ""} />
          </span>
        ))}
      </span>
    </div>
  );
}

/* The detail under a row: it opens taller in place and comes into focus from a soft blur, on the one height method of
   the site. A closed detail is inert and hidden from a screen reader. Reduced motion opens it at once. */
function Detail({ id, open, children }: { id: string; open: boolean; children: ReactNode }) {
  return (
    <div
      id={id}
      aria-hidden={!open}
      inert={!open}
      data-open={open}
      className="group/detail grid grid-rows-[0fr] transition-[grid-template-rows] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] data-[open=true]:grid-rows-[1fr] motion-reduce:transition-none"
    >
      <div className="min-h-0 overflow-hidden">
        <div className="opacity-0 blur-[4px] transition-[opacity,filter] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] group-data-[open=true]/detail:opacity-100 group-data-[open=true]/detail:blur-none motion-reduce:transition-none">
          {children}
        </div>
      </div>
    </div>
  );
}

function Chevron({ open }: { open: boolean }) {
  return (
    <ChevronDown
      aria-hidden
      className={`size-sp-5 flex-none text-mute transition-transform duration-250 ease-out motion-reduce:transition-none ${open ? "[transform:scaleY(-1)]" : ""}`}
    />
  );
}

/* The Case and the top Bullets of a trade check, behind one row that opens in place. */
function WhyRow({ offer }: { offer: TradeOffer }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className="flex flex-col border-t border-rule">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen(!open)}
        className="press flex min-h-touch w-full items-center justify-between gap-sp-2 text-left text-body leading-tight font-semibold text-ink focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent"
      >
        Why
        <Chevron open={open} />
      </button>
      <Detail id={id} open={open}>
        <div className="flex flex-col gap-sp-3 pb-sp-3">
          {offer.case && <p className="m-0 text-body leading-body text-ink-2">{offer.case}</p>}
          {offer.bullets.length > 0 && <BulletRows bullets={offer.bullets} idBase={`card-${offer.id}`} />}
        </div>
      </Detail>
    </div>
  );
}

/* The full card of one trade: the two sides, the tug bar, the Case and the Bullets, the action, and the Lean last. A
   trade check opens its Case behind a row. An offer of trade ideas sits in an open row already, so its Bullets show. */
function OfferBody({ offer, live, action, standalone }: { offer: TradeOffer; live: boolean; action?: ReactNode; standalone: boolean }) {
  const max = Math.max(0, ...offer.sides.flatMap((side) => side.gets.map((player) => player.points)));
  let from = 0;
  return (
    <div role={standalone ? "group" : undefined} aria-label={standalone ? "Trade card" : undefined} className="flex min-w-0 flex-col gap-sp-3">
      {offer.sides.map((side) => {
        const list = <SideList key={side.roster_id} side={side} lit={wins(side, offer.sides)} max={max} live={live} from={from} />;
        from += side.gets.length;
        return list;
      })}
      <Tug sides={offer.sides} live={live} />
      {offer.lean ? (
        (offer.case || offer.bullets.length > 0) && <WhyRow offer={offer} />
      ) : (
        offer.bullets.length > 0 && <BulletRows bullets={offer.bullets} idBase={`card-${offer.id}`} />
      )}
      {action}
      {offer.lean && <p className={`m-0 border-t border-rule pt-sp-3 text-score leading-tight font-bold tracking-tight ${LEAN_COLOR[offer.lean]}`}>{`${offer.lean}.`}</p>}
    </div>
  );
}

/* One offer of trade ideas as a row: the partner and the gist, and the full card under it when open. */
function OfferRow({ offer, open, onToggle, live, action }: { offer: TradeOffer; open: boolean; onToggle: () => void; live: boolean; action?: ReactNode }) {
  const id = useId();
  return (
    <li data-offer className="flex flex-col border-b border-rule last:border-b-0">
      <button
        type="button"
        data-row
        aria-expanded={open}
        aria-controls={id}
        onClick={onToggle}
        className="press flex min-h-touch w-full items-start justify-between gap-sp-3 py-sp-3 text-left focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent"
      >
        <span className="flex min-w-0 flex-col gap-sp-1">
          <Caps>With {offer.partner}</Caps>
          <span className="text-body leading-body font-semibold text-ink">{offer.gist}</span>
        </span>
        <Chevron open={open} />
      </button>
      <Detail id={id} open={open}>
        <div className="pb-sp-4">
          <OfferBody offer={offer} live={live && open} action={action} standalone={false} />
        </div>
      </Detail>
    </li>
  );
}

/* The trade card. A trade check shows its one trade in full. Trade ideas show a row per offer, and the first row opens
   on arrival; a tap opens or closes any other row. `action` gives the link of each trade, such as the Trade page. */
export function TradeBlockView({ block, live, action }: { block: TradeBlock; live: boolean; action?: (offer: TradeOffer) => ReactNode }) {
  const [opened, setOpened] = useState<ReadonlySet<string>>(() => new Set(block.offers.slice(0, 1).map((offer) => offer.id)));
  if (block.offers.length === 1 && block.offers[0].lean) {
    return <OfferBody offer={block.offers[0]} live={live} action={action?.(block.offers[0])} standalone />;
  }
  const toggle = (id: string) =>
    setOpened((now) => {
      const next = new Set(now);
      if (!next.delete(id)) next.add(id);
      return next;
    });
  return (
    <div role="group" aria-label="Trade card" data-block="trade">
      <ul className="m-0 flex list-none flex-col border-t border-rule p-0">
        {block.offers.map((offer) => (
          <OfferRow key={offer.id} offer={offer} open={opened.has(offer.id)} onToggle={() => toggle(offer.id)} live={live} action={action?.(offer)} />
        ))}
      </ul>
    </div>
  );
}
