/**
 * The Index list: the ledger of the Managers index, after the method of the Team Roster item (ADR 0028), with the chips of the playoff race.
 * A tap opens a row in place with the Open card, one row at a time, and the name of the open row rolls its letters.
 */
"use client";

import { type CSSProperties, Fragment, useState } from "react";
import { Avatar } from "@cpc/league/avatar";
import { OpenCard } from "@cpc/design/parts/open-card";
import { cn } from "@cpc/design/lib/utils";
import type { ManagerGrade } from "../schema/manager-types";
import { GradeDial } from "./grade-dial";
import type { RaceGroup } from "./race-group";

/* One row of the ledger, as the managers index builds it from a joined manager. The props are plain data (ADR 0012). */
export type IndexRow = {
  id: number;
  // The place in the power ranking of the page week.
  place: number;
  name: string;
  avatar: string;
  href: string;
  // The playoff odds in whole percents, or null when no week has odds.
  odds: number | null;
  group: RaceGroup | null;
  // The facts line of the open row: the record, the power rank, and the playoff odds.
  facts: string;
  grade: ManagerGrade | null;
};

type Filter = "all" | RaceGroup;

const CHIPS: { filter: Filter; label: string }[] = [
  { filter: "all", label: "All" },
  { filter: "in", label: "In" },
  { filter: "bubble", label: "Bubble" },
  { filter: "out", label: "Out" },
];

/* The words of a name, each a run of letters, so a long name wraps between words and never inside one.
   Intl.Segmenter keeps a letter made of two code points, such as an emoji, as one letter. */
function wordsOf(name: string): string[][] {
  const segmenter = new Intl.Segmenter(undefined, { granularity: "grapheme" });
  return name.split(" ").map((word) => [...segmenter.segment(word)].map((part) => part.segment));
}

/* The letter roll of the item: each letter is a one-line window that holds the muted letter and an ink copy under it.
   An open row slides each letter up one line, a letter later than the one before, so the ink name rolls in from the left.
   The copy is CSS content with empty alt text, so the name reads once and the text of the row holds the name once. */
function RollName({ name }: { name: string }) {
  let index = 0;
  return (
    <span className="ix-name">
      {wordsOf(name).map((letters, w) => (
        <Fragment key={w}>
          {w > 0 && " "}
          <span className="ix-word">
            {letters.map((letter) => {
              const i = index++;
              return (
                <span key={i} className="ix-letter" style={{ "--ix-i": i } as CSSProperties}>
                  <span className="ix-glyph" data-ch={letter}>
                    {letter}
                  </span>
                </span>
              );
            })}
          </span>
        </Fragment>
      ))}
    </span>
  );
}

/* The grade of the open row: the letter and the grade read, then the four arcs of the Grade dial in one row. */
function RowGrade({ grade, teams }: { grade: ManagerGrade; teams: number }) {
  return (
    <div className="flex flex-col gap-sp-3">
      <div className="flex items-start gap-sp-3">
        <span
          aria-label={`Grade ${grade.letter}`}
          className="flex size-touch flex-none items-center justify-center rounded-tile border border-accent font-mono text-stat leading-none font-bold text-ink"
        >
          {grade.letter}
        </span>
        <p className="m-0 text-lead leading-body text-ink-2">{grade.read}</p>
      </div>
      <GradeDial parts={grade.parts} teams={teams} size="small" />
    </div>
  );
}

export function IndexList({ rows, teams }: { rows: IndexRow[]; teams: number }) {
  const [filter, setFilter] = useState<Filter>("all");
  const [openId, setOpenId] = useState<number | null>(null);
  const countOf = (chip: Filter) => (chip === "all" ? rows.length : rows.filter((row) => row.group === chip).length);
  const shown = filter === "all" ? rows : rows.filter((row) => row.group === filter);

  // A tap on the pressed chip clears the filter, as in the item. A new filter closes the open row, so no row opens out of view.
  const choose = (chip: Filter) => {
    setFilter(chip === filter ? "all" : chip);
    setOpenId(null);
  };

  return (
    <div className="ix">
      <div role="group" aria-label="Playoff Race" className="flex flex-wrap gap-sp-1">
        {CHIPS.map(({ filter: chip, label }) => {
          const count = countOf(chip);
          const on = chip === filter;
          return (
            <button
              key={chip}
              type="button"
              aria-pressed={on}
              // A chip with no team stays in view with its count of 0, and it cannot be pressed.
              disabled={count === 0}
              onClick={() => choose(chip)}
              className={cn(
                "press inline-flex min-h-touch cursor-pointer items-center rounded-pill border-0 px-sp-4 text-body font-semibold transition-colors duration-300 disabled:cursor-default disabled:opacity-60",
                on ? "bg-ink text-page" : "bg-transparent text-ink-2",
              )}
            >
              {label}
              <sup className="ml-sp-0 font-mono text-meta leading-none tabular-nums">{count}</sup>
            </button>
          );
        })}
      </div>
      {/* The list remounts on a new filter, so the rows of the filter enter again in a stagger, as in the item. */}
      <ul key={filter} aria-label="Index List" className="m-0 mt-sp-3 list-none border-t border-rule p-0">
        {shown.map((row, k) => {
          const open = row.id === openId;
          return (
            <OpenCard
              key={row.id}
              look="row"
              panelId={`index-row-${row.id}`}
              open={open}
              onOpenChange={(next) => setOpenId(next ? row.id : null)}
              // The rule under the open row turns ink, as in the item.
              headClassName={cn("justify-center border-b py-sp-1 transition-colors duration-300", open ? "border-ink" : "border-rule")}
              head={
                // The cells enter a step after the row before, by the index k of the row in the filter.
                <span
                  className="ix-cells grid grid-cols-[1.5rem_auto_minmax(0,1fr)_auto] items-center gap-x-sp-3"
                  style={{ "--ix-k": k } as CSSProperties}
                >
                  <span className="font-mono text-meta text-ink-2 tabular-nums">{row.place}</span>
                  <Avatar src={row.avatar} />
                  <RollName name={row.name} />
                  <span className="font-mono text-body text-ink-2 tabular-nums">{row.odds === null ? "—" : `${row.odds}%`}</span>
                </span>
              }
              overview={row.facts}
              action={{ href: row.href, label: "Manager page", hiddenLabel: ` of ${row.name}` }}
            >
              {row.grade && <RowGrade grade={row.grade} teams={teams} />}
            </OpenCard>
          );
        })}
      </ul>
    </div>
  );
}
