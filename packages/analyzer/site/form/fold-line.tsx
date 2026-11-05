/**
 * The folded form of the Stack: one line with a face for each team, the word "For", and what Your Team gives for what it gets.
 * It stands in for the form while a grade runs and under a result. The Edit button opens the form again.
 */
"use client";

import { Avatar } from "@cpc/league/avatar";
import { AVATAR_FALLBACK } from "@cpc/league/images";
import { Card } from "@cpc/design/parts/card";
import type { Team } from "../lib/api";

type FoldLineProps = {
  // Your Team, the asker, and the teams of the other sides, in the order of the form.
  asker: Team | undefined;
  others: Team[];
  // The names of the players Your Team gives, then of the players it gets.
  gives: string[];
  gets: string[];
  // Set once a result shows. The grade locks the form, so the line has no Edit button while it runs.
  onEdit?: () => void;
};

/* "A", "A and B", or "A, B, and C", so the line reads as a sentence. */
function joinNames(names: string[]): string {
  if (names.length < 3) return names.join(" and ");
  return `${names.slice(0, -1).join(", ")}, and ${names.at(-1)}`;
}

/* The face of a team, with a ring of the card color, so faces that overlap stay apart. */
const FACE = "flex-none rounded-full border-2 border-card bg-page object-cover";

export function FoldLine({ asker, others, gives, gets, onEdit }: FoldLineProps) {
  return (
    <Card className="mt-sp-5 py-sp-2 pr-sp-2">
      <div role="group" aria-label="The trade" className="flex min-h-touch items-center gap-sp-3">
        {asker && <Avatar src={asker.avatar ?? AVATAR_FALLBACK} className={FACE} />}
        <span className="font-mono text-meta font-bold tracking-wide text-accent-ink uppercase">For</span>
        <span className="flex flex-none">
          {others.map((team, i) => (
            <Avatar key={team.roster_id} src={team.avatar ?? AVATAR_FALLBACK} className={i === 0 ? FACE : `${FACE} -ml-sp-2`} />
          ))}
        </span>
        <span className="min-w-0 flex-1 text-meta leading-tight text-ink-2">
          {joinNames(gives)} for {joinNames(gets)}
        </span>
        {onEdit && (
          <button
            type="button"
            onClick={onEdit}
            aria-label="Edit the trade"
            className="press min-h-touch flex-none cursor-pointer rounded-pill border border-rule px-sp-4 text-meta font-bold text-ink hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Edit
          </button>
        )}
      </div>
    </Card>
  );
}
