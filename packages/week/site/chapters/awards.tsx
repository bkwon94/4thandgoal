/**
 * The awards chapter: a grid of tiles, one per award, then the blurb.
 * A phone has two tiles per row; the tablet tier and up have three, so six awards sit in two rows.
 * A tile with no projections this week shows a note in place of the player.
 */
import { Reveal } from "@cpc/design/parts/reveal";
import { num } from "@cpc/design/format/format";
import { stagger } from "@cpc/design/lib/motion";
import type { Award, HeadshotMap } from "../schema/week-types";
import { Blurb } from "@cpc/design/parts/blurb";
import { Chapter } from "@cpc/design/parts/chapter";
import { Headshot } from "@cpc/league/headshot";
import { headshotSrc } from "@cpc/league/images";
import { Label } from "@cpc/design/parts/label";

/* The tile is the reveal box, so the grid still stretches every tile in a row to one height. */
function Tile({ award, headshots, index }: { award: Award; headshots: HeadshotMap; index: number }) {
  return (
    // The label is the first step of the stagger, so the first tile is the second.
    <Reveal className="rounded-card bg-card p-sp-3" delay={stagger(index + 1)}>
      {/* The MVB title takes two lines at phone width. Every title keeps two lines, so names and numbers align across a row. */}
      <Label className="mb-sp-1 min-h-[calc(2em*var(--leading-tight))]">{award.title}</Label>
      {award.missing ? (
        <div className="mt-sp-1 text-meta text-mute tabular-nums">Projections unavailable this week</div>
      ) : (
        <>
          {/* The headshot has no background, so the cutout sits on the card grey. The awards sit below the fold, so the headshot is lazy. */}
          <Headshot src={headshotSrc(headshots, award.player_id)} lazy className="flex-none object-cover mb-sp-2 block size-award rounded-full" />
          <div className="text-body leading-tight font-extrabold">{award.player}</div>
          <div className="mt-sp-1 text-stat leading-stat font-black tabular-nums">{num(award.points)}</div>
          <div className="mt-sp-1 text-meta text-mute tabular-nums">
            {award.projection !== null ? `proj ${num(award.projection)} · ${award.team}` : award.team}
          </div>
        </>
      )}
    </Reveal>
  );
}

/* The label, the tiles, and the blurb stagger in one by one, so the chapter itself has no reveal. */
export function Awards({ awards, headshots, blurb }: { awards: Award[]; headshots: HeadshotMap; blurb: string }) {
  return (
    <Chapter id="awards">
      <Reveal delay={stagger(0)}>
        <Label heading>Awards</Label>
      </Reveal>
      {/* The grid fills a row before the next, so the stagger index still reveals each row left to right. */}
      <div className="grid grid-cols-[1fr_1fr] gap-sp-2 tablet:grid-cols-[1fr_1fr_1fr]">
        {awards.map((award, i) => (
          <Tile key={award.title} award={award} headshots={headshots} index={i} />
        ))}
      </div>
      <Reveal delay={stagger(awards.length + 1)}>
        <Blurb className="mt-sp-3">{blurb}</Blurb>
      </Reveal>
    </Chapter>
  );
}
