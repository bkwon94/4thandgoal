/**
 * The hero of the week page, in the hero slots: the week, the winner by the margin, the dates, the reason with both teams
 * and their top players, and the share bar, then the full blurb under it. The hero stays dark in light.
 */
import { num } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Hero } from "@cpc/design/parts/hero";
import type { HeroScene } from "@cpc/design/parts/scene-math";
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

/* The title of a Matchup hero in words: the winner "by" the margin, such as "The Blue Tent by 1.43". The JSON puts the
   winner first. A tie has no winner, so its title names both teams. */
export function matchupTitle(pick: Pick): string {
  const [first, second] = pick.sides;
  const margin = first.score - second.score;
  return margin === 0 ? `${first.team.name} and ${second.team.name} tie` : `${first.team.name} by ${num(margin)}`;
}

/* The small caps line of the reason in the hero, such as "Closest Finish". It sits on a plate, as every text line of a hero. */
const REASON = "plate w-fit font-mono text-meta leading-tight font-bold tracking-caps text-accent-text uppercase";

export function MatchupOfTheWeek({
  week,
  dates,
  publishDate,
  pick,
  avatars,
  headshots,
  blurb,
  scene,
}: {
  week: number;
  dates: string;
  publishDate: string;
  pick: Pick;
  avatars: AvatarMap;
  headshots: HeadshotMap;
  blurb: string;
  // The scene of the week. The week page passes it, because this hero is the first hero of the page.
  scene?: HeroScene;
}) {
  // The JSON puts the winner first. A tie has no winner, and the first side still leads the hero.
  const [first, second] = pick.sides;
  return (
    // The rail links the hero by this id, and the scroll padding keeps it clear of the top band.
    // The blurb sits under the hero in the same chapter, so the hero stays as short as the others (decision 05).
    <div id="motw" className="flex flex-col gap-sp-5">
      <Hero
        label="Matchup of the Week"
        eyebrow={`Week ${twoDigits(week)} // Matchup of the Week`}
        title={matchupTitle(pick)}
        scene={scene}
        // One string, so React writes one text node and the browser kerns the line as one run.
        meta={`${dates} · Published ${publishDate}`}
        feature={
          <Rise step={1} className="flex flex-col gap-sp-3">
            <div className="flex items-center justify-between gap-sp-4">
              <div className={REASON}>{pick.reason}</div>
              {first.top !== null && (
                <PhotoFrame src={photoOf(headshots, first.top.player_id)} name={first.top.name} size="lg" />
              )}
            </div>
            <TeamRow side={first} avatars={avatars} lead />
            <TeamRow side={second} avatars={avatars} lead={false} />
          </Rise>
        }
        // The share bar has no width of its own, so it takes the full width of the action slot.
        action={
          <Rise step={2} className="w-full">
            <ShareBar share={shareOf(first.score, second.score)} tone="hero" />
          </Rise>
        }
      />
      <Rise step={3}>
        <p className="m-0 max-w-measure text-lead leading-body text-ink-2" {...textId("blurb", blurb)}>{blurb}</p>
      </Rise>
    </div>
  );
}
