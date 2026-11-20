/**
 * Find mode of the analyzer: the dark hero with Your team, the partner choice, the position chips, and the find button.
 * The find streams its real steps into the same wait as a grade, and each of up to five Ledger cards lands in one list
 * as the pick sends it, with the near ideas folded under them at the end.
 */
"use client";

import { motion } from "framer-motion";
import { ChevronDown, RotateCcw, Users } from "lucide-react";
import { type ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { AsOfLine, NoChartLine } from "./analyze-result";
import { BulletRows } from "./bullet-rows";
import { Ledger, ledgerOf, NearIdeas } from "./ledger";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { Hero } from "@cpc/design/parts/hero";
import { HeroMesh } from "@cpc/design/parts/hero-mesh";
import { waitDrive } from "@cpc/design/parts/mesh-canvas";
import { Sheet } from "./sheet";
import { StageLines } from "./stage-lines";
import { Button } from "@cpc/design/ui/button";
import { Collapsible, CollapsiblePanel, CollapsibleTrigger } from "@cpc/design/ui/collapsible";
import { PendingButton } from "@cpc/design/ui/pending-button";
import { SegmentedControl, SegmentedControlIndicator, SegmentedControlItem } from "@cpc/design/ui/segmented-control";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { EASE_OUT, SMOOTH_OUT } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import { Avatar } from "@cpc/league/avatar";
import { AVATAR_FALLBACK } from "@cpc/league/images";
import { useRequest } from "./use-request";
import type { FindResponse, FinderTrade, Lean } from "../lib/analyze-types";
import { ApiError, type ApiTarget, type FindRequest, type ShortlistTrade, streamFind, toErrorLine, type Team } from "../lib/api";

// A press can wait on a live fair check while the warm-up of the fair cache runs, and two presses share one Jev
// budget, so the finder waits much longer than a grade before it gives up.
const TIMEOUT_MS = 180_000;

// The steps of a find, in the order the stream sends them: the teams, the trade value match, the fair check, the
// check against both lineups, and the pick. The wait line counts them, so the reader knows how far the search is.
const FIND_STEPS = 5;

// Each step line stays on screen at least 1.5 s, so the reader can read it even when the steps end faster (decision 20).
const STEP_HOLD_MS = 1500;
// The pick thinks for most of the wait, so on step 5 the line names one trade of the Shortlist about every 3 s, long
// enough to read the names, short enough that the wait reads as work (decision 20).
const WEIGH_MS = 3000;
// The most characters of a step 5 line that fit one line of the wait at 390 px: the line box is 309 px there, and the
// body text runs about 7.1 px a character. A longer line takes the last names. A count of characters is plain and needs
// no measure of the font. A trade of five players can run past the box even by last names. StageLines then scrolls it
// once to its end within its hold, or, with motion off, wraps it in full, so no line overlaps another.
const WEIGH_FIT = 42;

// The pick sends up to 5 trades and up to 3 near ideas (decision 17). The page keeps to that count.
const MAX_PICKS = 5;
const MAX_NEAR = 3;

/* The position chips. Any sends no limit. Each other chip sends its position as aim_position, the same field that a
   typed question such as "trade ideas for an RB" sets on the front door. */
const AIMS = ["Any", "RB", "WR", "TE", "QB"] as const;
type Aim = (typeof AIMS)[number];

/* The wait holds each wait line of the stream in order, the teams that the search read, each trade that the pick has
   sent so far, the most trades that the pick can keep, and the trades of the Shortlist that the pick weighs. */
type FindState =
  | { status: "idle" }
  | { status: "finding"; lines: string[]; read: number[]; trades: FinderTrade[]; most: number; shortlist: ShortlistTrade[] }
  | { status: "done"; doc: FindResponse }
  | { status: "error"; message: string };

type TradeFinderProps = {
  teams: Team[];
  // The API of the client and the league season the find body sends. The page reads it from the config, so the finder
  // imports no config.
  target: ApiTarget;
  // The roster id of the team that asks, or null before a pick. The first side of the trade form, "Your Team", holds it.
  asker: number | null;
  // A pick of Your team in Find mode. The form puts it on its first side, so both modes share one asker.
  onAsker: (rosterId: number) => void;
  passphrase: string;
  // The passphrase is wrong, so the page clears it and asks again.
  onUnauthorized: () => void;
  // Find answered 422, so the page fetches the current rosters.
  onRostersStale?: () => void;
  // A card opens its trade in the analyzer. The document of the find carries the season, the asker, and the as-of
  // stamps, so the form can show the read of the card with no second grade.
  onOpen: (trade: FinderTrade, doc: FindResponse) => void;
  // A search runs or stops, so the form can lock the switch of the hero until it ends.
  onFindingChange?: (finding: boolean) => void;
  // The eyebrow and the switch of the hero. The form gives the same ones to the hero of Grade mode.
  eyebrow?: ReactNode;
  toggle?: ReactNode;
  // A grade runs, so the picker and the buttons stay off until the grade ends.
  locked?: boolean;
};

/* The body of a find: the asker, the partner when one is picked, and the limit when a chip other than Any is picked. */
export function findBody(season: number, asker: number, partner: number | null, aim: Aim): FindRequest {
  return {
    season,
    asker,
    ...(partner === null ? {} : { partner }),
    ...(aim === "Any" ? {} : { limit: { aim_position: aim } }),
  };
}

/* A choice of one team: a button on the hero that names the pick, and a sheet with the list. With `every`, the list
   starts with "Every team", which picks no team. The button reads as the label over the pick, so its name holds both. */
function TeamChoice({
  label,
  listName,
  teams,
  value,
  every,
  onChange,
  disabled,
}: {
  label: string;
  listName: string;
  teams: Team[];
  value: number | null;
  every?: string;
  onChange: (rosterId: number | null) => void;
  disabled: boolean;
}) {
  const [open, setOpen] = useState(false);
  const picked = teams.find((team) => team.roster_id === value) ?? null;
  const name = picked ? picked.team : (every ?? "Pick a team");
  function pick(rosterId: number | null) {
    onChange(rosterId);
    setOpen(false);
  }
  return (
    <>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen(true)}
        className="press flex min-h-touch w-full cursor-pointer items-center gap-sp-3 rounded-card bg-chip-dark px-sp-3 py-sp-2 text-left text-on-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60"
      >
        {picked ? (
          <Avatar src={picked.avatar ?? AVATAR_FALLBACK} />
        ) : (
          <span aria-hidden="true" className="grid size-avatar flex-none place-items-center rounded-full bg-on-dark text-band">
            <Users className="size-sp-4" />
          </span>
        )}
        <span className="flex min-w-0 flex-1 flex-col">
          <span className="text-label font-bold tracking-caps text-on-dark-muted uppercase">{label}</span>
          <b className="truncate text-row leading-tight font-bold">{name}</b>
        </span>
        <span aria-hidden="true" className="text-meta font-bold text-accent-text">
          Change
        </span>
      </button>
      <Sheet open={open} title={label} onClose={() => setOpen(false)}>
        <ul aria-label={listName} className="m-0 flex list-none flex-col gap-sp-1 p-0">
          {every !== undefined && (
            <li>
              <TeamRow lit={value === null} onClick={() => pick(null)} name={every} meta={`The search looks at all ${teams.length}`} />
            </li>
          )}
          {teams.map((team) => (
            <li key={team.roster_id}>
              <TeamRow
                lit={value === team.roster_id}
                onClick={() => pick(team.roster_id)}
                name={team.team}
                meta={team.manager}
                avatar={team.avatar ?? AVATAR_FALLBACK}
              />
            </li>
          ))}
        </ul>
      </Sheet>
    </>
  );
}

function TeamRow({ lit, onClick, name, meta, avatar }: { lit: boolean; onClick: () => void; name: string; meta: string; avatar?: string }) {
  return (
    <button
      type="button"
      aria-pressed={lit}
      onClick={onClick}
      className="press flex min-h-touch w-full cursor-pointer items-center gap-sp-3 rounded-card px-sp-3 py-sp-1 text-left text-ink hover:bg-card focus-visible:outline-2 focus-visible:outline-accent aria-pressed:bg-card"
    >
      {avatar ? (
        <Avatar src={avatar} />
      ) : (
        <span aria-hidden="true" className="grid size-avatar flex-none place-items-center rounded-full bg-ink text-page">
          <Users className="size-sp-4" />
        </span>
      )}
      <span className="flex min-w-0 flex-col">
        <b className="truncate text-row leading-tight font-bold">{name}</b>
        <span className="text-meta text-mute">{meta}</span>
      </span>
    </button>
  );
}

/* The chips of the position to get, through the segmented control wrapper, so one tap picks one and the pill slides. */
function PositionChips({ value, onChange, disabled }: { value: Aim; onChange: (aim: Aim) => void; disabled: boolean }) {
  return (
    <SegmentedControl<Aim> aria-label="Position" tone="dark" value={value} onValueChange={(next) => next !== null && onChange(next)} disabled={disabled}>
      <SegmentedControlIndicator />
      {AIMS.map((aim) => (
        <SegmentedControlItem key={aim} value={aim}>
          {aim}
        </SegmentedControlItem>
      ))}
    </SegmentedControl>
  );
}

/* The first live line of a find, as the stream sends it, so the wait shows it before the first part arrives and the
   first part changes nothing. With no partner the search reads every other team, so the line counts them. */
function firstLine(partner: number | null, partners: number): string {
  return partner === null && partners > 1 ? `Reading ${partners} teams` : "Reading their roster";
}

/* The wait line: the place of the running step and its live line, such as "4 of 5 · Checking 77 against both lineups". */
function waitLine(step: number, line: string): string {
  return `${Math.min(step, FIND_STEPS)} of ${FIND_STEPS} · ${line}`;
}

/* The line of step 5 that names one Shortlist trade: the players the asker gives, then "for", then the players he gets,
   such as "Weighing Walker for Lawrence, Pollard, Moore". A line too long for a phone takes the last names. */
export function weighLine(trade: ShortlistTrade): string {
  const line = (key: "name" | "last") => `Weighing ${trade.gives.map((p) => p[key]).join(", ")} for ${trade.gets.map((p) => p[key]).join(", ")}`;
  const full = line("name");
  return full.length <= WEIGH_FIT ? full : line("last");
}

/* The wait line on the screen. The stream can start two steps in the same moment, so the lines queue, and each line
   shows for at least STEP_HOLD_MS before the next one. A line with nothing queued behind it holds until the next line
   comes, and a line that has held gives way at once.
   On step 5, the line names one trade of the Shortlist every WEIGH_MS, in the order of the Shortlist, and starts again
   at the first while the pick still runs. The step line shows first, so the reader sees the step and its count. The
   lines stop when the first card lands: the card is the answer, so the wait goes back to the step line and holds. */
function useWaitLine(lines: string[], weighs: string[], landed: boolean): string {
  const [index, setIndex] = useState(0);
  // The index of the line that has shown for its hold. The hold is kept with its index, so a new line starts unheld.
  const [held, setHeld] = useState(-1);
  useEffect(() => {
    const hold = setTimeout(() => setHeld(index), STEP_HOLD_MS);
    return () => clearTimeout(hold);
  }, [index]);
  // The move to the next line runs before the paint, so a line that comes after the hold shows in the same frame.
  useLayoutEffect(() => {
    if (held === index && index < lines.length - 1) setIndex(index + 1);
  }, [held, index, lines.length]);
  const line = lines[Math.min(index, lines.length - 1)];
  const weighing = !landed && weighs.length > 0 && index === lines.length - 1 && line.startsWith(waitLine(FIND_STEPS, ""));
  // The turn of step 5: 0 shows the step line, and turn n shows Shortlist trade n - 1, round the list.
  const [turn, setTurn] = useState(0);
  useEffect(() => {
    if (!weighing) return;
    const next = setTimeout(() => setTurn(turn + 1), WEIGH_MS);
    return () => clearTimeout(next);
  }, [weighing, turn]);
  return weighing && turn > 0 ? weighs[(turn - 1) % weighs.length] : line;
}

/* The teams of the search as one row of avatars, where the grade shows its trade. Each avatar lights as the stream
   reports its team read, so the reader sees the search move. The light is an opacity and scale change of 250 ms with
   the ease-out, so a burst of reads still reads as a turn. With motion off, the avatar lights at once. */
function TeamsRead({ teams, read }: { teams: Team[]; read: number[] }) {
  return (
    <ul aria-hidden="true" className="m-0 flex list-none flex-wrap gap-sp-1 p-0">
      {teams.map((team) => {
        const lit = read.includes(team.roster_id);
        return (
          <li
            key={team.roster_id}
            data-team-read={team.roster_id}
            data-lit={lit}
            className={cn(
              "rounded-full ring-2 ring-band transition-[opacity,scale] duration-250 ease-[var(--ease-out)] motion-reduce:transition-none",
              lit ? "scale-100 opacity-100" : "scale-[0.92] opacity-30",
            )}
          >
            <Avatar src={team.avatar ?? AVATAR_FALLBACK} />
          </li>
        );
      })}
    </ul>
  );
}

/* The hero of the find wait: the same hero, mesh, title level, and line part as the grade wait. The line is the running
   step of the stream with its count, a list of one line, so StageLines holds it until the next step starts and then
   swaps it with the motion of the grade. The lines queue, so each step shows in turn. On step 5 the line names each
   Shortlist trade in turn, until the first card lands. The status holds the same line for a screen reader. The drive
   starts with the hero, so the mesh moves on the first frame after the tap. */
function FindWaitHero({
  eyebrow,
  toggle,
  lines,
  weighs,
  landed,
  teams,
  read,
}: {
  eyebrow?: ReactNode;
  toggle?: ReactNode;
  lines: string[];
  weighs: string[];
  landed: boolean;
  teams: Team[];
  read: number[];
}) {
  const [drive] = useState(() => waitDrive(performance.now()));
  const line = useWaitLine(lines, weighs, landed);
  return (
    <Hero
      label="Finding Trades"
      art={<HeroMesh drive={drive} />}
      level={2}
      eyebrow={eyebrow}
      toggle={toggle}
      title="Finding Trades"
      // The meta keeps the question of the idle hero. It names no time, because a press can wait on a live check.
      meta="Who has a trade for you?"
      feature={
        <div aria-busy="true">
          <p role="status" className="sr-only">
            {line}
          </p>
          <div aria-hidden="true" className="flex flex-col gap-sp-5">
            <StageLines lines={[line]} />
            <TeamsRead teams={teams} read={read} />
          </div>
        </div>
      }
    />
  );
}

/* The Lean word leads each card, as on the read. A yes leans in the accent, a gut call in the plain ink. */
function LeanWord({ lean }: { lean: Lean }) {
  const yes = lean === "Send it" || lean === "Lean yes";
  return <h3 className={cn("m-0 text-score leading-tight font-black tracking-tight", yes ? "text-accent-ink" : "text-ink")}>{lean}</h3>;
}

/* The Bullets fold under the Case, so the card stays short. One tap opens them. The panel of the shared Collapsible
   fades in with a small rise, and the chevron flips. The closed panel is hidden, so a keyboard skips its rows. With
   motion off it opens at once. */
function FoldedBullets({ trade, idBase }: { trade: FinderTrade; idBase: string }) {
  return (
    <Collapsible className="flex flex-col">
      <CollapsibleTrigger className="press group -mx-sp-2 flex min-h-touch w-fit cursor-pointer items-center gap-sp-1 rounded-pill px-sp-2 text-meta font-bold text-ink focus-visible:outline-2 focus-visible:outline-accent">
        Why it works · {trade.bullets.length}
        <ChevronDown
          aria-hidden="true"
          style={{ transitionTimingFunction: `cubic-bezier(${SMOOTH_OUT.join(",")})` }}
          className="size-sp-4 transition-transform duration-250 group-data-open:-scale-y-100 motion-reduce:transition-none"
        />
      </CollapsibleTrigger>
      <CollapsiblePanel>
        <div className="pt-sp-2 pb-sp-1">
          <BulletRows bullets={trade.bullets} idBase={idBase} />
        </div>
      </CollapsiblePanel>
    </Collapsible>
  );
}

/* One finder trade: the Lean, the Case of at most 3 lines with its condition first, the Ledger, and the folded
   Bullets. The pick writes no headline, so one voice speaks. After a fallback the trade has no Lean and no Bullet, so
   the card lists its plain fact lines. A card rises in as it lands, as the texts reveal of transitions.dev. Cards that
   land together rise one after another, `delay` seconds apart from the first. With motion off, they show at once. */
function FinderCard({ trade, asker, index, count, delay, onOpen, disabled }: { trade: FinderTrade; asker: number; index: number; count: number; delay: number; onOpen: () => void; disabled: boolean }) {
  const off = useMotionOff();
  const { partner } = ledgerOf(trade, asker);
  return (
    <motion.article
      aria-label={`Trade ${index + 1} of ${count}`}
      initial={off ? false : { opacity: 0, y: 12, filter: "blur(3px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ duration: 0.5, ease: EASE_OUT, delay }}
      className="flex flex-col gap-sp-3 rounded-card border border-rule bg-page p-sp-4"
    >
      <div className="flex items-baseline justify-between gap-sp-3">
        {trade.lean !== null ? (
          <LeanWord lean={trade.lean} />
        ) : (
          <h3 className="m-0 font-mono text-meta leading-tight font-bold tracking-wide text-accent-ink uppercase">
            Trade {index + 1} of {count}
          </h3>
        )}
        <span className="min-w-0 truncate text-meta text-mute">With {partner}</span>
      </div>
      {trade.case !== null && <p className="m-0 line-clamp-3 max-w-measure text-body leading-body text-pretty text-ink-2">{trade.case}</p>}
      <Ledger offer={trade} asker={asker} />
      {trade.bullets.length > 0 && <FoldedBullets trade={trade} idBase={`pick-${index + 1}`} />}
      {trade.fact_lines.length > 0 && (
        <ul aria-label="Facts" className="m-0 flex max-w-measure list-none flex-col gap-sp-2 p-0 text-meta text-ink-2">
          {trade.fact_lines.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
      <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" disabled={disabled} onClick={onOpen}>
        See the Full Result
      </Button>
    </motion.article>
  );
}

/* The near fold rises in after the last card, with the same rise as the cards, `after` cards of stagger later. With
   motion off, it shows at once. */
function NearFold({ doc, after }: { doc: FindResponse; after: number }) {
  const off = useMotionOff();
  if (doc.near.length === 0) return null;
  return (
    <motion.div
      initial={off ? false : { opacity: 0, y: 12, filter: "blur(3px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ duration: 0.5, ease: EASE_OUT, delay: after * 0.08 }}
    >
      <NearIdeas near={doc.near.slice(0, MAX_NEAR)} asker={doc.trade_pair.asker.roster_id} />
    </motion.div>
  );
}

/* The gap of the rise of two cards that land together, as the texts reveal of transitions.dev. */
const STAGGER_S = 0.08;

/* The line under the cards while the pick still writes, such as "Writing 4 more trades". It shimmers as a line of work
   in flight, as the shimmer text of transitions-dev, and a new count comes in through a small blur in place. It
   slides down with the list as a card lands. It names no time and no inner tool. With motion off, it holds still in
   the mute ink and swaps at once. */
function MoreLine({ left }: { left: number }) {
  const off = useMotionOff();
  const text = `Writing ${left} more ${left === 1 ? "trade" : "trades"}`;
  return (
    <motion.p
      layout={off ? false : "position"}
      aria-live="polite"
      initial={off ? false : { opacity: 0, y: 12, filter: "blur(3px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ duration: 0.5, ease: EASE_OUT }}
      className="m-0 grid min-h-touch items-center text-row font-bold"
    >
      {/* The key gives each count its own span, so a new count comes in through a small blur in place. The old count
          goes in the same frame, so the line never holds two counts. */}
      <motion.span
        key={text}
        className={cn(
          "col-start-1 row-start-1",
          off
            ? "text-mute"
            : "bg-clip-text text-transparent [background-image:linear-gradient(90deg,var(--color-mute)_0%,var(--color-mute)_40%,var(--color-ink)_50%,var(--color-mute)_60%,var(--color-mute)_100%)] [background-size:400%_100%]",
        )}
        initial={off ? false : { opacity: 0, filter: "blur(2px)", backgroundPosition: "100% 0%" }}
        animate={off ? undefined : { opacity: 1, filter: "blur(0px)", backgroundPosition: "0% 0%" }}
        transition={{
          opacity: { duration: 0.15, ease: "easeInOut" },
          filter: { duration: 0.15, ease: "easeInOut" },
          backgroundPosition: { duration: 2, ease: "linear", repeat: Infinity },
        }}
      >
        {text}
      </motion.span>
    </motion.p>
  );
}

/* The finder result: the cards in one list, or the empty line, then the near ideas folded, then the as-of line. After
   a fallback the list holds every offer of the shortlist, so only the picks keep to the count of 5.
   While the pick still writes, `doc` is null: the list holds the trades of the stream so far, a line under them counts
   the trades still to come, and the button of each card waits for the document. The part stays mounted from the first
   card to the document, so a card that showed does not rise again, and the document is the truth for the list. */
function FinderResult({
  trades: streamed,
  most,
  asker,
  doc,
  onOpen,
  disabled,
}: {
  trades: FinderTrade[];
  most: number;
  asker: number;
  doc: FindResponse | null;
  onOpen: (trade: FinderTrade, doc: FindResponse) => void;
  disabled: boolean;
}) {
  const all = doc === null ? streamed : doc.trades;
  const trades = doc?.fallback ? all : all.slice(0, MAX_PICKS);
  // The count of cards that showed in an earlier render. A card past it lands now, so the stagger counts from it.
  const shown = useRef(0);
  const before = Math.min(shown.current, trades.length);
  useEffect(() => {
    shown.current = trades.length;
  });
  // On a phone the wait hero fills the screen, so the first card of the stream lands below the fold. When it lands and
  // the reader cannot see all of it, the page scrolls once, smoothly, until the card sits at the top. A scroll keeps
  // the hero as it is, so no text changes size or place under the reader's thumb, and the reader has waited for this
  // card, so the move has a reason. A card already in full view does not move the page. With motion off, the scroll
  // jumps at once.
  const off = useMotionOff();
  const list = useRef<HTMLOListElement>(null);
  const landed = trades.length > 0;
  const streaming = doc === null;
  useEffect(() => {
    if (!landed || !streaming) return;
    const card = list.current?.firstElementChild;
    if (!card || card.getBoundingClientRect().bottom <= window.innerHeight) return;
    card.scrollIntoView?.({ behavior: off ? "auto" : "smooth", block: "start" });
    // Only the first card scrolls the page: the effect runs again only when a card first lands, so a later card never
    // pulls the reader away from the one he reads.
  }, [landed, streaming, off]);
  const left = doc === null ? Math.min(most, MAX_PICKS) - trades.length : 0;
  const count = doc === null ? Math.max(Math.min(most, MAX_PICKS), trades.length) : trades.length;
  if (doc === null && trades.length === 0) return null;
  return (
    <div className="flex flex-col gap-sp-4 pt-sp-5">
      {/* The pipeline writes the empty line, so the page shows it word for word. */}
      {doc !== null && doc.empty !== null && <p className="m-0 text-lead font-bold">{doc.empty}</p>}
      {doc !== null && doc.fallback && doc.trades.length > 0 && (
        <p className="m-0 text-lead text-ink-2">The picks did not come through. These are the trades the search kept, with their facts.</p>
      )}
      {trades.length > 0 && (
        <ol ref={list} aria-label="Trade ideas" className="m-0 flex list-none flex-col gap-sp-4 p-0">
          {trades.map((trade, i) => (
            <li key={trade.offer_id} className="scroll-mt-sp-4">
              <FinderCard
                trade={trade}
                asker={asker}
                index={i}
                count={count}
                delay={Math.max(0, i - before) * STAGGER_S}
                onOpen={() => doc !== null && onOpen(trade, doc)}
                disabled={disabled || doc === null}
              />
            </li>
          ))}
        </ol>
      )}
      {/* The line goes at once as the last card lands, so the eye follows the card and not a fade under it. */}
      {left > 0 && <MoreLine left={left} />}
      {doc !== null && (
        <>
          <NearFold doc={doc} after={Math.max(0, trades.length - before)} />
          <div className="pb-sp-5">
            <NoChartLine asOf={doc.as_of} />
            <AsOfLine doc={doc} />
          </div>
        </>
      )}
    </div>
  );
}

export function TradeFinder({
  teams,
  target,
  asker,
  onAsker,
  passphrase,
  onUnauthorized,
  onRostersStale,
  onOpen,
  onFindingChange,
  eyebrow,
  toggle,
  locked = false,
}: TradeFinderProps) {
  const [partner, setPartner] = useState<number | null>(null);
  const [aim, setAim] = useState<Aim>("Any");
  const [find, setFind] = useState<FindState>({ status: "idle" });
  // A late answer for an old partner must not overwrite the state of a new one.
  const request = useRequest();

  // The asker cannot trade with itself, so the partner choice lists the eleven other teams.
  const partners = teams.filter((team) => team.roster_id !== asker);
  const finding = find.status === "finding";
  const off = locked || finding;

  useEffect(() => {
    onFindingChange?.(finding);
  }, [finding, onFindingChange]);

  // A new partner or a new chip makes the old cards stale, so a change clears them.
  function pickPartner(rosterId: number | null) {
    request.drop();
    setPartner(rosterId);
    setFind({ status: "idle" });
  }

  function pickAim(next: Aim) {
    request.drop();
    setAim(next);
    setFind({ status: "idle" });
  }

  async function submit() {
    if (asker === null) return;
    const run = request.start();
    const { controller } = run;
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);
    setFind({ status: "finding", lines: [waitLine(1, firstLine(partner, partners.length))], read: [], trades: [], most: MAX_PICKS, shortlist: [] });
    // A live line starts a step, so it moves the wait line on. A done line ends the step, and the line holds until
    // the next step starts, because the next live line follows it at once.
    let step = 0;
    const events = {
      onStep: (line: string, live: boolean) => {
        if (!live || !run.isCurrent()) return;
        step += 1;
        const next = waitLine(step, line);
        // The first live line repeats the line that the wait opens with, so it adds no line to the queue.
        setFind((now) => (now.status === "finding" && now.lines[now.lines.length - 1] !== next ? { ...now, lines: [...now.lines, next] } : now));
      },
      onTeam: (rosterId: number) => {
        if (!run.isCurrent()) return;
        setFind((now) => (now.status === "finding" && !now.read.includes(rosterId) ? { ...now, read: [...now.read, rosterId] } : now));
      },
      // The Shortlist comes before the pick starts, so step 5 can name each trade it weighs.
      onShortlist: (shortlist: ShortlistTrade[]) => {
        if (!run.isCurrent()) return;
        setFind((now) => (now.status === "finding" ? { ...now, shortlist } : now));
      },
      // The pick sends its trades in order, so each new trade joins the end of the list.
      onTrade: (_index: number, most: number, trade: FinderTrade) => {
        if (!run.isCurrent()) return;
        setFind((now) =>
          now.status === "finding" && !now.trades.some((kept) => kept.offer_id === trade.offer_id) ? { ...now, trades: [...now.trades, trade], most } : now,
        );
      },
    };
    try {
      const doc = await streamFind(target, passphrase, findBody(target.season, asker, partner, aim), events, controller.signal);
      if (run.isCurrent()) setFind({ status: "done", doc });
    } catch (error) {
      // An abort from unmount must not set state on a gone component.
      if (!run.isCurrent()) return;
      if (error instanceof ApiError && error.status === 401) onUnauthorized();
      else setFind({ status: "error", ...toErrorLine(error, timedOut, "The search took too long.") });
      if (error instanceof ApiError && error.status === 422) onRostersStale?.();
    } finally {
      clearTimeout(timer);
    }
  }

  const pickers = (
    <div className="flex flex-col gap-sp-3">
      {/* A find needs the team that asks, so Your team stays in view and a pick here is the pick of Grade mode too. */}
      <TeamChoice
        label="Your team"
        listName="Teams"
        teams={teams}
        value={asker}
        onChange={(rosterId) => rosterId !== null && onAsker(rosterId)}
        disabled={off || teams.length === 0}
      />
      <TeamChoice label="Trade with" listName="Partners" teams={partners} value={partner} every="Every team" onChange={pickPartner} disabled={off || asker === null} />
      <PositionChips value={aim} onChange={pickAim} disabled={off} />
      {/* The hero shows the error line, so the reader sees why the search stopped where the search started. */}
      {find.status === "error" && (
        <div className="rounded-card bg-page px-sp-3 py-sp-2">
          <ErrorLine>{find.message}</ErrorLine>
        </div>
      )}
    </div>
  );

  // Every error shows Try Again in place of the find button, the same as the error box of the trade form.
  const action =
    find.status === "error" ? (
      <button
        type="button"
        onClick={submit}
        disabled={locked || asker === null}
        className="press flex h-touch w-full cursor-pointer items-center justify-center gap-sp-2 rounded-card bg-accent px-sp-4 text-lead font-bold text-on-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-on-dark disabled:cursor-not-allowed disabled:opacity-60"
      >
        <RotateCcw aria-hidden="true" className="size-sp-4" />
        Try Again
      </button>
    ) : (
      <PendingButton
        onClick={submit}
        disabled={locked || asker === null}
        pendingAnnouncement=""
        className="press flex h-touch w-full cursor-pointer items-center justify-center rounded-card bg-accent px-sp-4 text-lead font-bold text-on-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-on-dark disabled:cursor-not-allowed disabled:opacity-60 data-pending:opacity-80"
      >
        Find a Trade
      </PendingButton>
    );

  // The cards: the trades of the stream so far while the search runs, then the document.
  const result =
    find.status === "done"
      ? { trades: [], most: 0, asker: find.doc.trade_pair.asker.roster_id, doc: find.doc }
      : find.status === "finding" && asker !== null
        ? { trades: find.trades, most: find.most, asker, doc: null }
        : null;

  // The wait shows the teams the search reads: the picked partner, or the eleven other teams.
  const searched = partner === null ? partners : partners.filter((team) => team.roster_id === partner);

  return (
    <section aria-label="Trade Ideas" className="flex flex-col">
      {find.status === "finding" ? (
        <FindWaitHero
          eyebrow={eyebrow}
          toggle={toggle}
          lines={find.lines}
          weighs={find.shortlist.map(weighLine)}
          landed={find.trades.length > 0}
          teams={searched}
          read={find.read}
        />
      ) : (
        <Hero label="Trade Ideas" art={<HeroMesh />} eyebrow={eyebrow} toggle={toggle} title="Trade Ideas" meta="Who has a trade for you?" feature={pickers} action={action} />
      )}
      {/* One part in one place shows the cards of the stream and then the cards of the document, so React keeps it
          mounted and a card that showed stays where it is. */}
      {result !== null && <FinderResult {...result} onOpen={onOpen} disabled={locked} />}
    </section>
  );
}
