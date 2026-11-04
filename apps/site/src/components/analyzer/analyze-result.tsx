/**
 * The analyzer result from one analyze document: the decision for the asker, the fairness line, the swap card, and a read per side.
 * The trade finder reuses SwapCard, FairnessBlock, and AsOfLine. No letter grade shows anywhere.
 */
"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import type { AnalyzeResponse, AsOf, DecidedSide, Decision, Factor, Fairness, Player, TradeSide } from "@/lib/analyze-types";
import { knownGamesSegments } from "@/lib/format/known-games-segments";
import { useMotionOff } from "@/hooks/use-motion-off";
import { DURATION, rise } from "@/lib/motion";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Headshot } from "@/components/parts/headshot";
import { Label } from "@/components/parts/label";
import { cn } from "@/lib/utils";

/* A trade side with the asker flag. The swap card and the fairness line need no more, so the finder cards reuse them with a side that has no read. */
export type SwapSide = TradeSide & { mine: boolean };

/* A trade side joined to its read, so each side reads from one object. */
type Side = SwapSide & DecidedSide;

/* Join the trade sides to the decided sides by roster id. The decision side goes first, so the decision and "Your Side" name the same team. */
function joinSides(doc: AnalyzeResponse): Side[] {
  const sides = doc.trade.sides.flatMap((trade) => {
    const decided = doc.sides.find((s) => s.roster_id === trade.roster_id);
    return decided ? [{ ...trade, ...decided, mine: trade.roster_id === doc.decision.for_roster }] : [];
  });
  return sides.sort((a, b) => Number(b.mine) - Number(a.mine));
}

/* The small caps style of the table and the swap card. A className adds a color or a layout class. */
function Caps({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={cn("text-label font-bold tracking-caps text-mute uppercase", className)}>{children}</span>;
}

/* The move of a player in the swap card with three or more sides: "To" or "From", and the team. */
type Move = { word: "To" | "From"; team: string };

/* move names the team the player goes to or comes from. Only the swap card with three or more sides passes one. */
function PlayerChip({ player, move }: { player: Player; move?: Move }) {
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
      <div className="flex flex-col gap-sp-4 rounded-card bg-card p-sp-3">
        {sides.map((side) => (
          <SwapRow key={side.roster_id} side={side} sides={sides} />
        ))}
      </div>
    );
  }
  const [left, right] = sides;
  return (
    <div className="rounded-card bg-card p-sp-3">
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

/* The mark of a factor lean. The symbol is decorative, so a screen reader hears the word. */
const MARKS = {
  for: { symbol: "▲", color: "text-accent-ink" },
  against: { symbol: "▼", color: "text-ink" },
  even: { symbol: "–", color: "text-mute" },
} as const;

function Mark({ lean }: { lean: Factor["lean"] }) {
  const mark = MARKS[lean];
  return (
    <span className={cn("text-center font-black", mark.color)}>
      <span aria-hidden="true">{mark.symbol}</span>
      <span className="sr-only">{lean}</span>
    </span>
  );
}

const ANSWER_WORD = {
  yes: { word: "Yes", color: "text-accent-ink" },
  no: { word: "No", color: "text-ink" },
  not_as_is: { word: "Not as is", color: "text-mute" },
} as const;

/* The answer word rises in once, so the call lands with a beat. With motion off, it shows at rest at once. */
function DecisionBlock({ decision, team }: { decision: Decision; team?: string }) {
  const off = useMotionOff();
  const answer = ANSWER_WORD[decision.answer];
  return (
    <div className="border-l-(length:--chap-rule) border-accent py-sp-1 pl-sp-4">
      {/* Each chapter of the result opens with a level-two heading, and the decision chapter opens with this label. */}
      <Label heading>Decision for {team ?? "Your Side"}</Label>
      <motion.p
        className={cn("mt-0 mb-sp-2 text-headline leading-none font-black tracking-grade", answer.color)}
        {...rise(off, { duration: DURATION.decision })}
      >
        {answer.word}
      </motion.p>
      <Blurb>{decision.reason}</Blurb>
    </div>
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

/* The fairness line rises in like the decision word, so both read as one call. With motion off, it shows at rest at once. */
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
      <Label>Fairness</Label>
      <motion.p
        className={cn("mt-0 mb-sp-1 text-row leading-tight font-extrabold tracking-snug", state.color)}
        {...rise(off, { duration: DURATION.fairness })}
      >
        {line}
      </motion.p>
      <p className="mt-0 mb-sp-3 text-meta leading-tight text-mute">{state.meaning}</p>
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

/* The small label over a part of one side. */
function Part({ children }: { children: ReactNode }) {
  return <Caps className="mt-sp-4 mb-sp-2 block text-ink">{children}</Caps>;
}

function SideRead({ side }: { side: Side }) {
  const analysis = side.analysis;
  return (
    <div>
      <Label>
        {side.team}
        {side.mine && " · Your Side"}
      </Label>
      {analysis === null ? (
        <p className="m-0 text-body text-mute">The analysis is unavailable, so the data stands alone.</p>
      ) : (
        <Blurb>{analysis}</Blurb>
      )}

      <Part>The Data</Part>
      <p className="m-0 text-meta leading-tight text-ink-2">{side.chart.reason}</p>

      <Part>The Reasoning</Part>
      <ul className="m-0 list-none border-y-2 border-ink p-0 text-meta leading-tight">
        {side.factors.map((f) => (
          <li
            key={f.name}
            className="grid grid-cols-[var(--spacing-sp-4)_minmax(0,1fr)] gap-x-sp-1 border-b border-rule px-sp-1 py-sp-2 text-ink-2 last:border-b-0"
          >
            <Mark lean={f.lean} />
            <Caps>{f.name}</Caps>
            <span className="col-start-2">{f.reason}</span>
          </li>
        ))}
      </ul>
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
  const chartSegments = as_of.chart_week !== null ? [`Chart week ${as_of.chart_week}`] : [];
  return (
    <p className="m-0 text-meta text-mute tabular-nums">
      {[...knownGamesSegments(as_of), ...staleSegments, ...chartSegments].join(" · ")}
      {as_of.rosters_fetched !== null && <RostersFetched iso={as_of.rosters_fetched} />}
    </p>
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

/* A week with no chart gets one meta line that says so. A document without the flag shows nothing. */
export function NoChartLine({ asOf }: { asOf: AsOf }) {
  if (!asOf.no_chart || !asOf.no_chart_note) return null;
  return <p className="m-0 pt-sp-3 text-meta text-mute">{asOf.no_chart_note}</p>;
}

export default function AnalyzeResult({ doc }: { doc: AnalyzeResponse }) {
  const sides = joinSides(doc);
  const decisionTeam = sides.find((s) => s.roster_id === doc.decision.for_roster)?.team;

  /* From the tablet tier a chapter is a card, and a one-line card looks odd. So the short parts join the chapter they belong to, and the result has five chapters.
     The result sits in one wrapper inside the main, so it sets the card gap between its own chapters. */
  return (
    <div className="tablet:flex tablet:flex-col tablet:gap-card-gap">
      <Chapter>
        <DecisionBlock decision={doc.decision} team={decisionTeam} />
        <NoChartLine asOf={doc.as_of} />
        {/* The fairness line sits under the decision, so the decision stays the lead. The ticket asks the page to render a document with no block, as a guard, so it shows no line then. */}
        {doc.fairness && (
          <div className="mt-sp-5">
            <FairnessBlock sides={sides} fairness={doc.fairness} />
          </div>
        )}
      </Chapter>

      <Chapter>
        <Label heading>The Trade</Label>
        <SwapCard sides={sides} />
      </Chapter>

      {sides.map((side) => (
        <Chapter key={side.roster_id}>
          <SideRead side={side} />
        </Chapter>
      ))}

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
