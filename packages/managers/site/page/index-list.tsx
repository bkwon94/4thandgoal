/**
 * The Index list: the ledger of the Managers index, after the method of the Team Roster item (ADR 0028), with the chips of the playoff race.
 * A tap opens a row in place with the Open card, one row at a time. From the desktop tier a sticky stage sits beside the ledger.
 */
"use client";

import { PendingButton } from "@cpc/design/ui/pending-button";
import { type CSSProperties, Fragment, useState } from "react";
import { Avatar } from "@cpc/league/avatar";
import { OpenCard } from "@cpc/design/parts/open-card";
import { cn } from "@cpc/design/lib/utils";
import type { ManagerGrade } from "../schema/manager-types";
import { GradeDial } from "./grade-dial";
import { IndexStage } from "./index-stage";
import { RACE_WORDS, type RaceGroup } from "./race-group";

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
  { filter: "in", label: RACE_WORDS.in },
  { filter: "bubble", label: RACE_WORDS.bubble },
  { filter: "out", label: RACE_WORDS.out },
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
    <div className="gap-sp-3 flex flex-col">
      <div className="gap-sp-3 flex items-start">
        <span
          aria-label={`Grade ${grade.letter}`}
          className="size-touch rounded-tile border-accent text-stat text-ink flex flex-none items-center justify-center border font-mono leading-none font-bold"
        >
          {grade.letter}
        </span>
        <p className="text-lead leading-body text-ink-2 m-0">{grade.read}</p>
      </div>
      <GradeDial parts={grade.parts} teams={teams} size="small" />
    </div>
  );
}

export function IndexList({ rows, teams }: { rows: IndexRow[]; teams: number }) {
  const [filter, setFilter] = useState<Filter>("all");
  const [openId, setOpenId] = useState<number | null>(null);
  // The row in the stage. A row out of the filter leaves the stage to the first row of the filter, as in the item.
  const [stageId, setStageId] = useState<number | null>(null);
  const countOf = (chip: Filter) =>
    chip === "all" ? rows.length : rows.filter((row) => row.group === chip).length;
  const shown = filter === "all" ? rows : rows.filter((row) => row.group === filter);
  const staged = shown.find((row) => row.id === stageId) ?? shown[0];

  // A tap on the pressed chip clears the filter, as in the item. A new filter closes the open row, so no row opens out of view.
  const choose = (chip: Filter) => {
    setFilter(chip === filter ? "all" : chip);
    setOpenId(null);
  };

  /* From the desktop tier the ledger takes 53% of the width, a gap of 5%, and the stage the rest, as in the item.
     The stage is sticky under the top band. Under the desktop tier the stage is not shown, and the ledger is the page. */
  return (
    // oxlint-disable-next-line design/no-arbitrary-value -- the gap is 5 percent of the width, as in the layout of the item
    <div className="ix desktop:grid desktop:grid-cols-[minmax(0,53fr)_minmax(0,42fr)] desktop:items-start desktop:gap-x-[5%]">
      <div>
        {/* The id is the target of the playoff race Answer of the front door. */}
        <div
          id="race"
          role="group"
          aria-label="Playoff Race"
          className="scroll-mt-band-height gap-sp-1 flex flex-wrap"
        >
          {CHIPS.map(({ filter: chip, label }) => {
            const count = countOf(chip);
            const on = chip === filter;
            return (
              <PendingButton
                key={chip}
                type="button"
                aria-pressed={on}
                // A chip with no team stays in view with its count of 0, and it cannot be pressed.
                disabled={count === 0}
                onClick={() => choose(chip)}
                className={cn(
                  "press min-h-touch rounded-pill px-sp-4 text-body inline-flex cursor-pointer items-center border-0 font-semibold transition-colors duration-300 disabled:cursor-default disabled:opacity-60",
                  on ? "bg-ink text-page" : "text-ink-2 bg-transparent",
                )}
              >
                {label}
                <sup className="ml-sp-0 text-meta font-mono leading-none tabular-nums">{count}</sup>
              </PendingButton>
            );
          })}
        </div>
        {/* The list remounts on a new filter, so the rows of the filter enter again in a stagger, as in the item. */}
        <ul
          key={filter}
          aria-label="Index List"
          className="mt-sp-3 border-rule m-0 list-none border-t p-0"
        >
          {shown.map((row, k) => {
            const open = row.id === openId;
            return (
              <OpenCard
                key={row.id}
                look="row"
                panelId={`index-row-${row.id}`}
                open={open}
                onOpenChange={(next) => setOpenId(next ? row.id : null)}
                onEnter={() => setStageId(row.id)}
                // The rule under the open row turns ink, as in the item. From the desktop tier the rule of the row in the stage turns ink too.
                headClassName={cn(
                  "py-sp-1 justify-center border-b transition-colors duration-300",
                  open ? "border-ink" : "border-rule",
                  row === staged && "desktop:border-ink",
                )}
                head={
                  // The cells enter a step after the row before, by the index k of the row in the filter.
                  // The row in the stage rolls its name from the desktop tier, as the open row does.
                  <span
                    data-staged={row === staged ? "" : undefined}
                    className="ix-cells gap-x-sp-3 grid grid-cols-[1.5rem_auto_minmax(0,1fr)_auto] items-center"
                    style={{ "--ix-k": k } as CSSProperties}
                  >
                    <span className="text-meta text-ink-2 font-mono tabular-nums">{row.place}</span>
                    <Avatar src={row.avatar} />
                    <RollName name={row.name} />
                    <span className="text-body text-ink-2 font-mono tabular-nums">
                      {row.odds === null ? "—" : `${row.odds}%`}
                    </span>
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
      {staged && (
        <div
          data-ix-stage
          // oxlint-disable-next-line design/no-arbitrary-value -- the stage sits one step under the top band, a one-off
          className="desktop:sticky desktop:top-[calc(var(--spacing-band-height)+var(--spacing-sp-4))] desktop:block hidden"
        >
          <IndexStage row={staged} teams={teams} />
        </div>
      )}
    </div>
  );
}
