/**
 * Find mode of the analyzer: the dark hero with Your team, the partner choice, the position chips,
 * and the find button, then up to three cards of the picks under it. A chip sets aim_position of the Limit.
 */
"use client";

import { Users } from "lucide-react";
import { type ReactNode, useEffect, useState } from "react";
import { AsOfLine, NoChartLine, SwapCard, type SwapSide } from "./analyze-result";
import { BulletRows } from "./bullet-rows";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { Hero } from "@cpc/design/parts/hero";
import { HeroMesh } from "@cpc/design/parts/hero-mesh";
import { Sheet } from "./sheet";
import { Sweep } from "./sweep";
import { Button } from "@cpc/design/ui/button";
import { PendingButton } from "@cpc/design/ui/pending-button";
import { SegmentedControl, SegmentedControlIndicator, SegmentedControlItem } from "@cpc/design/ui/segmented-control";
import { Avatar } from "@cpc/league/avatar";
import { AVATAR_FALLBACK } from "@cpc/league/images";
import { useRequest } from "./use-request";
import type { FindResponse, FinderTrade } from "../lib/analyze-types";
import { ApiError, type ApiTarget, type FindRequest, postFind, toErrorLine, type Team } from "../lib/api";

// The finder asks Jev in waves and makes one Claude call, so it waits as long as a cold grade.
const TIMEOUT_MS = 60_000;

/* The position chips. Any sends no limit. Each other chip sends its position as aim_position, the same field that a
   typed question such as "trade ideas for an RB" sets on the front door. */
const AIMS = ["Any", "RB", "WR", "TE", "QB"] as const;
type Aim = (typeof AIMS)[number];

type FindState =
  | { status: "idle" }
  | { status: "finding" }
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
  // A card asks for the full result of its trade. The season is the one the finder document carries.
  onOpen: (trade: FinderTrade, season: number) => void;
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

/* The asker's side goes first, as on the analyze result, so "You Get" always leads the card. */
function swapSides(trade: FinderTrade, asker: number): SwapSide[] {
  const sides = trade.sides.map((side) => ({ ...side, mine: side.roster_id === asker }));
  return sides.sort((a, b) => Number(b.mine) - Number(a.mine));
}

/* One finder trade: its place, the headline, the swap card, then the Bullet rows of the analyzer.
   After a fallback the trade has no headline and no Bullet, so the card lists its plain fact lines. */
function FinderCard({ trade, asker, index, count, onOpen, locked }: { trade: FinderTrade; asker: number; index: number; count: number; onOpen: () => void; locked: boolean }) {
  const sides = swapSides(trade, asker);
  return (
    <article aria-label={`Trade ${index + 1}`} className="flex flex-col gap-sp-4 border-t border-rule py-sp-5">
      <h3 className="m-0 font-mono text-meta leading-tight font-bold tracking-wide text-accent-ink uppercase">
        Trade {index + 1} of {count}
      </h3>
      {trade.headline !== null && <p className="m-0 text-lead font-bold text-ink">{trade.headline}</p>}
      <SwapCard sides={sides} />
      {trade.bullets.length > 0 && <BulletRows bullets={trade.bullets} idBase={`pick-${index + 1}`} />}
      {trade.fact_lines.length > 0 && (
        <ul aria-label="Facts" className="m-0 flex max-w-measure list-none flex-col gap-sp-2 p-0 text-meta text-ink-2">
          {trade.fact_lines.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
      <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" disabled={locked} onClick={onOpen}>
        See the Full Result
      </Button>
    </article>
  );
}

/* The finder result: the cards, or the empty line, then the as-of line. */
function FinderResult({ doc, onOpen, locked }: { doc: FindResponse; onOpen: (trade: FinderTrade, season: number) => void; locked: boolean }) {
  const asker = doc.trade_pair.asker.roster_id;
  return (
    <div>
      {/* The pipeline writes the empty line, so the page shows it word for word. */}
      {doc.empty !== null && <p className="m-0 py-sp-5 text-lead font-bold">{doc.empty}</p>}
      {doc.fallback && doc.trades.length > 0 && (
        <p className="m-0 pt-sp-5 text-lead text-ink-2">The picks did not come through. These are the trades the search kept, with their facts.</p>
      )}
      {doc.trades.map((trade, i) => (
        <FinderCard
          key={trade.offer_id}
          trade={trade}
          asker={asker}
          index={i}
          count={doc.trades.length}
          onOpen={() => onOpen(trade, doc.season)}
          locked={locked}
        />
      ))}
      <div className="py-sp-5">
        <NoChartLine asOf={doc.as_of} />
        <AsOfLine doc={doc} />
      </div>
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
    setFind({ status: "finding" });
    try {
      const doc = await postFind(target, passphrase, findBody(target.season, asker, partner, aim), controller.signal);
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

  const feature = (
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
      {finding && (
        <div className="flex flex-col gap-sp-2 pt-sp-2">
          <Sweep track="bg-chip-dark" />
          <p role="status" className="m-0 text-lead text-on-dark-2">
            The search tries every small swap. This can take up to a minute.
          </p>
        </div>
      )}
    </div>
  );

  const action = (
    <PendingButton
      onClick={submit}
      disabled={locked || asker === null}
      pendingAnnouncement=""
      className="press flex h-touch w-full cursor-pointer items-center justify-center rounded-card bg-accent px-sp-4 text-lead font-bold text-on-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-on-dark disabled:cursor-not-allowed disabled:opacity-60 data-pending:opacity-80"
    >
      Find a Trade
    </PendingButton>
  );

  return (
    <section aria-label="Trade Ideas" className="flex flex-col">
      <Hero label="Trade Ideas" art={<HeroMesh />} eyebrow={eyebrow} toggle={toggle} title="Trade Ideas" meta="Who has a trade for you?" feature={feature} action={action} />
      {find.status === "error" && (
        <div className="flex flex-col gap-sp-3 pt-sp-5">
          <ErrorLine>{find.message}</ErrorLine>
          {/* Every error shows Try Again, the same as the error box of the trade form. */}
          <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" onClick={submit}>
            Try Again
          </Button>
        </div>
      )}
      {find.status === "done" && <FinderResult doc={find.doc} onOpen={onOpen} locked={locked} />}
    </section>
  );
}
