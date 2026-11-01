/**
 * All matchups: one row per game with both teams and scores, and a button that opens the recap panel.
 * It is the one client component of the week page, because the recap button holds open state.
 */
"use client";

import { motion } from "framer-motion";
import { useId, useState } from "react";
import { Reveal } from "@/components/reveal";
import { num, shortName } from "@/lib/format/format";
import { DURATION, EASE_OUT, INSTANT, stagger, useMotionOff } from "@/lib/motion";
import { cn } from "@/lib/utils";
import type { AvatarMap, Matchup, MatchupSide } from "@/lib/week-types";
import { Avatar, avatarSrc, Blurb, Chapter, Label, managerHref, TeamName } from "./parts";

/* The top scorer of one side, or a dash when the side started no one. */
function Star({ side }: { side: MatchupSide }) {
  return (
    <div className="flex-1 rounded-card bg-gry px-sp-3 py-sp-2">
      <span className="block text-label leading-tight tracking-caps text-mute uppercase">{`Top · ${side.team.name}`}</span>
      <b className="mt-sp-0 block text-body leading-tight tabular-nums">
        {side.top ? `${shortName(side.top.name)} ${num(side.top.points)}` : "—"}
      </b>
    </div>
  );
}

function Panel({ matchup }: { matchup: Matchup }) {
  return (
    <div className="pb-sp-3">
      <div className="mb-sp-2 flex gap-sp-2">
        {matchup.sides.map((side) => (
          <Star key={side.team.roster_id} side={side} />
        ))}
      </div>
      {matchup.is_pick ? (
        <Blurb>
          This is the Matchup of the Week. Read the full story at the top.{" "}
          {/* An inline link cannot scale, so the link is an inline block for the press. */}
          <a href="#motw" className="press inline-block text-red-ink underline hover:decoration-2">
            Go to the top story
          </a>
        </Blurb>
      ) : (
        <Blurb>{matchup.recap}</Blurb>
      )}
    </div>
  );
}

function Row({
  matchup,
  avatars,
  index,
  managersHref,
}: {
  matchup: Matchup;
  avatars: AvatarMap;
  index: number;
  managersHref: string | null;
}) {
  const first = index === 0;
  const [open, setOpen] = useState(false);
  const off = useMotionOff();
  const panelId = useId();
  // The JSON puts the winner first. A tie has no winner, so neither side is bold.
  const [winner, loser] = matchup.sides;
  const bold = cn(winner.winner && "font-extrabold text-red-ink");
  const loserHref = managerHref(managersHref, loser.team.roster_id);
  // The panel stays in the DOM when closed, so find-in-page still finds the recap text.
  // Height 0 hides it from sight. aria-hidden and inert hide it from assistive tech and the tab order.
  const panel = (
    // The panel animates height, an exception to the transform and opacity rule. The panel is short and opens
    // on a tap only, and a FLIP of the rows below would move every other matchup.
    <motion.div
      id={panelId}
      aria-hidden={!open}
      inert={!open}
      initial={false}
      animate={open ? { height: "auto", opacity: 1 } : { height: 0, opacity: 0 }}
      transition={off ? INSTANT : { duration: DURATION.collapse, ease: EASE_OUT }}
      className="overflow-hidden"
    >
      <Panel matchup={matchup} />
    </motion.div>
  );
  return (
    // The row is the reveal box, so last:border-b-0 still finds the last row.
    // The label is the first step of the stagger, so the first row is the second.
    <Reveal className="border-b border-rule last:border-b-0" delay={stagger(index + 1)}>
      {/* minmax(0,1fr) keeps both columns equal, even when one name has a long word.
          The chapter label already gives the first row its top space.
          From the tablet tier each half has room for the longest name and score, so the text keeps to one line.
          The truncate style ends a name that is still too long with an ellipsis, so it cannot push the row wide. */}
      <div
        className={cn(
          "grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)] items-center gap-sp-2 pb-sp-2 tabular-nums",
          first ? "pt-0" : "pt-sp-3",
        )}
      >
        <div className="flex min-w-0 items-center gap-sp-2 text-row leading-tight font-semibold hyphens-auto">
          <Avatar src={avatarSrc(avatars, winner.team.roster_id)} />
          <span className="min-w-0 tablet:truncate">
            <span className={bold}>
              <TeamName name={winner.team.name} href={managerHref(managersHref, winner.team.roster_id)} />
            </span> <span className={bold}>{num(winner.score)}</span>
          </span>
        </div>
        <div className="flex min-w-0 items-center justify-end gap-sp-2 text-right text-row leading-tight font-semibold hyphens-auto">
          {/* One string, so React writes one text node, as the old page did. A link splits the score from the name. */}
          <span className="min-w-0 tablet:truncate">
            {loserHref === null ? (
              `${num(loser.score)} ${loser.team.name}`
            ) : (
              <>
                {`${num(loser.score)} `}
                <TeamName name={loser.team.name} href={loserHref} />
              </>
            )}
          </span>
          <Avatar src={avatarSrc(avatars, loser.team.roster_id)} />
        </div>
      </div>
      {/* 44px is the smallest comfortable touch target. The color change on open is instant, so only the press animates.
          The label is in title case, as every button label of the site is. The caps style does not change what a screen reader hears. */}
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen(!open)}
        className={cn(
          "press mb-sp-3 flex min-h-touch w-full cursor-pointer items-center justify-center gap-sp-2 rounded-card border-0 px-sp-3",
          "text-meta font-bold tracking-caps uppercase [-webkit-tap-highlight-color:transparent]",
          open ? "bg-card-blk text-on-dark" : "bg-gry text-red-ink hover:bg-rule",
        )}
      >
        <span>{open ? "Hide Recap" : "Read Recap"}</span>
        {/* A turned square sits low in the line, so a small lift centers it on the text. */}
        <span
          aria-hidden
          className={cn(
            "inline-block size-chevron border-r-2 border-b-2 border-current transition-[translate,rotate] duration-200 ease-out",
            open ? "translate-y-px -rotate-135" : "-translate-y-sp-0 rotate-45",
          )}
        />
      </button>
      {panel}
    </Reveal>
  );
}

/* The label and the rows stagger in one by one, so the chapter itself has no reveal.
   The managers href is the managers index of the season. With null the team names render as plain text.
   The small Top label of the recap panel stays plain text: the winner and the loser names carry the links. */
export function AllMatchups({
  matchups,
  avatars,
  managersHref = null,
}: {
  matchups: Matchup[];
  avatars: AvatarMap;
  managersHref?: string | null;
}) {
  return (
    <Chapter id="matchups">
      <Reveal delay={stagger(0)}>
        <Label heading>All Matchups</Label>
      </Reveal>
      {matchups.map((matchup, i) => (
        <Row key={matchup.id} matchup={matchup} avatars={avatars} index={i} managersHref={managersHref} />
      ))}
    </Chapter>
  );
}
