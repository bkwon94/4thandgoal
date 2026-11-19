/**
 * The analyzer page body: the passphrase dialog, the teams fetch, and the Stack of the trade form.
 * It owns the passphrase, so a 401 from any call asks again. Stored teams show at once while a fresh fetch runs.
 * It owns the mode of the switch, Grade a trade or Find a trade, from the address, and the deadline eyebrow of the hero.
 */
"use client";

import { type ReactNode, useEffect, useState } from "react";
import { ErrorLine } from "@cpc/design/parts/error-line";
import { PassphraseDialog } from "./passphrase-dialog";
import { Reveal } from "@cpc/design/parts/reveal";
import { TradeForm } from "./trade-form";
import { Button } from "@cpc/design/ui/button";
import { useRequest } from "./use-request";
import { ApiError, type ApiTarget, retryText, type Team } from "../lib/api";
import { DURATION } from "@cpc/design/lib/motion";
import type { DeadlineState } from "@cpc/design/lib/deadline";
import { useDeadline } from "@cpc/design/hooks/use-deadline";
import { type AnalyzerMode, readMode, withMode } from "../lib/mode";
import { clearPassphrase, getPassphrase, setPassphrase } from "../lib/passphrase";
import { clearStoredTeams, fetchAndStoreTeams, readStoredTeams } from "../lib/teams-store";
import { prefillSides, readPrefill } from "../lib/prefill";
import type { Sides } from "../lib/trade";
import { getYourTeam } from "../lib/your-team";

type TeamsState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; teams: Team[] }
  | { status: "rate-limited"; retryAfter?: number }
  | { status: "failed" };

const WRONG_PASSPHRASE = "That passphrase is wrong.";

/* The teams of the empty Stack before the fetch answers. One constant, so the form sees no change of list on each render. */
const NO_TEAMS: Team[] = [];

/* The eyebrow of the hero during Deadline week: the countdown, then the passed line after the Lock. The countdown keeps
   its lower case in the caps of the eyebrow, so "~2d 14h 05m" reads as a time. Undefined outside Deadline week. */
function deadlineEyebrow(deadline: DeadlineState | null): ReactNode {
  if (deadline === null || deadline.state === "ended") return undefined;
  if (deadline.countdown === null) return "The trade deadline has passed";
  return (
    <>
      Trade deadline <span className="normal-case tabular-nums">{deadline.countdown}</span>
    </>
  );
}

/* The API target, the finder flag, and the Lock come from the page, so the analyzer and the form under it import no
   config. A client with no Lock has no Deadline week. The Lock is in epoch milliseconds. */
export function Analyzer({ target, finderOn, lock }: { target: ApiTarget; finderOn: boolean; lock?: number | null }) {
  // Undefined until the effect reads storage. Local storage does not exist during the static build.
  const [passphrase, setPassphraseState] = useState<string | null | undefined>(undefined);
  const [authError, setAuthError] = useState<string | undefined>();
  const [teams, setTeams] = useState<TeamsState>({ status: "idle" });
  // A new value starts the fetch again, for the retry button.
  const [attempt, setAttempt] = useState(0);
  // The refresh after a 422 runs outside the effect, so it reads its run before it sets state.
  const request = useRequest();

  // The sides that a link of the front door names in the query. The static page has no query, so the effect reads it.
  const [prefill, setPrefill] = useState<Sides | null>(null);
  // The half of the switch. A link of the Trade Wire names it in the query, so the effect reads it with the prefill.
  const [mode, setMode] = useState<AnalyzerMode>("grade");
  const deadline = useDeadline(lock);

  useEffect(() => {
    setPassphraseState(getPassphrase());
    setMode(readMode(window.location.search, finderOn));
    const named = readPrefill(window.location.search);
    if (named) {
      setPrefill(prefillSides(named));
      return;
    }
    // A link with no team opens on the team that the manager picked on the front door.
    const team = getYourTeam();
    if (team !== null) setPrefill(prefillSides({ team, partner: null, gives: [], gets: [] }));
  }, []);

  useEffect(() => {
    if (!passphrase) return;
    // A stale answer must not overwrite the state after a new submit or an unmount.
    let current = true;
    // Stored teams show at once. The fetch still runs, because a roster can change after a trade.
    const stored = readStoredTeams(target);
    setTeams(stored ? { status: "ready", teams: stored } : { status: "loading" });
    fetchAndStoreTeams(target, passphrase)
      .then((list) => current && setTeams({ status: "ready", teams: list }))
      .catch((error: unknown) => {
        if (!current) return;
        if (error instanceof ApiError && error.status === 401) {
          handleUnauthorized();
          return;
        }
        // The stored list is still good enough to grade a trade, so a failed refresh keeps it on the screen.
        if (stored) return;
        if (error instanceof ApiError && error.status === 429) {
          setTeams({ status: "rate-limited", retryAfter: error.retryAfter });
        } else {
          setTeams({ status: "failed" });
        }
      });
    return () => {
      current = false;
    };
  }, [passphrase, attempt]);

  function handleUnauthorized() {
    clearPassphrase();
    setPassphraseState(null);
    setAuthError(WRONG_PASSPHRASE);
    setTeams({ status: "idle" });
  }

  /* A 422 from analyze can mean a roster changed after the store. The form keeps its error line and gets the current rosters. */
  function handleStaleRosters() {
    if (!passphrase) return;
    clearStoredTeams(target);
    // fetchAndStoreTeams takes no signal, so only the run guard applies.
    const run = request.start();
    fetchAndStoreTeams(target, passphrase)
      .then((list) => run.isCurrent() && setTeams({ status: "ready", teams: list }))
      .catch((error: unknown) => {
        if (!run.isCurrent()) return;
        if (error instanceof ApiError && error.status === 401) handleUnauthorized();
        // Any other failure keeps the current list. The error line of the form already tells the reader.
      });
  }

  /* A tap on the switch names the new mode in the address, so a reload or a shared link opens the same half. */
  function changeMode(next: AnalyzerMode) {
    setMode(next);
    window.history.replaceState(window.history.state, "", `${window.location.pathname}${withMode(window.location.search, next)}`);
  }

  function handleSubmit(value: string) {
    setPassphrase(value);
    setAuthError(undefined);
    setPassphraseState(value);
  }

  /* The lines of the fetch sit between the hero and the form. The empty Stack shows under them from the first paint,
     with each control off until the teams arrive, so the page does not jump when they do. */
  const states = (
    <>
      <PassphraseDialog open={passphrase === null} error={authError} onSubmit={handleSubmit} />
      {teams.status === "loading" && (
        <p role="status" className="mt-sp-4 mb-0 text-lead text-mute">
          Loading the teams…
        </p>
      )}
      {teams.status === "rate-limited" && (
        <div className="mt-sp-4">
          <ErrorLine>{retryText(teams.retryAfter)}</ErrorLine>
        </div>
      )}
      {teams.status === "failed" && (
        <div className="mt-sp-4 flex flex-col gap-sp-3">
          <ErrorLine>The API did not answer. Try again.</ErrorLine>
          <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" onClick={() => setAttempt((n) => n + 1)}>
            Try Again
          </Button>
        </div>
      )}
    </>
  );

  const ready = teams.status === "ready" && passphrase;

  return (
    <TradeForm
      teams={ready ? teams.teams : NO_TEAMS}
      target={target}
      finderOn={finderOn}
      passphrase={passphrase ?? ""}
      onUnauthorized={handleUnauthorized}
      onRostersStale={handleStaleRosters}
      prefill={prefill}
      mode={mode}
      onModeChange={changeMode}
      eyebrow={deadlineEyebrow(deadline)}
    >
      {({ hero, form, result }) => (
        <>
          {hero}
          {states}
          {/* The form is the content of the route, so it fades and rises in once when it first shows. With motion off it shows at rest. */}
          <Reveal trigger="mount" duration={DURATION.page}>
            {form}
          </Reveal>
          {result}
        </>
      )}
    </TradeForm>
  );
}
