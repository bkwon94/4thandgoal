/**
 * The game changer hero: a black chapter with the player cutout on a red glow, the name, and the points.
 * It ports the .stage rules of the source stylesheet; the two gradients live in globals.css.
 */
import { Reveal } from "@/components/parts/reveal";
import { num } from "@/lib/format/format";
import { DURATION, HERO_DELAY } from "@/lib/motion";
import type { GameChanger as GameChangerData, HeadshotMap } from "@/lib/week-types";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Headshot } from "@/components/parts/headshot";
import { headshotSrc } from "@/lib/headshot";
import { Label } from "@/components/parts/label";

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
  return (
    <Chapter dark id="game-changer">
      {/* The stage spans the card edge to edge. The cutout bleeds off the right and bottom edges,
          so the player reads as part of the card and not as a separate image on top.
          From the tablet tier up the stage is two parts at the hero height: the text on the left and the cutout on the right.
          The one row has no minimum, and the stage clips, so a tall cutout never pushes the height. */}
      <div className="stage relative -mx-gutter -mt-sp-5 mb-sp-4 grid overflow-hidden tablet:h-hero-tablet tablet:grid-cols-2 tablet:grid-rows-1 desktop:h-hero-desktop">
        {/* The hero shows in three steps on load: the glow, then the cutout, then the points. The name and the label
            do not move, so the reader can start to read at once. The glow is a backdrop, so it fades in with no rise.
            The chapter has no reveal of its own, so no hero part sits inside two reveals. */}
        {/* From the tablet tier up the glow sits behind the right part only, so it lights the cutout and not the text. */}
        <Reveal
          className="stage-glow tablet:right-0 tablet:h-full tablet:w-1/2"
          trigger="mount"
          rise={false}
          delay={HERO_DELAY.glow}
          duration={DURATION.hero}
        />
        {/* The name wraps inside 60 percent of the card, so a long name never runs under the face.
            From the tablet tier up the left part bounds the name.
            The text aligns to the bottom of the hero, so the points and the cutout share one baseline.
            A balanced wrap keeps a long name from a one-word last line. */}
        <div className="relative z-3 max-w-[60%] px-gutter pt-sp-5 pb-sp-4 [grid-area:1/1] tablet:flex tablet:max-w-none tablet:flex-col tablet:justify-end tablet:pb-sp-6">
          <Label dark heading>Game Changer</Label>
          <div className="m-0 text-score leading-stat font-black text-balance tabular-nums">
            {line.name}
            <small className="mt-sp-1 mb-sp-2 block text-meta font-semibold text-on-dark-muted">
              {/* One string, so React writes one text node and the browser kerns the line as one run. */}
              {[line.position, line.nfl_team, gameChanger.team].filter(Boolean).join(" · ")}
            </small>
          </div>
          <Reveal
            className="m-0 text-hero leading-hero font-black tracking-grade text-accent-text tabular-nums"
            trigger="mount"
            delay={HERO_DELAY.points}
            duration={DURATION.hero}
          >
            {num(line.points)}
          </Reveal>
          {line.projection !== null && (
            <div className="mt-sp-1 text-meta font-semibold text-on-dark-muted">projected {num(line.projection)}</div>
          )}
        </div>
        {/* The reveal box takes the grid place of the cutout, so the cutout keeps its size and its bleed.
            From the tablet tier up the box fills the right part, and the cutout fills the hero height with its bottom on the floor.
            The cover fit crops the sides of the cutout, not the face. The cutout is the top story's image, so it loads first. */}
        <Reveal
          className="relative z-1 -mr-[28%] w-full self-end justify-self-end [grid-area:1/1] tablet:mr-0 tablet:h-full tablet:[grid-area:1/2]"
          trigger="mount"
          delay={HERO_DELAY.cutout}
          duration={DURATION.hero}
        >
          <Headshot
            src={headshotSrc(headshots, line.player_id)}
            priority
            className="flex-none object-cover block h-auto w-full tablet:h-full tablet:object-bottom"
          />
        </Reveal>
      </div>
      {blurb && <Blurb dark>{blurb}</Blurb>}
    </Chapter>
  );
}
