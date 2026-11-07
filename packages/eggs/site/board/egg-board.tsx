/**
 * The plain egg board: the counts, one card per egg word with each manager and the letters of the manager, and the feed.
 * It renders the board answer of the API, which holds no page and no spot.
 */
import type { Board } from "../lib/api";

export function EggBoard({ board }: { board: Board }) {
  const { left, found, to_drop } = board.counts;
  return (
    <div className="flex flex-col gap-sp-5">
      <p className="text-lead font-bold">{`${left} left to find · ${found} found · ${to_drop} to drop`}</p>
      {board.words.map((word) => (
        <section key={word.word} aria-labelledby={`egg-word-${word.word}`} className="flex flex-col gap-sp-2 rounded-card bg-card p-gutter">
          <h2 id={`egg-word-${word.word}`} className="text-stat font-black uppercase">
            {word.word} <span className="text-mute">${word.prize}</span>
          </h2>
          <ul className="flex flex-col gap-sp-1">
            {word.managers.map((manager) => (
              <li key={manager.roster_id} className="flex justify-between gap-sp-3 text-body">
                <span>{manager.team}</span>
                <span className="font-mono font-bold">{manager.letters.join(" ") || "–"}</span>
              </li>
            ))}
          </ul>
        </section>
      ))}
      <section aria-labelledby="egg-latest" className="flex flex-col gap-sp-2 rounded-card bg-card p-gutter">
        <h2 id="egg-latest" className="text-stat font-black uppercase">Latest claims</h2>
        <ul className="flex flex-col gap-sp-1">
          {board.latest.map((claim) => (
            <li key={`${claim.claimed_at}-${claim.roster_id}-${claim.letter}`} className="text-body">
              {`${claim.team} · ${claim.letter} · ${claim.word}`}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
