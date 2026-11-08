/**
 * The Game Changer chapter: the player in a round photo frame, the team line, three tiles for scored, projected,
 * and over, then the blurb.
 */
import { gap, num } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { Tile } from "@cpc/design/parts/tile";
import type { GameChanger as GameChangerData, HeadshotMap } from "../schema/week-types";
import { photoOf } from "../parts/photo";
import { WeekChapter } from "../parts/week-chapter";
import { textId } from "@cpc/design/lib/stable-id";

/* A player with no projection has no gap, so both tiles show a dash. */
const DASH = "—";

export function GameChanger({
  gameChanger,
  headshots,
  blurb,
}: {
  gameChanger: GameChangerData;
  headshots: HeadshotMap;
  blurb?: string;
}) {
  const line = gameChanger.award.line;
  const tiles = [
    { label: "Scored", value: num(line.points) },
    { label: "Projected", value: line.projection === null ? DASH : num(line.projection) },
    { label: "Over", value: line.projection === null ? DASH : gap(line.points - line.projection) },
  ];
  return (
    <WeekChapter id="game-changer" title="Game Changer">
      <Card className="flex flex-col gap-sp-4">
        <div className="flex items-center gap-sp-4">
          <PhotoFrame src={photoOf(headshots, line.player_id)} name={line.name} size="lg" />
          <div className="min-w-0">
            <div className="text-lead leading-tight font-bold">{line.name}</div>
            {/* One string, so React writes one text node and the browser kerns the line as one run. */}
            <div className="mt-sp-1 text-meta leading-tight text-mute">
              {[line.position, line.nfl_team, gameChanger.team].filter(Boolean).join(" · ")}
            </div>
          </div>
        </div>
        {/* The tiles share one row when each word fits, and a tile wraps to a new row where it does not, as on a phone.
            A tile never shrinks under its longest word, so "Projected" and "+20.44" never split. */}
        <ul className="m-0 flex list-none flex-wrap gap-sp-2 p-0">
          {tiles.map((tile) => (
            <li key={tile.label} className="flex-1">
              <Tile label={tile.label} value={tile.value} className="h-full" />
            </li>
          ))}
        </ul>
        {blurb && <p className="m-0 max-w-measure text-lead leading-body text-ink-2" {...textId("blurb", blurb)}>{blurb}</p>}
      </Card>
    </WeekChapter>
  );
}
