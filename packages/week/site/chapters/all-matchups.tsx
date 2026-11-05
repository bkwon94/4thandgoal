/**
 * Every game: one card per game, by top score, with both avatars, both scores, and a share bar.
 * A tap on a card opens its recap with a brand edge, the margin, and one link to a manager page.
 */
"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { num } from "@cpc/design/format/format";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { DURATION, INSTANT, RISE, RISE_EASE } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import type { AvatarMap, Matchup, MatchupSide } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import { ShareBar, shareOf } from "../parts/share-bar";
import { WeekChapter } from "../parts/week-chapter";

/* One team of a card. The card is one button, so the name is plain text. A long name cuts at the end of its row. */
function TeamRow({ side, avatars, lead }: { side: MatchupSide; avatars: AvatarMap; lead: boolean }) {
  return (
    <span className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-sp-3">
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} />
      <span className={cn("truncate text-body leading-tight", lead ? "font-bold text-ink" : "text-ink-2")}>
        {side.team.name}
      </span>
      <span className={cn("font-mono text-body tabular-nums", lead ? "font-bold text-ink" : "text-mute")}>
        {num(side.score)}
      </span>
    </span>
  );
}

function GameCard({ matchup, avatars, managersHref }: { matchup: Matchup; avatars: AvatarMap; managersHref: string | null }) {
  const [open, setOpen] = useState(false);
  const off = useMotionOff();
  // The JSON puts the winner first. A tie has no winner, and the first side still leads the card.
  const [first, second] = matchup.sides;
  // The id names the game, so a check of the readability floor can open the recap of one game by its control.
  const panelId = `recap-${matchup.id}`;
  const href = managerHrefOrNull(managersHref, first.team.roster_id);
  return (
    <li data-open={open} className="list-none">
      <Card edge={open} className="overflow-hidden p-0">
        {/* The whole card is one button of 44px or more, so the team names inside it are plain text. */}
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen(!open)}
          className="press flex min-h-touch w-full cursor-pointer flex-col gap-sp-3 border-0 bg-transparent p-sp-4 text-left text-inherit [-webkit-tap-highlight-color:transparent]"
        >
          <TeamRow side={first} avatars={avatars} lead />
          <ShareBar share={shareOf(first.score, second.score)} tone="page" />
          <TeamRow side={second} avatars={avatars} lead={false} />
        </button>
        {/* The panel stays in the DOM when closed, so the button always controls an element. Hidden keeps it from
            sight, from a screen reader, and from the tab order. It opens in 0.3s with transform and opacity only. */}
        <div id={panelId} hidden={!open}>
          {open && (
            <motion.div
              initial={off ? false : { opacity: 0, y: `calc(${RISE} * -1)` }}
              animate={{ opacity: 1, y: 0 }}
              transition={off ? INSTANT : { duration: DURATION.recap, ease: RISE_EASE }}
              className="flex flex-col gap-sp-3 border-t border-rule px-sp-4 pt-sp-3 pb-sp-4"
            >
              <span className="font-mono text-meta leading-tight font-bold tracking-caps text-accent-ink uppercase">
                {`Won by ${num(first.score - second.score)}`}
              </span>
              {matchup.recap !== null && <p className="m-0 max-w-measure text-lead leading-body text-ink-2">{matchup.recap}</p>}
              {/* One link per recap: the manager page of the team that leads the card. It is a full tap target. */}
              {href !== null && (
                <a
                  href={href}
                  className="press inline-flex min-h-touch w-fit items-center rounded-pill border border-rule bg-raised px-sp-5 text-body font-bold text-ink no-underline"
                >
                  Manager page<span className="sr-only">{` of ${first.team.name}`}</span>
                </a>
              )}
            </motion.div>
          )}
        </div>
      </Card>
    </li>
  );
}

/* The top score of a game: the score of its first side, the winner. */
const topScore = (matchup: Matchup) => Math.max(matchup.sides[0].score, matchup.sides[1].score);

/* The managers href is the managers index of the season. With null an open recap has no Manager page link. */
export function AllMatchups({
  matchups,
  avatars,
  managersHref = null,
}: {
  matchups: Matchup[];
  avatars: AvatarMap;
  managersHref?: string | null;
}) {
  const games = [...matchups].sort((a, b) => topScore(b) - topScore(a));
  return (
    <WeekChapter id="matchups" title="Every game" note="Tap for the recap">
      {/* Two cards per row from the tablet tier, so the twelve teams fit in less scroll. */}
      <ul className="m-0 grid grid-cols-1 gap-sp-2 p-0 tablet:grid-cols-2">
        {games.map((matchup) => (
          <GameCard key={matchup.id} matchup={matchup} avatars={avatars} managersHref={managersHref} />
        ))}
      </ul>
    </WeekChapter>
  );
}
