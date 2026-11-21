/**
 * Waiver hits and misses, a chapter of Act II: the top hits by Points over the line, the top misses with their bids,
 * the claims lost by a few dollars, and the teams that streamed QB, K, and DEF, the streaming king first.
 */
import { count, oneDecimal } from "@cpc/design/format/format";
import { ReportCard } from "../report/report-card";
import { signedOne } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import { ShowAll } from "../report/show-all";
import { WordTag } from "../report/word-tag";
import type { Pickup, WaiversChapter } from "../schema/midseason-types";

type Facts = WaiversChapter["facts"];

const ROW =
  "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0";

/* A free agent add has no bid, so it shows as a free add. */
const bidText = (bid: number) => (bid > 0 ? `$${bid}` : "Free add");

function PickupRow({ pickup }: { pickup: Pickup }) {
  return (
    <li className={ROW}>
      <span className="min-w-0">
        <span className="text-body block leading-tight font-bold">{pickup.player}</span>
        <span className="text-meta text-ink-2 block leading-tight">
          {pickup.position} · {pickup.team} · week {pickup.week} · {bidText(pickup.bid)}
        </span>
      </span>
      <span className="text-right">
        <span className="text-body block font-mono font-bold tabular-nums">
          {pickup.points_over_line !== null
            ? signedOne(pickup.points_over_line)
            : oneDecimal(pickup.points)}
        </span>
        <span className="text-meta text-mute block font-mono tabular-nums">
          {count(pickup.starts, "start", "starts")}
        </span>
      </span>
    </li>
  );
}

function Pickups({ label, rows }: { label: string; rows: Pickup[] }) {
  return (
    <div className="gap-sp-2 flex flex-col">
      <h4 className="text-body m-0 leading-tight font-bold">{label}</h4>
      <ReportCard className="py-sp-1">
        <ol aria-label={label} className="m-0 list-none p-0">
          {rows.map((pickup) => (
            <PickupRow
              key={`${pickup.player_id}-${pickup.roster_id}-${pickup.week}`}
              pickup={pickup}
            />
          ))}
        </ol>
      </ReportCard>
    </div>
  );
}

function OutbidList({ outbid }: { outbid: Facts["outbid"] }) {
  return (
    <div className="gap-sp-2 flex flex-col">
      <h4 className="text-body m-0 leading-tight font-bold">Outbid</h4>
      <ReportCard className="py-sp-1">
        <ol aria-label="Outbid" className="m-0 list-none p-0">
          {outbid.map((row) => (
            <li
              key={`${row.player_id}-${row.roster_id}`}
              className="border-rule py-sp-2 text-meta border-b leading-tight last:border-b-0"
            >
              <span className="text-ink font-semibold">{row.team}</span>
              <span className="text-ink-2">
                {" "}
                bid ${row.bid} on {row.player} and lost to {row.winner} by ${row.margin}. He
                gave{" "}
              </span>
              <span className="font-mono font-bold tabular-nums">
                {signedOne(row.winner_points_over_line)}
              </span>
              <span className="text-ink-2"> over the line.</span>
            </li>
          ))}
        </ol>
      </ReportCard>
    </div>
  );
}

function Streamers({ streamers }: { streamers: Facts["streamers"] }) {
  return (
    <div className="gap-sp-2 flex flex-col">
      <h4 className="text-body m-0 leading-tight font-bold">Streamers of QB, K, and DEF</h4>
      <ReportCard className="py-sp-1">
        <ShowAll
          label="Streamers"
          rows={streamers.map((row, index) => (
            <li key={row.roster_id} className={ROW}>
              <span className="min-w-0">
                <span className="text-body block leading-tight font-bold">
                  {row.team}
                  {index === 0 && <WordTag>Streaming king</WordTag>}
                </span>
                <span className="text-meta text-ink-2 block leading-tight">
                  {count(row.players, "player", "players")}, {count(row.starts, "start", "starts")}
                </span>
              </span>
              <span className="text-body font-mono font-bold tabular-nums">
                {oneDecimal(row.points)}
              </span>
            </li>
          ))}
        />
      </ReportCard>
    </div>
  );
}

export function Waivers({ chapter }: { chapter: WaiversChapter }) {
  const { hits, misses, outbid, streamers } = chapter.facts;
  return (
    <ReportChapter
      id={chapter.key}
      title={chapter.title}
      note="Points over the line"
      blurb={chapter.blurb}
    >
      <div className="gap-sp-4 desktop:grid-cols-2 grid">
        <Pickups label="Hits" rows={hits} />
        <Pickups label="Misses" rows={misses} />
      </div>
      {outbid.length > 0 && <OutbidList outbid={outbid} />}
      {streamers.length > 0 && <Streamers streamers={streamers} />}
    </ReportChapter>
  );
}
