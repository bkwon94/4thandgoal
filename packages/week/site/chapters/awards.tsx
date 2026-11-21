/**
 * The Awards chapter: a tile for each award with its name, a round photo, the points, the player, and the team, then the blurb.
 * Each tier has two tiles per row, so the awards read in a grid and the longest award name fits its tile whole.
 */
import { num } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import type { Award, HeadshotMap } from "../schema/week-types";
import { photoOf } from "../parts/photo";
import { WeekChapter } from "../parts/week-chapter";
import { stableId, textId } from "@cpc/design/lib/stable-id";

/* A tile with no projections this week shows a note in place of the player.
   The name of the award has the full width of the tile, so a long word such as "Underperformer" fits whole.
   The photo sits beside the points, and the player and the team have the full width under them. */
function AwardTile({ award, headshots }: { award: Award; headshots: HeadshotMap }) {
  return (
    <li className="min-w-0 list-none" {...stableId("award", award.title)}>
      <Card className="gap-sp-3 flex h-full flex-col">
        <div className="text-meta tracking-caps text-accent-ink font-mono leading-tight font-bold uppercase">
          {award.title}
        </div>
        {award.missing ? (
          <div className="text-meta text-mute">Projections unavailable this week</div>
        ) : (
          <div className="gap-sp-1 flex flex-col">
            <div className="gap-sp-2 flex items-center justify-between">
              <div className="text-score leading-stat font-mono font-bold tabular-nums">
                {num(award.points)}
              </div>
              <PhotoFrame src={photoOf(headshots, award.player_id)} name={award.player} size="md" />
            </div>
            <div className="text-body leading-tight font-bold">{award.player}</div>
            <div className="text-meta text-mute leading-tight tabular-nums">
              {award.projection !== null
                ? `${award.team} · proj ${num(award.projection)}`
                : award.team}
            </div>
          </div>
        )}
      </Card>
    </li>
  );
}

export function Awards({
  awards,
  headshots,
  blurb,
}: {
  awards: Award[];
  headshots: HeadshotMap;
  blurb: string;
}) {
  return (
    <WeekChapter id="awards" title="Awards">
      <ul className="gap-sp-2 m-0 grid grid-cols-2 p-0">
        {awards.map((award) => (
          <AwardTile key={award.title} award={award} headshots={headshots} />
        ))}
      </ul>
      <p
        className="max-w-measure text-lead leading-body text-ink-2 m-0"
        {...textId("blurb", blurb)}
      >
        {blurb}
      </p>
    </WeekChapter>
  );
}
