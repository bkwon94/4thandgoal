/**
 * The Trades chapter: one card for each trade, with each side and the players it gets, each in a round photo frame.
 * Two sides face each other across the swap arrows, three or four sit two per row, and a tap opens the record and manager link of each.
 */
import { Fragment } from "react";
import { cn } from "@cpc/design/lib/utils";
import { record } from "@cpc/design/format/format";
import { OpenCard } from "@cpc/design/parts/open-card";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { AvatarMap, Trade, TradeSide } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import { WeekChapter } from "../parts/week-chapter";

/* The team row of a side. The card is one button, so the name is plain text. The manager link sits in the open panel. */
function TeamRow({ side, avatars }: { side: TradeSide; avatars: AvatarMap }) {
  return (
    <span className="flex min-h-touch min-w-0 items-center gap-sp-2 text-body leading-tight font-bold">
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} />
      <span className="min-w-0 truncate">{side.team.name}</span>
    </span>
  );
}

/* One side of a closed trade. A button holds only phrasing content, so the list of players is a span with the list role. */
function Side({ side, avatars }: { side: TradeSide; avatars: AvatarMap }) {
  return (
    <span className="flex min-w-0 flex-col gap-sp-2">
      <TeamRow side={side} avatars={avatars} />
      <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">Gets</span>
      <span role="list" aria-label={`${side.team.name} gets`} className="flex flex-col gap-sp-2">
        {side.players.map((player) => (
          <span role="listitem" key={player.name} className="flex min-w-0 items-center gap-sp-2">
            <PhotoFrame src={player.headshot} name={player.name} size="md" decorative />
            <span className="min-w-0 text-body leading-tight font-semibold">{player.name}</span>
          </span>
        ))}
        {side.picks.map((pick) => (
          <span role="listitem" key={pick} className="text-meta leading-tight text-mute">
            {pick}
          </span>
        ))}
      </span>
    </span>
  );
}

/* The swap arrows between the two sides of a pair. They are a graphic, so a screen reader skips them. */
function Swap() {
  return (
    <span aria-hidden="true" className="flex justify-center self-center text-mute">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 8h14l-3-3M20 16H6l3 3" />
      </svg>
    </span>
  );
}

/* The avatar of a chip, in pixels. It sits inside one line of meta text. */
const CHIP_AVATAR = 20;

/* One trade on the Open card. The closed card is the trade of now: each side and the players it gets.
   The open panel holds a record chip for each side and one manager page link for each side. */
function TradeCard({
  trade,
  index,
  avatars,
  managersHref,
}: {
  trade: Trade;
  index: number;
  avatars: AvatarMap;
  managersHref: string | null;
}) {
  // Three or four sides have no single other side, so only a pair gets the swap arrows.
  const pair = trade.sides.length === 2;
  const chips = trade.sides.map((side) => (
    <>
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} size={CHIP_AVATAR} />
      {`${side.team.name} ${record(side.team.wins, side.team.losses)}`}
    </>
  ));
  // With no managers file a side has no href, so it has no link.
  const actions = trade.sides.flatMap((side) => {
    const href = managerHrefOrNull(managersHref, side.team.roster_id);
    return href === null ? [] : [{ href, label: side.team.name, hiddenLabel: ", manager page" }];
  });
  return (
    <OpenCard
      as="article"
      // A trade has no id in the JSON, so its place in the list names it.
      panelId={`trade-${index}`}
      headClassName={cn(
        "grid items-start gap-sp-3",
        pair ? "grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]" : "grid-cols-[minmax(0,1fr)_minmax(0,1fr)]",
      )}
      head={trade.sides.map((side, sideIndex) => (
        <Fragment key={side.team.roster_id}>
          {pair && sideIndex === 1 && <Swap />}
          <Side side={side} avatars={avatars} />
        </Fragment>
      ))}
      chips={chips}
      action={actions}
    />
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
      {/* Two cards per row start at the desktop tier. At the tablet tier a pair card is too narrow for a name such as "McConkey". */}
      {/* The cards start at the top of their row, so an open card does not stretch the closed card beside it. */}
      <div className="grid grid-cols-1 items-start gap-sp-2 desktop:grid-cols-2">
        {trades.map((trade, index) => (
          <TradeCard key={index} trade={trade} index={index} avatars={avatars} managersHref={managersHref} />
        ))}
      </div>
    </WeekChapter>
  );
}
