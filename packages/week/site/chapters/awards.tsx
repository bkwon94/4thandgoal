/**
 * The Awards chapter: a tile for each award with its name, a round photo, the points, and the player, then the blurb.
 * Two tiles sit per row. A tap opens a tile on the Open card to the team and the projection.
 */
import { num } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { OpenCard } from "@cpc/design/parts/open-card";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { Award, HeadshotMap } from "../schema/week-types";
import { photoOf } from "../parts/photo";
import { WeekChapter } from "../parts/week-chapter";

/* The name of the award. It has the full width of the tile, so a long word such as "Underperformer" fits whole. */
function Title({ award }: { award: Award }) {
  return (
    <div className="font-mono text-meta leading-tight font-bold tracking-caps text-accent-ink uppercase">{award.title}</div>
  );
}

/* A tile with no projections this week shows a note in place of the player. It has no detail to open, so it is a plain card. */
function MissingTile({ award }: { award: Award }) {
  return (
    <li className="min-w-0 list-none">
      <Card className="flex h-full flex-col gap-sp-3">
        <Title award={award} />
        <div className="text-meta text-mute">Projections unavailable this week</div>
      </Card>
    </li>
  );
}

/* One award on the Open card. The closed tile is the name, the points beside the photo, and the player.
   The open panel holds the chips: the team, and the projection when the award has one. */
function AwardTile({ award, headshots, index }: { award: Award; headshots: HeadshotMap; index: number }) {
  if (award.missing) return <MissingTile award={award} />;
  const chips = [award.team, ...(award.projection !== null ? [`Proj ${num(award.projection)}`] : [])];
  return (
    <OpenCard
      // The index names the tile, because two weeks can repeat a title but one page never repeats an index.
      panelId={`award-${index}`}
      head={
        <>
          <Title award={award} />
          <span className="flex flex-col gap-sp-1">
            <span className="flex items-center justify-between gap-sp-2">
              <span className="font-mono text-score leading-stat font-bold tabular-nums">{num(award.points)}</span>
              <PhotoFrame src={photoOf(headshots, award.player_id)} name={award.player} size="md" />
            </span>
            <span className="text-body leading-tight font-bold">{award.player}</span>
          </span>
        </>
      }
      chips={chips}
    />
  );
}

export function Awards({ awards, headshots, blurb }: { awards: Award[]; headshots: HeadshotMap; blurb: string }) {
  return (
    <WeekChapter id="awards" title="Awards">
      {/* The tiles start at the top of their row, so an open tile does not stretch the closed tile beside it. */}
      <ul className="m-0 grid grid-cols-2 items-start gap-sp-2 p-0">
        {awards.map((award, index) => (
          <AwardTile key={award.title} award={award} headshots={headshots} index={index} />
        ))}
      </ul>
      <p className="m-0 max-w-measure text-lead leading-body text-ink-2">{blurb}</p>
    </WeekChapter>
  );
}
