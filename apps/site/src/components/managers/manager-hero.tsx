/**
 * The hero of a manager page: the large avatar, the team name, the owner, the record, and the standing.
 * Under it sit the three numbers, the grade, the playoff odds, and the power rank, each with one quiet line of context.
 */
import type { ReactNode } from "react";
import { Reveal } from "@/components/parts/reveal";
import { Avatar } from "@cpc/league/avatar";
import { Chapter } from "@/components/parts/chapter";
import { ordinal, record } from "@/lib/format/format";
import { DURATION, REVEAL_STAGGER } from "@/lib/motion";
import type { Manager, ManagerGrade } from "@/lib/manager-types";
import { GradeMark, GradePopover } from "./grade-popover";
import { OddsCount } from "./odds-count";

/* A change in words. Positive is up, so the odds change and the rank movement read the same way. */
function changeWords(change: number): string {
  if (change === 0) return "no change";
  return change > 0 ? `up ${change}` : `down ${Math.abs(change)}`;
}

/* The depth words in short form, one per slot rank in the file's order, such as "QB fine · RB deep · WR thin · TE deep". */
function depthWords(grade: ManagerGrade): string {
  return grade.slots.map((slot) => `${slot.position} ${slot.depth}`).join(" · ");
}

/* One number: one quiet label over it, the number as the one emphasis, and at most one quiet line under it.
   The mark, when given, sits beside the label. */
function SeasonNumber({
  label,
  mark,
  children,
  context,
}: {
  label: string;
  mark?: ReactNode;
  children: ReactNode;
  context?: ReactNode;
}) {
  return (
    <div className="min-w-0">
      <dt className="text-label leading-tight font-semibold tracking-caps text-mute uppercase">
        {label}
        {mark}
      </dt>
      <dd className="m-0 mt-sp-2 text-score leading-none font-extrabold text-ink tabular-nums">{children}</dd>
      {context && <dd className="m-0 mt-sp-1 text-meta text-mute">{context}</dd>}
    </div>
  );
}

/* A place out of the league, such as "4th of 12". The place is the emphasis, so "of 12" stays small and quiet. */
function Place({ place, of }: { place: number; of: number }) {
  return (
    <>
      {ordinal(place)}
      <span className="text-meta font-semibold text-mute">{` of ${of}`}</span>
    </>
  );
}

export function ManagerHero({ manager, avatar, teams }: { manager: Manager; avatar: string; teams: number }) {
  const { grade, odds, rank } = manager;
  return (
    // The hero shows at once with the masthead, so it takes no reveal.
    <Chapter>
      <div className="flex items-center gap-sp-4">
        {/* The team name sits next to the avatar, so the image is decorative. */}
        <Avatar src={avatar} size="headshot" />
        <div className="min-w-0">
          {/* The name wraps and never truncates. The balance splits a long name into even lines. */}
          <h1 className="m-0 text-stat leading-tight font-extrabold text-balance text-ink tablet:text-score">
            {manager.team.name}
          </h1>
          <div className="mt-sp-1 text-meta text-mute">{manager.team.owner}</div>
          <div className="mt-sp-1 text-body text-ink-2 tabular-nums">
            <span className="font-semibold text-ink">{record(manager.wins, manager.losses)}</span>
            {` · ${ordinal(manager.standing)} of ${teams}`}
          </div>
        </div>
      </div>
      {/* The rule and the space above it set the numbers apart from the team, so the hero reads as two groups.
          At the desktop tier the grade column takes the width of its depth line, so the four positions fit one line.
          A third of the column is 219px there, and the depth line is about 238px. On a phone the depth line may wrap. */}
      <dl
        role="group"
        aria-label="Hero Numbers"
        className="m-0 mt-sp-5 grid grid-cols-3 gap-sp-4 border-t border-rule pt-sp-5 desktop:grid-cols-[max-content_1fr_1fr]"
      >
        {/* The letter stays one plain element in one place, so the grade motion targets it. */}
        {/* On load the letter fades and rises into place with the hero timing, and the depth line follows one stagger later.
            The rise is the quieter choice over a scale, because the large letter would grow at every edge. */}
        {/* The letter opens the grade popover, and the mark beside the label says so. With no grade the dash stays plain. */}
        <SeasonNumber
          label="Grade"
          mark={grade ? <GradeMark /> : null}
          context={
            grade ? (
              <Reveal trigger="mount" delay={REVEAL_STAGGER} duration={DURATION.hero}>
                {depthWords(grade)}
              </Reveal>
            ) : null
          }
        >
          {grade ? (
            <Reveal trigger="mount" duration={DURATION.hero}>
              <GradePopover grade={grade} teams={teams} />
            </Reveal>
          ) : (
            "—"
          )}
        </SeasonNumber>
        <SeasonNumber label="Playoff Odds" context={odds && manager.odds_change !== null ? changeWords(manager.odds_change) : null}>
          {odds ? <OddsCount value={odds.playoff} /> : "—"}
        </SeasonNumber>
        <SeasonNumber label="Power Rank" context={rank !== null && manager.movement !== null ? changeWords(manager.movement) : null}>
          {rank !== null ? <Place place={rank} of={teams} /> : "—"}
        </SeasonNumber>
      </dl>
    </Chapter>
  );
}
