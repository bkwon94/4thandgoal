/**
 * The claim sheet: the team pills, a card for each egg word, the block notice, the passphrase field when the browser has
 * none, and the claim ticket. The locked stub of the ticket names the next step that is missing, so a manager knows what to do.
 */
"use client";

import { PendingButton } from "@cpc/design/ui/pending-button";
import { useEffect, useRef, useState } from "react";
import { Label } from "@cpc/design/parts/label";
import {
  Sheet,
  SheetBackdrop,
  SheetClose,
  SheetContent,
  SheetGrip,
  SheetTitle,
} from "@cpc/design/ui/sheet";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import { EggsError, type Board, type ClaimAnswer, type EggsApi } from "../lib/api";
import { clearPassphrase, getPassphrase, setPassphrase } from "../lib/passphrase";
import { ClaimTicket, STAMP_MS, type Send } from "./claim-ticket";
import { ArtGround, SlotRow } from "./egg-art";
import { hasOpenSlot, heldLetters, leaderLine, slotsOf } from "./slots";

type ClaimSheetProps = {
  api: EggsApi;
  letter: string;
  token: string;
  // The answer of the claim, with the gift card of the egg word and the team, for the hero card.
  onClaimed: (answer: ClaimAnswer, prize: number | null, team: string) => void;
  onClaimedFirst: () => void;
  onClose: () => void;
};

type Word = Board["words"][number];

const WRONG_PASSPHRASE = "The passphrase is wrong. Ask a league member for it.";

/* The label of the stub of the claim ticket: the first missing step, or the claim itself. The stub is locked until no step is missing. */
function stubLabel(
  letter: string,
  team: number | null,
  word: string | null,
  block: boolean,
  passphrase: string,
): { label: string; locked: boolean } {
  if (team === null) return { label: "Pick your team", locked: true };
  if (!block && word === null) return { label: "Pick an egg word", locked: true };
  if (!passphrase) return { label: "Enter the passphrase", locked: true };
  return {
    label: block ? `Tear to claim ${letter} as a block` : `Tear to claim ${letter} for ${word}`,
    locked: false,
  };
}

/* True when the manager can put the letter in the word: the word has no winner and a free slot for the letter. */
function fits(word: Word, team: number, letter: string): boolean {
  return word.winner === null && hasOpenSlot(word.word, heldLetters(word, team), letter);
}

export function ClaimSheet({
  api,
  letter,
  token,
  onClaimed,
  onClaimedFirst,
  onClose,
}: ClaimSheetProps) {
  const [board, setBoard] = useState<Board | null>(null);
  const [team, setTeam] = useState<number | null>(null);
  const [word, setWord] = useState<string | null>(null);
  // The field shows only when the browser holds no passphrase.
  const [stored, setStored] = useState(() => getPassphrase());
  const [typed, setTyped] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [send, setSend] = useState<Send>("idle");
  const motion = !useMotionOff();
  // The stamp holds on the ticket, then the end card shows. A close of the sheet in the hold stops the timer.
  const hold = useRef<ReturnType<typeof setTimeout> | null>(null);
  const asked = useRef(false);

  useEffect(
    () => () => {
      if (hold.current !== null) clearTimeout(hold.current);
    },
    [],
  );

  useEffect(() => {
    api.board().then(setBoard, () => setError("The egg board did not load. Try again."));
  }, [api]);

  const manager = board?.managers.find((each) => each.roster_id === team) ?? null;
  // A letter that fits no egg word of the manager can only be a block.
  const block =
    board !== null && team !== null && !board.words.some((each) => fits(each, team, letter));
  const passphrase = stored ?? typed.trim();
  const { label, locked } = stubLabel(letter, team, word, block, passphrase);
  const ready = !locked && send === "idle";

  function pickTeam(rosterId: number | null) {
    setTeam(rosterId);
    setWord(null);
  }

  async function claim() {
    if (team === null || !ready) return;
    const target = block ? null : word;
    setSend("sending");
    setError(null);
    try {
      const answer = await api.claim(passphrase, { token, roster_id: team, word: target });
      setPassphrase(passphrase);
      const prize = board?.words.find((each) => each.word === target)?.prize ?? null;
      setSend("claimed");
      hold.current = setTimeout(() => onClaimed(answer, prize, manager?.team ?? ""), STAMP_MS);
    } catch (failure) {
      if (failure instanceof EggsError && failure.status === 401) {
        clearPassphrase();
        setStored(null);
        setTyped("");
        setError(WRONG_PASSPHRASE);
        setSend("idle");
      } else if (failure instanceof EggsError && failure.status === 409) {
        // The stub comes back under the TAKEN stamp, then the end card for another manager first shows.
        setSend("taken");
        hold.current = setTimeout(onClaimedFirst, STAMP_MS);
      } else {
        // A refusal of the API is a 422 that names its reason, so the sheet shows the reason.
        setError(
          failure instanceof EggsError
            ? failure.message
            : "The claim did not go through. Try again.",
        );
        setSend("idle");
      }
    }
  }

  return (
    <Sheet
      side="bottom"
      open
      onOpenChange={(next) => {
        // A drag close reports twice before the hunt drops the sheet, and the hunt must hear one close.
        if (!next && !asked.current) {
          asked.current = true;
          onClose();
        }
      }}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      <SheetBackdrop />
      {/* The Drawer owns the slide, the drag, the dim, the focus trap, and the fade under reduced motion. The sheet is a
          bottom sheet at every tier, so the tablet tier keeps the same edge and a max width. */}
      <SheetContent className="rounded-t-hero border-rule mx-auto flex max-h-[92dvh] w-full max-w-lg flex-col border border-b-0">
        {/* The grip says "sheet" to a thumb. A drag down on the sheet closes it. */}
        <SheetGrip className="mt-sp-3 h-sp-1 w-sp-6" />
        {/* The body scrolls when its content is taller than the sheet. Each part with no content of its own to hold its
            height takes flex-none, or the column shrinks it: the hero, whose overflow-hidden lets it shrink. */}
        <div className="gap-sp-5 px-gutter pt-sp-3 pb-sp-6 flex min-h-0 flex-1 flex-col overflow-y-auto overscroll-contain">
          <div className="egg-up gap-sp-3 rounded-tile border-rule-dark bg-band p-sp-3 text-on-dark relative flex flex-none items-center overflow-hidden border">
            <span className="relative flex-none">
              {/* The ground reaches the edges of the hero on the left, top, and bottom. On the right it stops at the edge of
                  the tile, so the full gap lies between the ground and the title. */}
              <ArtGround inset="-inset-y-sp-3 -left-sp-3 right-0" />
              {/* The tile is taller than the glyph box of the letter at the largest headline size, 46px, so axe can read its contrast. */}
              <span className="rounded-letter bg-accent text-headline text-on-dark shadow-orb relative flex size-16 items-center justify-center font-mono font-bold">
                {letter}
              </span>
            </span>
            <div className="gap-sp-1 flex min-w-0 flex-col">
              <Label dark className="text-meta mb-0">
                Claim
              </Label>
              {/* Each line is its own element. axe reads the page under the sheet at each line of an element, and a line
                  that wraps sits over two parts of the page, so axe then cannot read its contrast. The break leaves room
                  for a wide letter in the narrow column at 340px. */}
              <SheetTitle id="egg-claim-title" className="text-stat m-0 leading-tight font-bold">
                <span className="block">{`Put ${letter} in`}</span>{" "}
                <span className="block">an egg word.</span>
              </SheetTitle>
            </div>
            <SheetClose
              aria-label="Close"
              className="press size-touch rounded-pill bg-band text-on-dark-muted ml-auto flex flex-none items-center justify-center self-start"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                aria-hidden="true"
              >
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </SheetClose>
          </div>

          <section className="egg-up egg-up-1 flex flex-col">
            <Label className="text-meta">1 · Who are you?</Label>
            {manager === null ? (
              <div role="group" aria-label="Your team" className="gap-sp-2 flex flex-wrap">
                {board?.managers.map((each) => (
                  <PendingButton
                    key={each.roster_id}
                    type="button"
                    onClick={() => pickTeam(each.roster_id)}
                    className="press min-h-touch rounded-pill border-rule bg-card px-sp-4 text-body text-ink border font-bold"
                  >
                    {each.team}
                  </PendingButton>
                ))}
              </div>
            ) : (
              <div className="egg-pop gap-sp-2 flex flex-wrap items-center">
                <span className="min-h-touch gap-sp-2 rounded-pill bg-ink px-sp-4 text-body text-page inline-flex items-center font-bold">
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M20 6 9 17l-5-5" />
                  </svg>
                  {manager.team}
                </span>
                <PendingButton
                  type="button"
                  onClick={() => pickTeam(null)}
                  className="press min-h-touch px-sp-3 text-body text-accent-ink font-bold"
                >
                  Change
                </PendingButton>
              </div>
            )}
          </section>

          {board !== null && team !== null && (
            <section className="gap-sp-3 flex flex-col">
              <Label className="egg-up text-meta mb-0">2 · Where does {letter} go?</Label>
              <div role="group" aria-label="Egg word" className="gap-sp-3 flex flex-col">
                {board.words.map((each, index) => (
                  <WordCard
                    key={each.word}
                    word={each}
                    team={team}
                    letter={letter}
                    step={index + 1}
                    picked={word === each.word}
                    onPick={() => setWord(each.word)}
                  />
                ))}
              </div>
              {block && (
                <div className="egg-up egg-up-4 gap-sp-3 rounded-card border-accent bg-card p-sp-4 flex items-center border-2 border-dashed">
                  <span className="rounded-letter border-accent text-score text-accent-ink flex size-11 flex-none items-center justify-center border-2 border-dashed font-mono font-bold">
                    {letter}
                  </span>
                  <div className="gap-sp-0 flex flex-col">
                    <span className="text-body font-bold">
                      {letter} fits none of your egg words.
                    </span>
                    <span className="text-meta text-ink-2">
                      Claim it as a block. Then no other manager can put it in a word.
                    </span>
                  </div>
                </div>
              )}
            </section>
          )}

          {stored === null && (
            <label className="flex flex-col">
              <span className="mb-sp-3 text-meta text-accent-ink leading-tight font-bold tracking-wide uppercase">
                3 · League passphrase
              </span>
              <input
                type="password"
                autoComplete="off"
                value={typed}
                onChange={(event) => setTyped(event.target.value)}
                className="min-h-touch rounded-tile border-rule bg-card px-sp-4 text-lead text-ink border"
              />
            </label>
          )}

          {error && (
            <p role="alert" className="text-lead text-accent-ink">
              {error}
            </p>
          )}

          <div className="gap-sp-2 flex flex-col">
            <ClaimTicket
              letter={letter}
              word={block ? null : word}
              block={block}
              team={manager?.team ?? null}
              label={label}
              locked={locked}
              send={send}
              motion={motion}
              onTear={claim}
            />
            {/* Each sentence is its own line. A line that wraps sits over two parts of the page under the sheet, and axe then
                cannot read its contrast. */}
            <span className="text-meta text-mute text-center">
              <span className="block">The first claim wins the egg.</span>
              <span className="block">The commissioner can undo a claim.</span>
            </span>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

/* The card of one egg word: its gift card, the count of the manager, the tiles, the bar, and the leader.
   A ghost tile pulses where the letter lands. A word with no open slot for the letter is faded and disabled.
   The fade is the muted tokens on the raised surface, not an opacity: the entry motion of the card holds its opacity
   at 1, and the muted text keeps the contrast floor of 4.5 to 1 on the raised surface. */
function WordCard({
  word,
  team,
  letter,
  step,
  picked,
  onPick,
}: {
  word: Word;
  team: number;
  letter: string;
  step: number;
  picked: boolean;
  onPick: () => void;
}) {
  const held = heldLetters(word, team);
  const open = fits(word, team, letter);
  const shown = held.length + (picked ? 1 : 0);
  const note = open
    ? leaderLine(word)
    : word.winner !== null
      ? `${word.winner.team} won ${word.word}.`
      : `No open ${letter} in this word.`;
  // The card takes its name from the text it shows, so the name holds each visible word (WCAG 2.5.3). The slot row is
  // aria-hidden, as the count says the same.
  return (
    <PendingButton
      type="button"
      aria-pressed={picked}
      disabled={!open}
      onClick={onPick}
      className={cn(
        "press egg-up gap-sp-3 rounded-card p-sp-4 text-ink flex w-full flex-col border text-left",
        `egg-up-${Math.min(step, 4)}`,
        picked
          ? "border-accent bg-raised ring-accent-glow ring-4"
          : open
            ? "border-rule bg-card"
            : "border-rule bg-raised text-mute border-dashed",
      )}
    >
      <span className="gap-sp-2 flex w-full items-baseline">
        <span className="text-body font-bold tracking-wide">{word.word}</span>{" "}
        {/* The spaces between the parts of the row keep the words of the name apart. A flex row shows no space. */}
        <span
          className={cn(
            "rounded-pill border-rule px-sp-2 text-meta border font-mono font-bold",
            open ? "text-ink-2" : "text-mute",
          )}
        >
          ${word.prize}
        </span>{" "}
        <span
          className={cn(
            "text-row ml-auto font-mono font-bold",
            picked ? "text-accent-ink" : open ? "text-ink" : "text-mute",
          )}
        >
          {shown}
          <span className="text-mute">/{word.word.length}</span>
        </span>
      </span>
      <SlotRow
        slots={slotsOf(word.word, held, open ? letter : null)}
        tone="page"
        picked={picked}
        faded={!open}
      />
      <span className="rounded-pill bg-raised block h-1 w-full overflow-hidden">
        <span
          className={cn(
            "rounded-pill ease-rise block h-full transition-[width] duration-500",
            picked ? "bg-accent" : open ? "bg-ink" : "bg-mute",
          )}
          style={{ width: `${Math.round((shown / word.word.length) * 100)}%` }}
        />
      </span>
      <span className="text-meta text-mute">{note}</span>
    </PendingButton>
  );
}
