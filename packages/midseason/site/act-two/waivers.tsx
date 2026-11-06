/**
 * Waiver hits and misses, a chapter of Act II: the top hits by Points over the line, the top misses with their bids,
 * the claims lost by a few dollars, and the teams that streamed QB, K, and DEF, the streaming king first. A hit that
 * its team let go carries "the one that got away" line, as a draft steal does.
 */
import { count, num } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { Tag } from "@cpc/design/parts/tag";
import { signedOne } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import { ShowAll } from "../report/show-all";
import type { Pickup, WaiversChapter } from "../schema/midseason-types";

type Facts = WaiversChapter["facts"];

const ROW = "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0";

/* A free agent add has no bid, so it shows as a free add. */
const bidText = (bid: number) => (bid > 0 ? `$${bid}` : "Free add");

function PickupRow({ pickup }: { pickup: Pickup }) {
  return (
    <li className={ROW}>
      <span className="min-w-0">
        <span className="block text-body leading-tight font-bold">{pickup.player}</span>
        <span className="block text-meta leading-tight text-ink-2">
          {pickup.position} · {pickup.team} · week {pickup.week} · {bidText(pickup.bid)}
        </span>
        {pickup.line !== null && (
          <span className="block text-meta leading-tight font-semibold text-accent-ink">
            {pickup.line.charAt(0).toUpperCase() + pickup.line.slice(1)}
          </span>
        )}
      </span>
      <span className="text-right">
        <span className="block font-mono text-body font-bold tabular-nums">
          {pickup.points_over_line !== null ? signedOne(pickup.points_over_line) : num(pickup.points)}
        </span>
        <span className="block font-mono text-meta text-mute tabular-nums">{count(pickup.starts, "start", "starts")}</span>
      </span>
    </li>
  );
}

function Pickups({ label, rows }: { label: string; rows: Pickup[] }) {
  return (
    <div className="flex flex-col gap-sp-2">
      <h4 className="m-0 text-body leading-tight font-bold">{label}</h4>
      <Card className="py-sp-1">
        <ol aria-label={label} className="m-0 list-none p-0">
          {rows.map((pickup) => (
            <PickupRow key={`${pickup.player_id}-${pickup.roster_id}-${pickup.week}`} pickup={pickup} />
          ))}
        </ol>
      </Card>
    </div>
  );
}

function OutbidList({ outbid }: { outbid: Facts["outbid"] }) {
  return (
    <div className="flex flex-col gap-sp-2">
      <h4 className="m-0 text-body leading-tight font-bold">Outbid</h4>
      <Card className="py-sp-1">
        <ol aria-label="Outbid" className="m-0 list-none p-0">
          {outbid.map((row) => (
            <li key={`${row.player_id}-${row.roster_id}`} className="border-b border-rule py-sp-2 text-meta leading-tight last:border-b-0">
              <span className="font-semibold text-ink">{row.team}</span>
              <span className="text-ink-2">
                {" "}bid ${row.bid} on {row.player} and lost to {row.winner} by ${row.margin}. He gave{" "}
              </span>
              <span className="font-mono font-bold tabular-nums">{signedOne(row.winner_points_over_line)}</span>
              <span className="text-ink-2"> over the line.</span>
            </li>
          ))}
        </ol>
      </Card>
    </div>
  );
}

function Streamers({ streamers }: { streamers: Facts["streamers"] }) {
  return (
    <div className="flex flex-col gap-sp-2">
      <h4 className="m-0 text-body leading-tight font-bold">Streamers of QB, K, and DEF</h4>
      <Card className="py-sp-1">
        <ShowAll
          label="Streamers"
          rows={streamers.map((row, index) => (
            <li key={row.roster_id} className={ROW}>
              <span className="min-w-0">
                <span className="block text-body leading-tight font-bold">
                  {row.team}
                  {index === 0 && <Tag className="text-meta">Streaming king</Tag>}
                </span>
                <span className="block text-meta leading-tight text-ink-2">
                  {count(row.players, "player", "players")}, {count(row.starts, "start", "starts")}
                </span>
              </span>
              <span className="font-mono text-body font-bold tabular-nums">{num(row.points)}</span>
            </li>
          ))}
        />
      </Card>
    </div>
  );
}

export function Waivers({ chapter }: { chapter: WaiversChapter }) {
  const { hits, misses, outbid, streamers } = chapter.facts;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} note="Points over the line" blurb={chapter.blurb} roast={chapter.roast}>
      <div className="grid gap-sp-4 desktop:grid-cols-2">
        <Pickups label="Hits" rows={hits} />
        <Pickups label="Misses" rows={misses} />
      </div>
      {outbid.length > 0 && <OutbidList outbid={outbid} />}
      {streamers.length > 0 && <Streamers streamers={streamers} />}
    </ReportChapter>
  );
}
