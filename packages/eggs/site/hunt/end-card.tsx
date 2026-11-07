/**
 * The hero card at the end of each path of a find: the claim, the block, another manager first, and the limit of the check.
 * Each card rises in on the hero of the look, and a claim drops the red tile into its slot as the count rises.
 */
"use client";

import type { ReactNode } from "react";
import { Hero } from "@cpc/design/parts/hero";
import { Label } from "@cpc/design/parts/label";
import type { ClaimAnswer } from "../lib/api";
import { ArtGround, SlotRow } from "./egg-art";
import { slotsOf } from "./slots";

/* The end of a path. A claim carries the answer of the API, the gift card of the egg word, and the team. */
export type End =
  | { kind: "claimed"; answer: ClaimAnswer; prize: number | null; team: string }
  | { kind: "claimed-first"; letter: string }
  | { kind: "limit"; minutes: number };

/* The minutes of a wait of the given seconds, at least 1. The check limit is per hour, so a missing wait is 60. */
export function minutesOf(seconds: number | undefined): number {
  return seconds === undefined ? 60 : Math.max(1, Math.ceil(seconds / 60));
}

export function EndCard({ end, onClose }: { end: End; onClose: () => void }) {
  if (end.kind === "limit") {
    return (
      <Shell
        label="Limit"
        title="The eggs need a rest."
        line={`Try again in ${end.minutes} ${end.minutes === 1 ? "minute" : "minutes"}.`}
        onClose={onClose}
      >
        <div className="flex flex-col items-center gap-sp-2 font-mono font-bold">
          <span className="text-hero leading-hero text-accent-text">{end.minutes}</span>
          <span className="text-meta tracking-caps text-on-dark-muted uppercase">Minutes left</span>
        </div>
      </Shell>
    );
  }
  if (end.kind === "claimed-first") {
    return (
      <Shell label="Too late" title="Another manager claimed first." line="The first claim wins the egg." onClose={onClose} board>
        <span className="egg-pop flex size-28 items-center justify-center rounded-letter bg-chip-dark font-mono text-hero leading-hero font-bold text-on-dark-muted line-through decoration-accent decoration-6">
          {end.letter}
        </span>
      </Shell>
    );
  }
  const { answer, prize, team } = end;
  if (answer.word === null) {
    return (
      <Shell
        label="Blocked"
        title={`You hold ${answer.letter} as a block.`}
        line={`No other manager can put this ${answer.letter} in a word.`}
        team={team}
        onClose={onClose}
        board
      >
        <div className="relative size-28">
          <span className="egg-pop absolute inset-0 flex items-center justify-center rounded-letter border-4 border-dashed border-accent bg-band font-mono text-hero leading-hero font-bold text-accent-text">
            {answer.letter}
          </span>
          <span className="egg-stamp absolute -inset-x-3.5 top-10 rounded-letter border-2 border-on-dark bg-accent py-sp-1 font-mono text-lead font-bold tracking-wide text-on-dark">
            BLOCKED
          </span>
        </div>
      </Shell>
    );
  }
  const word = answer.word;
  const letters = answer.letters[word] ?? [];
  // The letters before the claim are the letters after it, less the one new letter.
  const before = [...letters];
  before.splice(before.lastIndexOf(answer.letter), 1);
  const left = word.length - letters.length;
  const won = answer.winner !== null;
  const gift = prize === null ? "gift card" : `$${prize}`;
  return (
    <Shell
      label="Claimed"
      title={won ? `${word} is complete.` : `${answer.letter} goes to ${word}.`}
      line={won ? `The ${gift} gift card is yours.` : `${left} ${left === 1 ? "letter" : "letters"} to go for the ${gift}.`}
      team={team}
      onClose={onClose}
      board
    >
      <div className="flex items-baseline gap-sp-0 font-mono font-bold">
        <span className="egg-tick text-hero leading-hero">{letters.length}</span>
        <span className="text-score text-on-dark-muted">/{word.length}</span>
      </div>
      <SlotRow slots={slotsOf(word, before, answer.letter)} tone="hero" landing />
    </Shell>
  );
}

/* The hero card of an end, with its label, the art of the end, its title and the line under it, the button back to
   the page, and the link to the egg board after a claim. */
function Shell({
  label,
  title,
  line,
  team,
  board = false,
  onClose,
  children,
}: {
  label: string;
  title: string;
  line: string;
  team?: string;
  board?: boolean;
  onClose: () => void;
  children: ReactNode;
}) {
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="egg-end-title" className="fixed inset-0 z-50 grid place-items-center overflow-y-auto p-gutter">
      <div aria-hidden="true" className="egg-scrim fixed inset-0 bg-band/80" />
      <Hero label={label} className="egg-hero egg-hero-in w-full max-w-sm">
        <div className="flex flex-col items-center gap-sp-4 text-center">
          <div className="flex w-full items-center justify-between gap-sp-2">
            <Label dark className="mb-0 text-meta">
              {label}
            </Label>
            {team && (
              <span className="font-mono text-meta font-bold tracking-caps text-on-dark-muted uppercase">{team}</span>
            )}
          </div>
          {/* The ground reaches the edges of the hero, and never above or below the art. */}
          <div className="relative flex flex-col items-center gap-sp-4 self-stretch">
            <ArtGround inset="inset-y-0 -inset-x-hero-x" />
            <div className="relative flex flex-col items-center gap-sp-4">{children}</div>
          </div>
          <div className="egg-fade-in egg-fade-in-late flex flex-col gap-sp-1">
            <h2 id="egg-end-title" className="text-score leading-tight font-bold">
              {title}
            </h2>
            <p className="text-lead text-on-dark-2">
              {line}
            </p>
          </div>
          <div className="flex w-full flex-col items-center gap-sp-2">
            <button
              type="button"
              onClick={onClose}
              className="press min-h-touch w-full rounded-pill bg-on-dark text-lead font-bold text-band"
            >
              Back to the page
            </button>
            {board && (
              <a href="/eggs/" className="inline-flex min-h-touch items-center rounded-pill px-sp-4 text-body font-bold text-accent-text">
                See the egg board
              </a>
            )}
          </div>
        </div>
      </Hero>
    </div>
  );
}
