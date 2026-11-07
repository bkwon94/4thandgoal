/**
 * The plain find card: the egg holds a letter, and one button opens the claim sheet.
 * The look of the find, with the blur, the ring, and the crack, belongs to a later ticket.
 */
"use client";

export function FindCard({ letter, onClaim, onClose }: { letter: string; onClaim: () => void; onClose: () => void }) {
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="egg-find-title" className="fixed inset-0 z-50 grid place-items-center bg-page/80 p-gutter">
      <div className="flex w-full max-w-sm flex-col items-center gap-sp-3 rounded-card bg-card p-gutter text-ink">
        <h2 id="egg-find-title" className="text-stat font-black uppercase">You found an egg</h2>
        <p data-testid="egg-letter" className="text-hero font-black text-accent-text">{letter}</p>
        <button type="button" onClick={onClaim} className="min-h-touch w-full rounded-card bg-accent font-bold text-accent-foreground">
          Claim {letter}
        </button>
        <button type="button" onClick={onClose} className="min-h-touch w-full font-bold">
          Close
        </button>
      </div>
    </div>
  );
}
