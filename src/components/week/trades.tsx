/**
 * The trades chapter: one grey card per trade, with a column per side that lists what the side gets.
 * Two sides face each other across a red For tag; three or four sides wrap two per row with no tag.
 * A phone stacks the cards; the tablet tier and up put two cards per row, so two trades compare side by side.
 */
import { Fragment } from "react";
import { Reveal } from "@/components/parts/reveal";
import { stagger } from "@/lib/motion";
import { cn } from "@/lib/utils";
import type { AvatarMap, Trade, TradeSide } from "@/lib/week-types";
import { Avatar } from "@/components/parts/avatar";
import { avatarSrc } from "@/lib/avatar";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { managerHref, TeamName } from "@/components/parts/team-name";

/* Each column spans three rows of the card grid: the team, the Gets label, and the chips.
   A long team name grows its row in both columns, so the chips start on one line. */
function Side({ side, avatars, managersHref }: { side: TradeSide; avatars: AvatarMap; managersHref: string | null }) {
  return (
    <div className="row-span-3 grid min-w-0 grid-rows-subgrid gap-y-0">
      <div className="flex flex-col items-center gap-sp-1 text-center text-meta leading-tight font-extrabold hyphens-auto">
        <Avatar src={avatarSrc(avatars, side.team.roster_id)} />
        <span>
          <TeamName name={side.team.name} href={managerHref(managersHref, side.team.roster_id)} />
        </span>
      </div>
      <span className="mt-sp-2 mb-sp-1 justify-self-center text-label font-bold tracking-wide text-mute uppercase">
        Gets
      </span>
      <ul className="m-0 flex list-none flex-col gap-sp-2 p-0">
        {side.players.map((player) => (
          <li
            key={player.name}
            className="flex flex-col items-center overflow-hidden rounded-card bg-wht px-sp-2 pt-sp-2 pb-sp-3 text-center"
          >
            {/* The cutout fills the chip top edge to edge, so the chip reads as a card for that player.
                The red rule matches the page accent. The gradient is plain sRGB, as the stylesheet draws it.
                The base styles cap an image at 100% width, so max-w-none lets the cutout reach past the chip padding. */}
            <img
              src={player.headshot}
              alt=""
              loading="lazy"
              className="-mx-sp-2 -mt-sp-2 mb-sp-2 block h-headshot w-[calc(100%+var(--spacing-sp-2)*2)] max-w-none flex-none border-b-2 border-red bg-[linear-gradient(var(--color-gry),var(--color-wht))] object-contain object-bottom"
            />
            <b className="text-row leading-tight font-extrabold tracking-snug">{player.name}</b>
          </li>
        ))}
        {side.picks.map((pick, i) => (
          <li key={i} className="py-sp-1 text-center text-meta text-mute">
            {pick}
          </li>
        ))}
      </ul>
    </div>
  );
}

/* The divider runs the full card height between the two columns. The tag sits on it, level with the team names. */
function For() {
  return (
    <div className="relative row-span-3 flex flex-col items-center before:absolute before:inset-y-0 before:left-1/2 before:w-px before:bg-divider">
      <span className="relative mt-sp-5 rounded-sm bg-red p-sp-1 text-label font-extrabold tracking-caps text-on-dark uppercase">
        For
      </span>
    </div>
  );
}

function TradeCard({
  trade,
  avatars,
  index,
  managersHref,
}: {
  trade: Trade;
  avatars: AvatarMap;
  index: number;
  managersHref: string | null;
}) {
  // Three or four sides have no single other side, so only a pair gets the For tag.
  const pair = trade.sides.length === 2;
  return (
    // The label is the first step of the stagger, so the first card is the second.
    <Reveal className={cn("rounded-card bg-gry p-sp-3", index > 0 && "mt-sp-2 tablet:mt-0")} delay={stagger(index + 1)}>
      <div
        className={cn(
          "grid gap-x-sp-2 gap-y-sp-4",
          pair ? "grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]" : "grid-cols-[minmax(0,1fr)_minmax(0,1fr)]",
        )}
      >
        {trade.sides.map((side, i) => (
          <Fragment key={side.team.roster_id}>
            {pair && i === 1 && <For />}
            <Side side={side} avatars={avatars} managersHref={managersHref} />
          </Fragment>
        ))}
      </div>
    </Reveal>
  );
}

/* A week with no trades has no trades chapter, as the old page did.
   The label and the cards stagger in one by one, so the chapter itself has no reveal.
   The managers href is the managers index of the season. With null the team names render as plain text. */
export function Trades({
  trades,
  avatars,
  managersHref = null,
}: {
  trades: Trade[];
  avatars: AvatarMap;
  managersHref?: string | null;
}) {
  if (trades.length === 0) return null;
  return (
    <Chapter id="trades">
      <Reveal delay={stagger(0)}>
        <Label heading>Trades</Label>
      </Reveal>
      {/* The grid gap takes the place of the card margin. The grid fills a row before the next,
          so the stagger index still reveals each row left to right. A lone last card keeps its column width. */}
      <div className="tablet:grid tablet:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] tablet:gap-sp-2">
        {trades.map((trade, i) => (
          <TradeCard key={i} trade={trade} avatars={avatars} index={i} managersHref={managersHref} />
        ))}
      </div>
    </Chapter>
  );
}
