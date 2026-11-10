/**
 * The analyzer result from one analyze document, in one column: the Lean on its scale, the Case, the fairness line, the swap card, and one tab per side.
 * The trade finder reuses SwapCard, FairnessBlock, and AsOfLine. No letter grade shows anywhere.
 */
"use client";

import { motion } from "framer-motion";
import { useId, useState, type ReactNode } from "react";
import type { AnalyzeResponse, AsOf, DecidedSide, Fairness, Lean, TradeSide, TradedPlayer } from "../lib/analyze-types";
import { knownGamesSegments } from "../lib/known-games-segments";
import { BulletRows } from "./bullet-rows";
import { SideTabs } from "./side-tabs";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { DURATION, rise } from "@cpc/design/lib/motion";
import { Blurb } from "@cpc/design/parts/blurb";
import { Card } from "@cpc/design/parts/card";
import { Chapter } from "@cpc/design/parts/chapter";
import { Hero } from "@cpc/design/parts/hero";
import { Headshot } from "@cpc/league/headshot";
import { Label } from "@cpc/design/parts/label";
import { cn } from "@cpc/design/lib/utils";
import { stableId, textId, TRADE_ANSWER, TRADE_KEY } from "@cpc/design/lib/stable-id";

/* A trade side with the asker flag. The swap card and the fairness line need no more, so the finder cards reuse them with a side that has no read. */
export type SwapSide = TradeSide & { mine: boolean };

/* A trade side joined to its read, so each side reads from one object. */
type Side = SwapSide & DecidedSide;

/* Join the trade sides to the read sides by roster id. The asker's side goes first, so the Lean and "Your Side" name the same team. */
function joinSides(doc: AnalyzeResponse): Side[] {
  const sides = doc.trade.sides.flatMap((trade) => {
    const decided = doc.sides.find((s) => s.roster_id === trade.roster_id);
    return decided ? [{ ...trade, ...decided, mine: trade.roster_id === doc.trade.asker }] : [];
  });
  return sides.sort((a, b) => Number(b.mine) - Number(a.mine));
}

/* The small caps style of the table and the swap card. A className adds a color or a layout class. */
function Caps({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={cn("text-label font-bold tracking-caps text-mute uppercase", className)}>{children}</span>;
}

/* The move of a player in the swap card with three or more sides: "To" or "From", and the team. */
type Move = { word: "To" | "From"; team: string };

/* The ranks of a traded player: the Season rank, then the Recent rank with its label only when the document sends one. */
function rankLine(player: TradedPlayer): string | null {
  if (!player.season_rank) return null;
  return player.recent_rank
    ? `Season rank ${player.season_rank} · Recent rank ${player.recent_rank}`
    : `Season rank ${player.season_rank}`;
}

/* move names the team the player goes to or comes from. Only the swap card with three or more sides passes one.
   ranks shows the rank line. Only the side card passes it, so the swap card and the finder cards show no rank. */
function PlayerChip({ player, move, ranks }: { player: TradedPlayer; move?: Move; ranks?: boolean }) {
  const line = ranks ? rankLine(player) : null;
  return (
    <li className="flex flex-col items-center overflow-hidden rounded-card bg-page px-sp-2 pt-sp-2 pb-sp-3 text-center">
      {/* The cutout fills the chip edge to edge, so the chip reads as a card for that player. The name names it, so the image is decorative. */}
      <Headshot
        src={player.headshot}
        lazy
        className="-mx-sp-2 -mt-sp-2 mb-sp-2 block h-headshot self-stretch border-b-2 border-accent bg-linear-to-b from-card to-page object-contain object-bottom"
      />
      <b className="text-row leading-tight font-extrabold tracking-snug">{player.name}</b>
      <span className="py-sp-1 text-meta text-mute">
        {player.position} · {player.nfl_team}
      </span>
      {line && <span className="text-meta text-ink-2">{line}</span>}
      {/* A long team name wraps under the name, so the tag never clips at the phone width. */}
      {/* The word is a muted caps label and the team keeps its own case, so a team name that starts with "To" reads apart.
          The space between the two spans keeps the text "To <Team>" for a screen reader. */}
      {move && (
        <span className="text-meta leading-tight break-words">
          <Caps>{move.word}</Caps> <span className="font-bold text-ink">{move.team}</span>
        </span>
      )}
    </li>
  );
}

/* One column of the swap card. The column spans the card's three rows, so a long team name pushes both columns' chips down together. */
function SwapColumn({ side }: { side: SwapSide }) {
  return (
    <div className="row-span-3 grid min-w-0 grid-rows-subgrid gap-y-0">
      <div className="text-center text-meta leading-tight font-extrabold hyphens-auto">{side.team}</div>
      <span className="mt-sp-2 mb-sp-1 justify-self-center text-label font-bold tracking-wide text-mute uppercase">
        {side.mine ? "You Get" : "Gets"}
      </span>
      <ul className="m-0 flex list-none flex-col gap-sp-2 p-0">
        {side.gets.map((player) => (
          <PlayerChip key={player.player_id} player={player} />
        ))}
      </ul>
    </div>
  );
}

/* The team name of a roster id, or none when the document lacks the id or the id names no side. An old document has no to and no from, so its chips show no tag. */
function teamOf(sides: SwapSide[], rosterId: number | undefined): string | undefined {
  return rosterId === undefined ? undefined : sides.find((s) => s.roster_id === rosterId)?.team;
}

/* The chips of one half of a row. They wrap into as many columns as fit, so a row never scrolls sideways at the phone width. */
function ChipGroup({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="min-w-0">
      <span className="mb-sp-1 block text-label font-bold tracking-wide text-mute uppercase">{label}</span>
      <ul className="m-0 grid list-none grid-cols-[repeat(auto-fill,minmax(9rem,1fr))] gap-sp-2 p-0">{children}</ul>
    </div>
  );
}

/* One row of the swap card with three or more sides: the team, what it gives, and what it gets.
   A phone stacks the gives over the gets. From the tablet tier they sit side by side in two equal columns. */
function SwapRow({ side, sides }: { side: SwapSide; sides: SwapSide[] }) {
  return (
    <div role="group" aria-label={side.team} className="flex flex-col gap-sp-3 border-b border-divider pb-sp-4 last:border-b-0 last:pb-0">
      <div className="text-meta leading-tight font-extrabold hyphens-auto">{side.team}</div>
      <div className="flex flex-col gap-sp-3 tablet:grid tablet:grid-cols-2 tablet:gap-x-sp-4">
        <ChipGroup label={side.mine ? "You Give" : "Gives"}>
          {side.gives.map((player) => {
            const team = teamOf(sides, player.to);
            return <PlayerChip key={player.player_id} player={player} move={team ? { word: "To", team } : undefined} />;
          })}
        </ChipGroup>
        <ChipGroup label={side.mine ? "You Get" : "Gets"}>
          {side.gets.map((player) => {
            const team = teamOf(sides, player.from);
            return <PlayerChip key={player.player_id} player={player} move={team ? { word: "From", team } : undefined} />;
          })}
        </ChipGroup>
      </div>
    </div>
  );
}

export function SwapCard({ sides }: { sides: SwapSide[] }) {
  // An arrow fits two sides only, so three or more sides read as one row per side, in the order given.
  if (sides.length > 2) {
    return (
      <div className="flex flex-col gap-sp-4 rounded-card bg-card p-sp-3" {...stableId("swap-card")}>
        {sides.map((side) => (
          <SwapRow key={side.roster_id} side={side} sides={sides} />
        ))}
      </div>
    );
  }
  const [left, right] = sides;
  return (
    <div className="rounded-card bg-card p-sp-3" {...stableId("swap-card")}>
      <div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] gap-x-sp-2 gap-y-sp-4">
        <SwapColumn side={left} />
        {/* The divider runs the full card height. The tag sits on it, level with the team names. */}
        <div className="relative row-span-3 flex flex-col items-center before:absolute before:inset-y-0 before:left-1/2 before:w-px before:bg-divider before:content-['']">
          <span className="relative mt-sp-5 rounded-sm bg-accent p-sp-1 text-label font-extrabold tracking-caps text-on-dark uppercase">
            For
          </span>
        </div>
        <SwapColumn side={right} />
      </div>
    </div>
  );
}

/* The Lean word sits on the hero, so each color is one that the band holds in both themes. A yes leans in the accent, a no in the plain ink. */
const LEAN_COLOR: Record<Lean, string> = {
  "Send it": "text-accent-text",
  "Lean yes": "text-accent-text",
  "Gut call": "text-on-dark-2",
  "Lean no": "text-on-dark",
  Pass: "text-on-dark",
};

/* The egg hunt reads the answer of the result as yes, no, or not as is, so each Lean maps to one of the three. */
const LEAN_ANSWER: Record<Lean, "yes" | "no" | "not_as_is"> = {
  "Send it": "yes",
  "Lean yes": "yes",
  "Gut call": "not_as_is",
  "Lean no": "no",
  Pass: "no",
};

/* The five Leans from the no end to the yes end, so the lit step shows how strong the call is. */
const SCALE: readonly Lean[] = ["Pass", "Lean no", "Gut call", "Lean yes", "Send it"];

/* The 5-step scale under the Lean word. The lit step carries aria-current, so a screen reader hears which step the Lean is.
   The scale sits on the hero, so each color is a hero role. The plate keeps the glow and the grid off the labels. */
function LeanScale({ lean }: { lean: Lean }) {
  return (
    <ol aria-label="The Lean scale" className="plate m-0 grid max-w-measure list-none grid-cols-5 gap-x-sp-1">
      {SCALE.map((step) => {
        const lit = step === lean;
        return (
          <li key={step} aria-current={lit ? "step" : undefined} className="flex flex-col gap-sp-1">
            <span aria-hidden="true" className={cn("block h-sp-1 rounded-pill", lit ? "bg-accent" : "bg-rule-dark")} />
            <span
              className={cn(
                "text-center text-label leading-tight font-bold tracking-caps uppercase",
                lit ? "text-on-dark" : "text-on-dark-muted",
              )}
            >
              {step}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

/* The Case under the scale. A phone clamps it to 3 lines, so the page stays short, and the button opens the rest.
   From the tablet tier the Case shows in full and the button hides. The button goes once the Case is open, because
   nothing is left to read. The plate sits on the wrapper, so the clamp clips the text and not the plate. */
function CaseText({ readCase }: { readCase: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className="flex flex-col items-start gap-sp-1">
      <div className="plate max-w-measure">
        <p
          id={id}
          className={cn("m-0 text-lead leading-body text-on-dark-2", !open && "max-tablet:line-clamp-3")}
          {...textId("blurb", readCase)}
        >
          {readCase}
        </p>
      </div>
      {!open && (
        <button
          type="button"
          aria-expanded={false}
          aria-controls={id}
          onClick={() => setOpen(true)}
          className="press plate min-h-touch cursor-pointer text-meta font-bold text-accent-text underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent-text tablet:hidden"
        >
          Read the full case
        </button>
      )}
    </div>
  );
}

/* The read fills the hero slots: the side as the eyebrow and the Lean word as the title. The feature holds the rest
   in the order of decision 05: the scale, the Case, then the fairness line. Each chapter of the result opens with a
   level-two heading, so the title is level two. The Lean word rises in once, so the call lands with a beat. With
   motion off, it shows at rest at once. The no-values note and the fairness block sit on a card under the Case, so
   their text keeps the colors of the card. The read has no stats and no action, so the hero shows no empty area. */
function ReadHero({
  lean,
  readCase,
  team,
  asOf,
  sides,
  fairness,
}: {
  lean: Lean;
  readCase: string;
  team?: string;
  asOf: AsOf;
  sides: SwapSide[];
  fairness?: Fairness | null;
}) {
  const off = useMotionOff();
  const note = asOf.no_chart && asOf.no_chart_note;
  const card =
    note || fairness ? (
      <Card>
        <NoChartLine asOf={asOf} />
        {/* The ticket asks the page to render a document with no block, as a guard, so it shows no line then. */}
        {fairness && (
          <div className={note ? "mt-sp-4" : undefined}>
            <FairnessBlock sides={sides} fairness={fairness} />
          </div>
        )}
      </Card>
    ) : null;
  return (
    <Hero
      label="The Read"
      level={2}
      eyebrow={`The read for ${team ?? "Your Side"}`}
      title={
        <motion.span className={cn("inline-block", LEAN_COLOR[lean])} {...stableId("verdict-word")} {...rise(off, { duration: DURATION.decision })}>
          {lean}
        </motion.span>
      }
      feature={
        <div className="flex flex-col gap-sp-4">
          <LeanScale lean={lean} />
          <CaseText readCase={readCase} />
          {card}
        </div>
      }
    />
  );
}

/* The page words of the fairness states. The glossary says "Good for both" on the page, never "win-win".
   Each state has a short meaning, because one word alone does not tell the reader what it means. */
const FAIRNESS_WORD = {
  win_win: { word: "Good for both", color: "text-accent-ink", meaning: "Every side gets more than it gives." },
  fair: {
    word: "Fair",
    color: "text-mute",
    meaning: "No side gives much more than it gets, so every side can take it without a loss.",
  },
  lopsided: { word: "Lopsided", color: "text-ink", meaning: "It gives more than it gets." },
} as const;

/* The fairness line rises in like the Lean word, so both read as one call. With motion off, it shows at rest at once. */
export function FairnessBlock({ sides, fairness }: { sides: SwapSide[]; fairness: Fairness }) {
  const off = useMotionOff();
  const state = FAIRNESS_WORD[fairness.state];
  // A lopsided line names the side that gives more, so the reader knows who loses. The type says a lopsided block always has gives_more, and the pipeline sets it to a side of the trade.
  // "Both" fits two sides only, so a win-win trade of three or more sides says "Good for all".
  const word = fairness.state === "win_win" && sides.length > 2 ? "Good for all" : state.word;
  const line =
    fairness.state === "lopsided"
      ? `${word}: ${sides.find((s) => s.roster_id === fairness.gives_more)!.team} gives more.`
      : word;
  return (
    <div>
      {/* The line is a pill next to its label, so the finder cards and the read show the fairness at a glance. */}
      <div className="mb-sp-2 flex flex-wrap items-center gap-sp-2">
        <span className="font-mono text-meta leading-tight font-bold tracking-wide text-mute uppercase">Fairness</span>
        {/* The pill is a short label, not prose, so it is a span at the row size. */}
        <motion.span
          className={cn("m-0 rounded-pill border border-rule px-sp-3 py-sp-1 text-row leading-tight font-extrabold tracking-snug", state.color)}
          {...rise(off, { duration: DURATION.fairness })}
        >
          {line}
        </motion.span>
      </div>
      <p className="mt-0 mb-sp-3 text-lead text-mute">{state.meaning}</p>
      <ul className="m-0 flex list-none flex-col gap-sp-2 p-0">
        {/* joinSides puts the asker's side first, so the reasons take that order. A finder card sorts its sides the same way. */}
        {sides.map((side) => (
          <li key={side.roster_id}>
            <Caps className="mb-sp-1 block">{side.team}</Caps>
            <Blurb>{fairness.sides.find((f) => f.roster_id === side.roster_id)?.reason}</Blurb>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* The players a side gets and gives. A phone stacks the two groups. From the tablet tier they stand next to each other. */
function SidePlayers({ side }: { side: Side }) {
  return (
    <div className="flex flex-col gap-sp-3 tablet:grid tablet:grid-cols-2 tablet:gap-x-sp-4">
      <ChipGroup label={side.mine ? "You Get" : "Gets"}>
        {side.gets.map((player) => (
          <PlayerChip key={player.player_id} player={player} ranks />
        ))}
      </ChipGroup>
      <ChipGroup label={side.mine ? "You Give" : "Gives"}>
        {side.gives.map((player) => (
          <PlayerChip key={player.player_id} player={player} ranks />
        ))}
      </ChipGroup>
    </div>
  );
}

/* The box of the Week lines: one line for the trade week and one for the next week. It shows before a tap, because a team in a playoff spot reads it first. */
function WeekLines({ side }: { side: Side }) {
  return (
    // A region, not a section, because each section of the view is one chapter.
    <div role="region" aria-label="This week and next" className="mt-sp-4 border border-rule px-sp-3 py-sp-2">
      <Caps className="text-ink">This week and next</Caps>
      <ul className="mt-sp-2 mb-0 flex max-w-measure list-none flex-col gap-sp-1 p-0 text-meta text-ink-2">
        {side.week_lines.map((line) => (
          <li key={line.week}>{line.text}</li>
        ))}
      </ul>
    </div>
  );
}

/* The panel of one side: the players, then the Bullets with their Marks, then the Week lines. The tab names the team. */
function SideRead({ side }: { side: Side }) {
  return (
    <div>
      <SidePlayers side={side} />

      <div className="mt-sp-4">
        <BulletRows bullets={side.bullets} idBase={side.roster_id} />
      </div>

      <WeekLines side={side} />
    </div>
  );
}

/* The reader's locale formats the time, so each manager sees the fetch time in a familiar form.
   The finder document carries the same as_of block, so the finder page shows the same line. */
export function AsOfLine({ doc }: { doc: { as_of: AsOf; stale: string[] } }) {
  const { as_of, stale } = doc;
  const tradeWeek = as_of.known_games?.week ?? as_of.stats_through + 1;
  // Stats that failed to fetch leave the line stale, so the line says so.
  const staleSegments = stale.includes("stats") ? [`Week ${tradeWeek} stats not fetched`] : [];
  // The line names no chart week, because no page text names the source of the player values.
  // The line is a list of facts, not prose, so it is a div at the meta size.
  return (
    <div className="m-0 text-meta text-mute tabular-nums">
      {[...knownGamesSegments(as_of), ...staleSegments].join(" · ")}
      {as_of.rosters_fetched !== null && <RostersFetched iso={as_of.rosters_fetched} />}
    </div>
  );
}

/* The fetch time of the rosters, in the reader's locale. */
function RostersFetched({ iso }: { iso: string }) {
  const fetched = new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
  return (
    <>
      {" · rosters fetched "}
      {/* The build and the browser can format the time apart, so a static render must not warn about it. */}
      <time dateTime={iso} suppressHydrationWarning>
        {fetched}
      </time>
    </>
  );
}

/* A week with no player values gets one line of prose that says so. A document without the flag shows nothing. */
export function NoChartLine({ asOf }: { asOf: AsOf }) {
  if (!asOf.no_chart || !asOf.no_chart_note) return null;
  return <p className="m-0 pt-sp-3 text-lead text-mute">{asOf.no_chart_note}</p>;
}

/* The key of a trade: each side by roster id, with the ids of the players it gives in order, as "3:4046,4881|12:6794".
   One trade always gives one key, whatever the order of the form, so the egg hunt can match one exact trade. */
export function tradeKey(doc: AnalyzeResponse): string {
  return [...doc.trade.sides]
    .sort((a, b) => a.roster_id - b.roster_id)
    .map((side) => `${side.roster_id}:${side.gives.map((player) => player.player_id).sort().join(",")}`)
    .join("|");
}

export default function AnalyzeResult({ doc }: { doc: AnalyzeResponse }) {
  const sides = joinSides(doc);
  const askerTeam = sides.find((s) => s.roster_id === doc.trade.asker)?.team;

  /* From the tablet tier a chapter is a card, and a one-line card looks odd. So the short parts join the chapter they belong to, and the result has four chapters.
     The result sits in one wrapper inside the main, so it sets the card gap between its own chapters. */
  return (
    // The root carries the trade key and the answer of the Lean, so the egg hunt reads them as a condition.
    <div className="tablet:flex tablet:flex-col tablet:gap-card-gap" {...{ [TRADE_KEY]: tradeKey(doc), [TRADE_ANSWER]: LEAN_ANSWER[doc.lean] }}>
      <ReadHero lean={doc.lean} readCase={doc.case} team={askerTeam} asOf={doc.as_of} sides={sides} fairness={doc.fairness} />

      <Chapter>
        <Label heading>The Trade</Label>
        <SwapCard sides={sides} />
      </Chapter>

      {/* One tab per team under the swap card. joinSides puts the asker first, so the tab of the asker opens first. */}
      <Chapter>
        <Label heading>The Sides</Label>
        <SideTabs label="The sides" tabs={sides.map((side) => ({ key: side.roster_id, label: side.team, panel: <SideRead side={side} /> }))} />
      </Chapter>

      {/* The API returns no counters yet. The slot holds their place under the sides. */}
      <Chapter>
        <Label heading>Suggested Counters</Label>
        <Blurb>No counters yet.</Blurb>
        <div className="mt-sp-4">
          <AsOfLine doc={doc} />
        </div>
      </Chapter>
    </div>
  );
}
