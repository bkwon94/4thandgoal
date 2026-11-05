/**
 * The trade finder: the partner picker, the "Find a Trade" button, and up to three cards of trades that are good for both.
 * It posts the pair to the find route. A card hands its trade to the trade form, which grades it through the analyze route.
 */
"use client";

import { useState } from "react";
import { AsOfLine, FairnessBlock, NoChartLine, SwapCard, type SwapSide } from "./analyze-result";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { TeamPicker } from "./team-picker";
import { Button } from "@cpc/design/ui/button";
import { useRequest } from "./use-request";
import type { FindResponse, FinderTrade } from "../lib/analyze-types";
import { ApiError, type ApiTarget, postFind, toErrorLine, type Team } from "../lib/api";

// The finder grades every small swap of the pair and makes one Claude call, so it waits as long as a cold grade.
const TIMEOUT_MS = 60_000;

type FindState =
  | { status: "idle" }
  | { status: "finding" }
  | { status: "done"; doc: FindResponse }
  | { status: "error"; message: string; retry: boolean };

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

/* One finder trade: the swap card, the fairness line, and the reason. A null reason shows the fairness line alone. */
function FinderCard({ trade, asker, index, onOpen, locked }: { trade: FinderTrade; asker: number; index: number; onOpen: () => void; locked: boolean }) {
  const sides = swapSides(trade, asker);
  return (
    <article aria-label={`Trade ${index + 1}`} className="flex flex-col gap-sp-4 border-b-(length:--chap-rule) border-card py-sp-5">
      <SwapCard sides={sides} />
      <FairnessBlock sides={sides} fairness={trade.fairness} />
      {trade.reason !== null && <p className="m-0 text-body text-ink-2">{trade.reason}</p>}
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
      {doc.empty !== null && <p className="m-0 py-sp-5 text-body font-bold">{doc.empty}</p>}
      {doc.trades.map((trade, i) => (
        <FinderCard
          key={trade.sides.flatMap((s) => s.gives.map((p) => p.player_id)).join("-")}
          trade={trade}
          asker={asker}
          index={i}
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

  // A new partner makes the old cards stale, so a change clears them.
  function pickPartner(rosterId: number) {
    request.drop();
    setPartner(rosterId);
    setFind({ status: "idle" });
  }

  async function submit() {
    if (partner === null) return;
    const run = request.start();
    const { controller } = run;
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);
    setFind({ status: "finding" });
    try {
      const doc = await postFind(target, passphrase, { season: target.season, asker, partner }, controller.signal);
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
    <section aria-labelledby="find-trade" className="flex flex-col gap-sp-5">
      <h2 id="find-trade" className="m-0 text-stat leading-stat font-black uppercase">
        Find a Trade
      </h2>
      <TeamPicker label="Trade Partner" teams={partners} value={partner} disabledId={null} onChange={pickPartner} locked={locked || finding} />
      <Button
        className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold"
        disabled={partner === null || finding || locked}
        aria-busy={finding || undefined}
        onClick={submit}
      >
        {finding ? "Finding…" : "Find a Trade"}
      </Button>
      {finding && (
        <p role="status" className="m-0 text-meta text-mute">
          The search tries every small swap. This can take up to a minute early in the week.
        </p>
      )}
      {find.status === "error" && (
        <div className="flex flex-col gap-sp-3">
          <ErrorLine>{find.message}</ErrorLine>
          {find.retry && (
            <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" onClick={submit}>
              Try Again
            </Button>
          )}
        </div>
      )}
      {find.status === "done" && <FinderResult doc={find.doc} onOpen={onOpen} locked={locked} />}
    </section>
  );
}
