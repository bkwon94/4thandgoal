/**
 * The hero of the week page: the matchup of the week with its reason, the margin, both teams and their top players,
 * the share bar, and the full blurb. It sits on the band in both themes, so the hero stays dark in light.
 */
import { num } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Hero } from "@cpc/design/parts/hero";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { Rise } from "@cpc/design/parts/rise";
import type { AvatarMap, HeadshotMap, MatchupSide, Pick } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { ShareBar, shareOf } from "../parts/share-bar";
import { photoOf } from "../parts/photo";
import { textId } from "@cpc/design/lib/stable-id";

/* The week number with two digits, as the week chip writes it: "08". */
const twoDigits = (week: number) => String(week).padStart(2, "0");

/* The top player of a side as one line: "Brock Bowers · TE · 24.7". A side that started no one has no line. */
function topLine(side: MatchupSide): string | null {
  return side.top ? `${side.top.name} · ${side.top.position} · ${num(side.top.points)}` : null;
}

/* One team of the matchup: the avatar, the name with the top player under it, and the score.
   Each line of text sits on a plate, so the grid and the glow never sit under a letter.
   The home hero passes withTop false, because it shows the matchup in one look and not its players. */
export function TeamRow({
  side,
  avatars,
  lead,
  withTop = true,
}: {
  side: MatchupSide;
  avatars: AvatarMap;
  lead: boolean;
  withTop?: boolean;
}) {
  const top = withTop ? topLine(side) : null;
  return (
    <div className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-sp-3">
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} />
      <div className="min-w-0">
        <div className={cn("plate w-fit text-lead leading-tight", lead ? "font-bold text-on-dark" : "text-on-dark-2")}>
          {side.team.name}
        </div>
        {top !== null && <div className="plate mt-sp-1 w-fit text-meta leading-tight text-on-dark-muted">{top}</div>}
      </div>
      <div
        className={cn(
          "plate font-mono text-score leading-stat tabular-nums",
          lead ? "font-bold text-on-dark" : "text-on-dark-muted",
        )}
      >
        {num(side.score)}
      </div>
    </div>
  );
}

export function MatchupOfTheWeek({
  week,
  dates,
  publishDate,
  pick,
  avatars,
  headshots,
  blurb,
}: {
  week: number;
  dates: string;
  publishDate: string;
  pick: Pick;
  avatars: AvatarMap;
  headshots: HeadshotMap;
  blurb: string;
}) {
  // The JSON puts the winner first. A tie has no winner, and the first side still leads the hero.
  const [first, second] = pick.sides;
  return (
    // The rail links the hero by this id, and the scroll padding keeps it clear of the top band.
    <div id="motw">
      <Hero label="Matchup of the Week">
        <Rise step={0}>
          <h1 className="plate m-0 w-fit font-mono text-meta leading-tight font-bold tracking-caps text-on-dark-muted uppercase">
            {`Week ${twoDigits(week)} // Matchup of the Week`}
          </h1>
          {/* One string, so React writes one text node and the browser kerns the line as one run. */}
          <div className="plate mt-sp-2 w-fit font-mono text-meta leading-tight text-on-dark-2 tabular-nums">
            {`${dates} · Published ${publishDate}`}
          </div>
        </Rise>
        <Rise step={1} className="mt-sp-5 flex items-center justify-between gap-sp-4">
          <div className="min-w-0">
            <div className="plate w-fit font-mono text-meta leading-tight font-bold tracking-caps text-accent-text uppercase">
              {`${pick.reason} · Margin`}
            </div>
            <div className="plate mt-sp-2 w-fit font-mono text-hero leading-none font-bold tracking-grade tabular-nums">
              {num(first.score - second.score)}
            </div>
          </div>
          {first.top !== null && <PhotoFrame src={photoOf(headshots, first.top.player_id)} name={first.top.name} size="lg" />}
        </Rise>
        <Rise step={2} className="mt-sp-5 flex flex-col gap-sp-3">
          <TeamRow side={first} avatars={avatars} lead />
          <TeamRow side={second} avatars={avatars} lead={false} />
          <ShareBar share={shareOf(first.score, second.score)} tone="hero" />
        </Rise>
        <Rise step={3}>
          <p className="plate mt-sp-5 mb-0 max-w-measure text-lead leading-body text-on-dark-2" {...textId("blurb", blurb)}>{blurb}</p>
        </Rise>
      </Hero>
    </div>
  );
}
