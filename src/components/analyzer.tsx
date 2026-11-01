/**
 * The analyzer page body: the passphrase dialog, the teams fetch, and the trade form.
 * It owns the passphrase, so a 401 from any call asks again. Stored teams show at once while a fresh fetch runs.
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { ErrorLine } from "@/components/error-line";
import { PassphraseDialog } from "@/components/passphrase-dialog";
import { Reveal } from "@/components/reveal";
import { TeamsSkeleton } from "@/components/teams-skeleton";
import { TradeForm } from "@/components/trade-form";
import { Button } from "@/components/ui/button";
import { Chapter } from "@/components/week/parts";
import { ApiError, retryText, type Team } from "@/lib/api";
import { DURATION } from "@/lib/motion";
import { clearPassphrase, getPassphrase, setPassphrase } from "@/lib/passphrase";
import { clearStoredTeams, fetchAndStoreTeams, readStoredTeams } from "@/lib/teams-store";

type TeamsState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; teams: Team[] }
  | { status: "rate-limited"; retryAfter?: number }
  | { status: "failed" };

const WRONG_PASSPHRASE = "That passphrase is wrong.";

/* The season and the finder flag come from the page, so the analyzer and the form under it import no config. */
export function Analyzer({ season, finderOn }: { season: number; finderOn: boolean }) {
  // Undefined until the effect reads storage. Local storage does not exist during the static build.
  const [passphrase, setPassphraseState] = useState<string | null | undefined>(undefined);
  const [authError, setAuthError] = useState<string | undefined>();
  const [teams, setTeams] = useState<TeamsState>({ status: "idle" });
  // A new value starts the fetch again, for the retry button.
  const [attempt, setAttempt] = useState(0);
  // The refresh after a 422 runs outside the effect, so it reads this flag before it sets state.
  const mounted = useRef(true);

  useEffect(() => {
    // React strict mode runs the cleanup and the effect again on mount, so the effect sets the flag.
    mounted.current = true;
    setPassphraseState(getPassphrase());
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (!passphrase) return;
    // A stale answer must not overwrite the state after a new submit or an unmount.
    let current = true;
    // Stored teams show at once. The fetch still runs, because a roster can change after a trade.
    const stored = readStoredTeams();
    setTeams(stored ? { status: "ready", teams: stored } : { status: "loading" });
    fetchAndStoreTeams(passphrase)
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
    clearStoredTeams();
    fetchAndStoreTeams(passphrase)
      .then((list) => mounted.current && setTeams({ status: "ready", teams: list }))
      .catch((error: unknown) => {
        if (!mounted.current) return;
        if (error instanceof ApiError && error.status === 401) handleUnauthorized();
        // Any other failure keeps the current list. The error line of the form already tells the reader.
      });
  }

  function handleSubmit(value: string) {
    setPassphrase(value);
    setAuthError(undefined);
    setPassphraseState(value);
  }

  /* The form and every state of the fetch sit in one chapter, so from the tablet tier they read as one white card.
     The chapter carries the gutter and the vertical padding. */
  const states = (
    <>
      <PassphraseDialog open={passphrase === null} error={authError} onSubmit={handleSubmit} />
      {teams.status === "loading" && <TeamsSkeleton />}
      {teams.status === "rate-limited" && <ErrorLine>{retryText(teams.retryAfter)}</ErrorLine>}
      {teams.status === "failed" && (
        <div className="flex flex-col gap-sp-3">
          <ErrorLine>The API did not answer. Try again.</ErrorLine>
          <Button className="press h-touch w-full rounded-card px-sp-4 text-lead font-bold" onClick={() => setAttempt((n) => n + 1)}>
            Try Again
          </Button>
        </div>
      )}
    </>
  );

  if (teams.status !== "ready" || !passphrase) return <Chapter>{states}</Chapter>;

  return (
    <TradeForm teams={teams.teams} season={season} finderOn={finderOn} passphrase={passphrase} onUnauthorized={handleUnauthorized} onRostersStale={handleStaleRosters}>
      {/* The result sits after the chapter, not inside it, so its own chapters read as cards under the form card. */}
      {({ form, result }) => (
        <>
          <Chapter>
            {states}
            {/* The form is the content of the route, so it fades and rises in once when it first shows. With motion off it shows at rest. */}
            <Reveal trigger="mount" duration={DURATION.page}>
              {form}
            </Reveal>
          </Chapter>
          {result}
        </>
      )}
    </TradeForm>
  );
}
