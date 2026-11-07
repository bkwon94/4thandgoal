/**
 * The plain claim sheet: the team pills, the egg words, the passphrase field when the browser has none, and the claim.
 * The button names the next step that is missing, so a manager knows what to do.
 */
"use client";

import { useEffect, useState } from "react";
import { EggsError, type Board, type ClaimAnswer, type EggsApi } from "../lib/api";
import { clearPassphrase, getPassphrase, setPassphrase } from "../lib/passphrase";

type ClaimSheetProps = {
  api: EggsApi;
  letter: string;
  token: string;
  onClaimed: (answer: ClaimAnswer) => void;
  onClaimedFirst: () => void;
  onClose: () => void;
};

const WRONG_PASSPHRASE = "The passphrase is wrong. Ask a league member for it.";

/* The label of the claim button: the first missing step, or the claim itself. */
function buttonLabel(letter: string, team: number | null, word: string | null, passphrase: string): string {
  if (team === null) return "Pick your team";
  if (word === null) return "Pick an egg word";
  if (!passphrase) return "Enter the passphrase";
  return `Claim ${letter}`;
}

export function ClaimSheet({ api, letter, token, onClaimed, onClaimedFirst, onClose }: ClaimSheetProps) {
  const [board, setBoard] = useState<Board | null>(null);
  const [team, setTeam] = useState<number | null>(null);
  const [word, setWord] = useState<string | null>(null);
  // The field shows only when the browser holds no passphrase.
  const [stored, setStored] = useState(() => getPassphrase());
  const [typed, setTyped] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.board().then(setBoard, () => setError("The egg board did not load. Try again."));
  }, [api]);

  const passphrase = stored ?? typed.trim();
  const label = buttonLabel(letter, team, word, passphrase);
  const ready = label === `Claim ${letter}` && !busy;

  async function claim() {
    if (team === null || word === null || !ready) return;
    setBusy(true);
    setError(null);
    try {
      const answer = await api.claim(passphrase, { token, roster_id: team, word });
      setPassphrase(passphrase);
      onClaimed(answer);
    } catch (failure) {
      if (failure instanceof EggsError && failure.status === 401) {
        clearPassphrase();
        setStored(null);
        setTyped("");
        setError(WRONG_PASSPHRASE);
      } else if (failure instanceof EggsError && failure.status === 409) {
        onClaimedFirst();
      } else {
        setError(failure instanceof EggsError ? failure.message : "The claim did not go through. Try again.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="egg-claim-title" className="fixed inset-0 z-50 grid place-items-center overflow-y-auto bg-page/80 p-gutter">
      <div className="flex w-full max-w-md flex-col gap-sp-4 rounded-card bg-card p-gutter text-ink">
        <h2 id="egg-claim-title" className="text-stat font-black uppercase">Claim {letter}</h2>
        <div role="group" aria-label="Your team" className="flex flex-wrap gap-sp-2">
          {board?.managers.map((manager) => (
            <button
              key={manager.roster_id}
              type="button"
              aria-pressed={team === manager.roster_id}
              onClick={() => setTeam(manager.roster_id)}
              className="min-h-touch rounded-pill border border-rule px-sp-3 font-bold aria-pressed:bg-accent aria-pressed:text-accent-foreground"
            >
              {manager.team}
            </button>
          ))}
        </div>
        <div role="group" aria-label="Egg word" className="flex flex-col gap-sp-2">
          {board?.words.map((each) => (
            <button
              key={each.word}
              type="button"
              aria-pressed={word === each.word}
              onClick={() => setWord(each.word)}
              className="min-h-touch rounded-card border border-rule px-sp-3 text-left font-bold aria-pressed:border-accent"
            >
              {each.word}
            </button>
          ))}
        </div>
        {stored === null && (
          <label className="flex flex-col gap-sp-1 text-meta font-bold uppercase">
            Passphrase
            <input
              type="password"
              autoComplete="off"
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              className="min-h-touch rounded-card border border-rule bg-page px-sp-3 text-body normal-case"
            />
          </label>
        )}
        {error && <p role="alert" className="text-body text-accent-text">{error}</p>}
        <button
          type="button"
          disabled={!ready}
          onClick={claim}
          className="min-h-touch rounded-card bg-accent font-bold text-accent-foreground disabled:opacity-60"
        >
          {label}
        </button>
        <button type="button" onClick={onClose} className="min-h-touch font-bold">
          Close
        </button>
      </div>
    </div>
  );
}
