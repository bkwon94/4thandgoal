/**
 * The analyzer result from one analyze document, in one column: the Lean on its scale, the Case, the fairness line, the swap card, and one tab per side.
 * It arrives in a staged reveal of about 1 s over the mesh. The trade finder reuses SwapCard and AsOfLine. No letter grade shows anywhere.
 */
"use client";

import { motion } from "framer-motion";
import { useEffect, useId, useState, type ReactNode } from "react";
import type { AnalyzeResponse, AsOf, ReadSide, Fairness, Lean, TradeSide, TradedPlayer } from "../lib/analyze-types";
import { favoredSide } from "../lib/favored-side";
import { knownGamesSegments } from "../lib/known-games-segments";
import { BulletRows } from "./bullet-rows";
import { SideTabs } from "./side-tabs";
import { TradeOnStage, type StageSide } from "./trade-on-stage";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { DURATION, EASE_OUT, INSTANT, rise } from "@cpc/design/lib/motion";
import { Blurb } from "@cpc/design/parts/blurb";
import { Card } from "@cpc/design/parts/card";
import { Chapter } from "@cpc/design/parts/chapter";
import { Hero } from "@cpc/design/parts/hero";
import { HeroMesh } from "@cpc/design/parts/hero-mesh";
import { revealDrive } from "@cpc/design/parts/mesh-canvas";
import { Headshot } from "@cpc/league/headshot";
import { Label } from "@cpc/design/parts/label";
import { cn } from "@cpc/design/lib/utils";
import { stableId, textId, TRADE_ANSWER, TRADE_KEY } from "@cpc/design/lib/stable-id";

/* A trade side with the asker flag. The swap card and the fairness line need no more, so the finder cards reuse them with a side that has no read. */
export type SwapSide = TradeSide & { mine: boolean };

/* A trade side joined to its read, so each side reads from one object. */
type Side = SwapSide & ReadSide;

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
      {/* The cutout fills the chip edge to edge, so the chip reads as a card for that player. The name names it, so the image is decorative.
          max-w-none lifts the max-width of 100% that the base styles set on each image, so the frame stretches into the side margins of the chip. */}
      <Headshot
        src={player.headshot}
        lazy
        className="-mx-sp-2 -mt-sp-2 mb-sp-2 block h-headshot max-w-none self-stretch border-b-2 border-accent bg-linear-to-b from-card to-page object-contain object-bottom"
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

/* The staged reveal, in ms from the moment the grade arrives. The one pulse of the card skeleton in globals.css lasts as
   long as the beat of the cards, so keep the two the same. The Lean word lands first, then the scale fills, then the
   Case and the result cards with the side tabs rise in, so the reader gets the answer before the detail. Each part ends
   by about 1 s. No beat waits on the clock before the Lean word, so a fast grade shows at once. */
const REVEAL = { scale: 200, fill: 260, case: 450, cards: 500 } as const;

/* True once `ms` have passed since the part mounted, and at once with motion off. A part that adds the class of a
   transitions.dev recipe on its beat reads it, as the orchestration of the recipe does. */
function useBeat(ms: number, off: boolean): boolean {
  const [on, setOn] = useState(off);
  useEffect(() => {
    if (off) {
      setOn(true);
      return;
    }
    const timer = setTimeout(() => setOn(true), ms);
    return () => clearTimeout(timer);
  }, [ms, off]);
  return on;
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
   The scale sits on the hero, so each color is a hero role. The glow stays low in the corner, off the labels (ADR 0036).
   In the reveal, the scale fades in on its beat and the accent of the lit step fills from the left, so the eye goes
   from the word to the step. With motion off, it shows at rest. */
function LeanScale({ lean, off }: { lean: Lean; off: boolean }) {
  return (
    <motion.ol
      aria-label="The Lean scale"
      className="m-0 grid max-w-measure list-none grid-cols-5 gap-x-sp-1"
      initial={off ? false : { opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={off ? INSTANT : { duration: 0.2, ease: EASE_OUT, delay: REVEAL.scale / 1000 }}
    >
      {SCALE.map((step) => {
        const lit = step === lean;
        return (
          <li key={step} aria-current={lit ? "step" : undefined} className="flex flex-col gap-sp-1">
            <span aria-hidden="true" className="relative block h-sp-1 overflow-hidden rounded-pill bg-rule-dark">
              {lit && (
                <motion.span
                  data-reveal-part="scale"
                  className="absolute inset-0 origin-left rounded-pill bg-accent"
                  initial={off ? false : { scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={off ? INSTANT : { duration: 0.3, ease: EASE_OUT, delay: REVEAL.fill / 1000 }}
                />
              )}
            </span>
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
    </motion.ol>
  );
}

/* The Case under the scale. A phone clamps it to 3 lines, so the page stays short, and the button opens the rest.
   From the tablet tier the Case shows in full and the button hides. The button goes once the Case is open, because
   nothing is left to read. The wrapper holds the text, so the clamp clips only the text. */
function CaseText({ readCase }: { readCase: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className="flex flex-col items-start gap-sp-1">
      <div className="max-w-measure">
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
          className="press min-h-touch cursor-pointer text-meta font-bold text-accent-text underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent-text tablet:hidden"
        >
          Read the full case
        </button>
      )}
    </div>
  );
}

/* The read fills the hero slots: the side as the eyebrow and the Lean word as the title. The feature holds the rest
   in this order: the trade on the stage, the scale, the Case, then the fairness line. Each chapter of the result opens with a
   level-two heading, so the title is level two. The no-values note and the fairness block sit on a card under the
   Case, so their text keeps the colors of the card. The read has no stats and no action, so the hero shows no empty area.
   The ground is the mesh of the grade wait, and the reveal starts the moment the grade arrives: the lines of the
   favored side flash once, and the mesh dips toward that side and goes flat. The Lean word rises in at once, the scale
   fills on its beat, and the Case rises in with recipe 18 of transitions.dev, the Case first and the card one stagger
   after it. With motion off, the mesh stays still and each part shows at rest, inside the plain fade of the result. */
function ReadHero({
  lean,
  readCase,
  team,
  asOf,
  sides,
  fairness,
  favored,
  stage,
}: {
  lean: Lean;
  readCase: string;
  team?: string;
  asOf: AsOf;
  sides: SwapSide[];
  fairness?: Fairness | null;
  // The index in `sides` of the favored side, or null when no side is favored.
  favored: number | null;
  // The trade on the stage, one row per side in the order of `sides`.
  stage: StageSide[];
}) {
  const off = useMotionOff();
  // The drive starts with the hero, which mounts when the grade arrives, so the flash adds no delay.
  const [drive] = useState(() => revealDrive(performance.now(), favored));
  const caseShown = useBeat(REVEAL.case, off);
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
      art={<HeroMesh drive={drive} />}
      level={2}
      eyebrow={`The read for ${team ?? "Your Side"}`}
      title={
        <motion.span className={cn("inline-block", LEAN_COLOR[lean])} {...stableId("lean-word")} {...rise(off, { duration: DURATION.decision })}>
          {lean}
        </motion.span>
      }
      feature={
        <div className="flex flex-col gap-sp-4">
          {/* The same rows as the wait, asker first, with the faces at rest. The mesh reads the center of each row as the
              place of that side, so the dip of the reveal sits under the row of the favored side. */}
          <TradeOnStage sides={stage} show="tokens" />
          <LeanScale lean={lean} off={off} />
          <div className={cn("t-stagger flex flex-col gap-sp-4", caseShown && "is-shown")}>
            <div className="t-stagger-line t-stagger-line--1">
              <CaseText readCase={readCase} />
            </div>
            {card && <div className="t-stagger-line t-stagger-line--2">{card}</div>}
          </div>
        </div>
      }
    />
  );
}

/* The page words of the fairness states. Each state has a short meaning, because one word alone does not tell the reader what it means. */
const FAIRNESS_WORD = {
  fair: {
    word: "Fair",
    color: "text-mute",
    meaning: "No side gives much more than it gets, so every side can take it without a loss.",
  },
  lopsided: { word: "Lopsided", color: "text-ink", meaning: "It gives more than it gets." },
} as const;

/* The fairness line rises in with the card of the read, in the texts reveal of the Case, so no part sits inside two reveals. */
function FairnessBlock({ sides, fairness }: { sides: SwapSide[]; fairness: Fairness }) {
  const state = FAIRNESS_WORD[fairness.state];
  // A lopsided line names the side that gives more, so the reader knows who loses. The type says a lopsided block always has gives_more, and the pipeline sets it to a side of the trade.
  const word = state.word;
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
        <span className={cn("m-0 rounded-pill border border-rule px-sp-3 py-sp-1 text-row leading-tight font-extrabold tracking-snug", state.color)}>
          {line}
        </span>
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

/* The skeleton of the result cards: one block for each chapter, in the colors of the page. It pulses once, then the
   real cards fade in over it on their beat, as recipe 14 of transitions.dev. A screen reader skips it. */
function CardsSkeleton() {
  return (
    <div aria-hidden="true" className="t-skel-skeleton is-pulsing flex flex-col gap-sp-3 tablet:gap-card-gap">
      {/* The heights follow the swap card, the side tabs, and the counters, so the cards that fade in fill about the same space. */}
      {["11rem", "14rem", "6rem"].map((height) => (
        <div key={height} className="flex flex-col gap-sp-3 px-gutter py-sp-5 tablet:bg-page">
          <span className="block h-sp-3 w-1/4 rounded-pill bg-rule" />
          <span className="block rounded-card bg-raised" style={{ height }} />
        </div>
      ))}
    </div>
  );
}

/* The avatar of each team by roster id. The analyze document carries none, so the form passes the avatars of the teams of
   the league. A team with no avatar shows the default one. */
export default function AnalyzeResult({ doc, avatars = new Map() }: { doc: AnalyzeResponse; avatars?: ReadonlyMap<number, string | null> }) {
  const off = useMotionOff();
  const cardsShown = useBeat(REVEAL.cards, off);
  const sides = joinSides(doc);
  const askerTeam = sides.find((s) => s.roster_id === doc.trade.asker)?.team;
  // The favored roster comes from the Lean of the grade (see favored-side.ts). The hero takes its place in the order of the sides.
  const favoredRoster = favoredSide(doc);
  const favored = favoredRoster === null ? null : sides.findIndex((s) => s.roster_id === favoredRoster);

  /* From the tablet tier a chapter is a card, and a one-line card looks odd. So the short parts join the chapter they belong to, and the result has four chapters.
     The result sits in one wrapper inside the main, so it sets the card gap between its own chapters. */
  return (
    // The root carries the trade key and the answer of the Lean, so the egg hunt reads them as a condition. The attribute data-trade-answer keeps its name, because the eggs read it. The stable id is lean-word.
    // With motion off, the reveal is one plain fade of the whole result, and no part moves.
    <motion.div
      className="tablet:flex tablet:flex-col tablet:gap-card-gap"
      {...{ [TRADE_KEY]: tradeKey(doc), [TRADE_ANSWER]: LEAN_ANSWER[doc.lean] }}
      initial={off ? { opacity: 0 } : false}
      animate={{ opacity: 1 }}
      transition={{ duration: DURATION.page, ease: "easeOut" }}
    >
      <ReadHero
        lean={doc.lean}
        readCase={doc.case}
        team={askerTeam}
        asOf={doc.as_of}
        sides={sides}
        fairness={doc.fairness}
        favored={favored !== null && favored >= 0 ? favored : null}
        stage={sides.map((side) => ({
          id: side.roster_id,
          team: side.team,
          avatar: avatars.get(side.roster_id) ?? null,
          players: side.gets.map((player) => ({ id: player.player_id, name: player.name, headshot: player.headshot })),
        }))}
      />

      <div className={cn("t-skel", cardsShown && "is-revealed")}>
      <CardsSkeleton />
      <div className="t-skel-content tablet:flex tablet:flex-col tablet:gap-card-gap">
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
      </div>
    </motion.div>
  );
}
