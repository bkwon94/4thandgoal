/**
 * The trade finder: the optional partner picker, the "Find a Trade" button, and up to three cards of the Advisor picks.
 * It posts the asker, and the partner when one is picked, to the find route. A card hands its trade to the trade form.
 */
"use client";

import { useState } from "react";
import { AsOfLine, NoChartLine, SwapCard, type SwapSide } from "./analyze-result";
import { BulletRows } from "./bullet-rows";
import { Card } from "@cpc/design/parts/card";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { Sweep } from "./sweep";
import { TeamPicker } from "./team-picker";
import { Button } from "@cpc/design/ui/button";
import { useRequest } from "./use-request";
import type { FindResponse, FinderTrade } from "../lib/analyze-types";
import { ApiError, type ApiTarget, postFind, toErrorLine, type Team } from "../lib/api";

// The finder asks Jev in waves and makes one Claude call, so it waits as long as a cold grade.
const TIMEOUT_MS = 60_000;

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
  // The roster id of the team that asks. The first side of the trade form, "Your Team", sets it.
  asker: number;
  passphrase: string;
  // The passphrase is wrong, so the page clears it and asks again.
  onUnauthorized: () => void;
  // Find answered 422, so the page fetches the current rosters.
  onRostersStale?: () => void;
  // A card asks for the full result of its trade. The season is the one the finder document carries.
  onOpen: (trade: FinderTrade, season: number) => void;
  // A grade runs, so the picker and the buttons stay off until the grade ends.
  locked?: boolean;
};

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

export function TradeFinder({ teams, target, asker, passphrase, onUnauthorized, onRostersStale, onOpen, locked = false }: TradeFinderProps) {
  const [partner, setPartner] = useState<number | null>(null);
  const [find, setFind] = useState<FindState>({ status: "idle" });
  // A late answer for an old partner must not overwrite the state of a new one.
  const request = useRequest();

  // The asker cannot trade with itself, so the picker lists the eleven other teams.
  const partners = teams.filter((team) => team.roster_id !== asker);
  const finding = find.status === "finding";

  // A new partner, or no partner, makes the old cards stale, so a change clears them.
  function pickPartner(rosterId: number | null) {
    request.drop();
    setPartner(rosterId);
    setFind({ status: "idle" });
  }

  async function submit() {
    const run = request.start();
    const { controller } = run;
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);
    setFind({ status: "finding" });
    try {
      // With no partner, the body has no partner key, so the search runs over every other team.
      const body = partner === null ? { season: target.season, asker } : { season: target.season, asker, partner };
      const doc = await postFind(target, passphrase, body, controller.signal);
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

  return (
    <section aria-labelledby="find-trade">
      <Card className="flex flex-col gap-sp-5">
        <div className="flex flex-col gap-sp-2">
          <h2 id="find-trade" className="m-0 text-stat leading-stat font-black uppercase">
            Find a Trade
          </h2>
          <p className="m-0 text-lead text-ink-2">Pick a partner, or search every team. The search finds up to 3 trades.</p>
        </div>
        <TeamPicker label="Trade Partner" teams={partners} value={partner} disabledId={null} onChange={pickPartner} locked={locked || finding} />
        {partner !== null && (
          <Button
            variant="ghost"
            className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold"
            disabled={locked || finding}
            onClick={() => pickPartner(null)}
          >
            Search Every Team
          </Button>
        )}
        <Button
          className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold"
          disabled={finding || locked}
          aria-busy={finding || undefined}
          onClick={submit}
        >
          {finding ? "Finding…" : "Find a Trade"}
        </Button>
        {finding && (
          <div className="flex flex-col gap-sp-2">
            <Sweep />
            <p role="status" className="m-0 text-lead text-mute">
              The search tries every small swap. This can take up to a minute.
            </p>
          </div>
        )}
        {find.status === "error" && (
          <div className="flex flex-col gap-sp-3">
            <ErrorLine>{find.message}</ErrorLine>
            {/* Every error shows Try Again, the same as the error box of the trade form. */}
            <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" onClick={submit}>
              Try Again
            </Button>
          </div>
        )}
        {find.status === "done" && <FinderResult doc={find.doc} onOpen={onOpen} locked={locked} />}
      </Card>
    </section>
  );
}
