/**
 * The Trades chapter: one card for each trade, with each side and the players it gets, each in a round photo frame.
 * Two sides face each other across the swap arrows. Three or four sides sit two per row with no arrows.
 */
import { Fragment } from "react";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { AvatarMap, Trade, TradeSide } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import { WeekChapter } from "../parts/week-chapter";

/* The team row of a side. With a managers file the whole row is the link, so the tap target is 44px or more. */
function TeamRow({ side, avatars, href }: { side: TradeSide; avatars: AvatarMap; href: string | null }) {
  const content = (
    <>
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} />
      <span className="min-w-0 truncate">{side.team.name}</span>
    </>
  );
  const row = "flex min-h-touch min-w-0 items-center gap-sp-2 text-body leading-tight font-bold";
  return href === null ? (
    <div className={row}>{content}</div>
  ) : (
    <a href={href} className={cn(row, "press text-inherit no-underline hover-fine:underline")}>
      {content}
    </a>
  );
}

function Side({ side, avatars, managersHref }: { side: TradeSide; avatars: AvatarMap; managersHref: string | null }) {
  return (
    <div className="flex min-w-0 flex-col gap-sp-2">
      <TeamRow side={side} avatars={avatars} href={managerHrefOrNull(managersHref, side.team.roster_id)} />
      <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">Gets</span>
      <ul aria-label={`${side.team.name} gets`} className="m-0 flex list-none flex-col gap-sp-2 p-0">
        {side.players.map((player) => (
          <li key={player.name} className="flex min-w-0 items-center gap-sp-2">
            <PhotoFrame src={player.headshot} name={player.name} size="md" decorative />
            <span className="min-w-0 text-body leading-tight font-semibold">{player.name}</span>
          </li>
        ))}
        {side.picks.map((pick) => (
          <li key={pick} className="text-meta leading-tight text-mute">
            {pick}
          </li>
        ))}
      </ul>
    </div>
  );
}

/* The swap arrows between the two sides of a pair. They are a graphic, so a screen reader skips them. */
function Swap() {
  return (
    <div aria-hidden="true" className="flex justify-center self-center text-mute">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 8h14l-3-3M20 16H6l3 3" />
      </svg>
    </div>
  );
}

function TradeCard({ trade, avatars, managersHref }: { trade: Trade; avatars: AvatarMap; managersHref: string | null }) {
  // Three or four sides have no single other side, so only a pair gets the swap arrows.
  const pair = trade.sides.length === 2;
  return (
    <Card
      as="article"
      className={cn(
        "grid items-start gap-sp-3",
        pair ? "grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]" : "grid-cols-[minmax(0,1fr)_minmax(0,1fr)]",
      )}
    >
      {trade.sides.map((side, index) => (
        <Fragment key={side.team.roster_id}>
          {pair && index === 1 && <Swap />}
          <Side side={side} avatars={avatars} managersHref={managersHref} />
        </Fragment>
      ))}
    </Card>
  );
}

/* A week with no trades has no trades chapter. The managers href is the managers index of the season.
   With null the team names are plain text. */
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
    <WeekChapter id="trades" title="Trades" note={`${trades.length} this week`}>
      <div className="grid grid-cols-1 gap-sp-2 tablet:grid-cols-2">
        {trades.map((trade, index) => (
          <TradeCard key={index} trade={trade} avatars={avatars} managersHref={managersHref} />
        ))}
      </div>
    </WeekChapter>
  );
}
