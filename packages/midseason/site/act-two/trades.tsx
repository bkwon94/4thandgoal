/**
 * The trade report card, a chapter of Act II: the top 3 trades as full cards with the record of each team since the
 * trade, then every other trade as a short row. A player out in the first week after his trade has a tag.
 */
import { oneDecimal } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { ReportCard } from "../report/report-card";
import { fullRecord, signedOne } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import { ShowAll } from "../report/show-all";
import { WordTag } from "../report/word-tag";
import type { TradeCard, TradesChapter } from "../schema/midseason-types";

/* The trades that show as full cards (decision ticket 04). */
export const FULL_CARDS = 3;
export const HURT_ON_ARRIVAL = "Hurt on arrival";

type Side = TradeCard["sides"][number];

/* The players a side got, each with the hurt on arrival tag when he missed the first week. */
function Got({ side }: { side: Side }) {
  return (
    <ul className="m-0 flex list-none flex-col gap-sp-1 p-0">
      {side.got.map((player) => (
        <li key={player.player_id} className="text-meta leading-tight text-ink-2">
          <span className="font-semibold text-ink">{player.player}</span> {player.position}
          {player.points_over_line !== null && (
            <span className="font-mono tabular-nums"> {signedOne(player.points_over_line)}</span>
          )}
          {player.hurt_on_arrival && <WordTag tone="accent">{HURT_ON_ARRIVAL}</WordTag>}
        </li>
      ))}
    </ul>
  );
}

/* The result of a trade as a mono caps word with no box, in the ink color for a trade with a winner. */
function Result({ trade }: { trade: TradeCard }) {
  return (
    <span
      className={cn(
        "font-mono text-label font-bold tracking-caps uppercase",
        trade.winner !== null ? "text-ink" : "text-mute",
      )}
    >
      {trade.result}
    </span>
  );
}

function FullCard({ trade }: { trade: TradeCard }) {
  return (
    <ReportCard as="article" className="flex flex-col gap-sp-3">
      <div className="flex flex-wrap items-baseline justify-between gap-sp-2">
        <span className="font-mono text-meta tracking-caps text-mute uppercase">Week {trade.week}</span>
        <Result trade={trade} />
      </div>
      {trade.winner !== null && (
        <p className="m-0 text-lead leading-tight">
          <span className="font-bold">{trade.winner}</span> leads by{" "}
          <span className="font-mono font-bold tabular-nums">{oneDecimal(trade.gap)}</span> points over the line.
        </p>
      )}
      <div className="grid gap-sp-3 tablet:grid-cols-2">
        {trade.sides.map((side) => (
          <div key={side.roster_id} data-side className="flex flex-col gap-sp-1 border-t border-rule pt-sp-2">
            <span className="flex flex-wrap items-baseline justify-between gap-x-sp-2">
              <span data-team className="text-body leading-tight font-bold">
                {side.team}
              </span>
              <span className="font-mono text-meta text-ink-2 tabular-nums">
                {fullRecord(side.since.wins, side.since.losses, side.since.ties)} since
              </span>
            </span>
            <span className="font-mono text-meta text-mute tabular-nums">Net {signedOne(side.net)}</span>
            <Got side={side} />
          </div>
        ))}
      </div>
    </ReportCard>
  );
}

/* One short row of a trade after the top 3: the week, the result, and what each side got. */
function ShortRow({ trade }: { trade: TradeCard }) {
  return (
    <li className="flex flex-col gap-sp-1 border-b border-rule py-sp-2 last:border-b-0">
      <span className="flex flex-wrap items-baseline justify-between gap-sp-2">
        <span className="font-mono text-meta tracking-caps text-mute uppercase">Week {trade.week}</span>
        <Result trade={trade} />
      </span>
      {trade.sides.map((side) => (
        <span key={side.roster_id} className="text-meta leading-tight">
          <span className="font-semibold">{side.team}</span>
          <span className="text-ink-2"> got </span>
          {side.got.map((player, index) => (
            <span key={player.player_id} className="text-ink-2">
              {index > 0 && ", "}
              {player.player}
              {player.hurt_on_arrival && <WordTag tone="accent">{HURT_ON_ARRIVAL}</WordTag>}
            </span>
          ))}
        </span>
      ))}
    </li>
  );
}

export function Trades({ chapter }: { chapter: TradesChapter }) {
  const { trades } = chapter.facts;
  const rest = trades.slice(FULL_CARDS);
  return (
    <ReportChapter id={chapter.key} title={chapter.title} note={`${trades.length} trades`} blurb={chapter.blurb}>
      <div className="flex flex-col gap-sp-3">
        {trades.slice(0, FULL_CARDS).map((trade) => (
          <FullCard key={trade.transaction_id} trade={trade} />
        ))}
      </div>
      {rest.length > 0 && (
        <ReportCard className="py-sp-1">
          <ShowAll
            label="Every other trade"
            rows={rest.map((trade) => (
              <ShortRow key={trade.transaction_id} trade={trade} />
            ))}
          />
        </ReportCard>
      )}
    </ReportChapter>
  );
}
