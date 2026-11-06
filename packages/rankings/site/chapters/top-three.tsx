/**
 * The Power Rankings card of the home page: the top three teams of the last week, then a link to all teams.
 * Each row shows the rank, the avatar, the team, the record with the movement, and the playoff odds.
 */
import { Card } from "@cpc/design/parts/card";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import type { RankingsWeek } from "../schema/rankings-types";
import { PlayoffOdds, RecordLine } from "./power-rankings";

/* The avatar of each roster id, with the folder of the latest week in front of each path. */
type AvatarMap = Readonly<Record<string, string>>;

/* The rank in two digits, as the Ladder shows "01". */
const twoDigits = (rank: number) => String(rank).padStart(2, "0");

export function TopThree({ week, avatars, href }: { week: RankingsWeek; avatars: AvatarMap; href: string }) {
  return (
    <Card className="py-sp-2">
      <ol aria-label="Top three" className="m-0 list-none p-0">
        {week.rows.slice(0, 3).map((row) => (
          <li
            key={row.roster_id}
            className="grid grid-cols-[auto_auto_minmax(0,1fr)_auto] items-center gap-x-sp-3 py-sp-2"
          >
            <span className="font-mono text-row font-bold tabular-nums">{twoDigits(row.rank)}</span>
            <Avatar src={avatarSrc(avatars, row.roster_id)} />
            <span className="flex min-w-0 flex-col">
              <span className="text-row leading-tight font-bold">{row.name}</span>
              <span className="mt-sp-0 font-mono text-meta leading-tight text-ink-2 tabular-nums">
                <RecordLine row={row} />
              </span>
            </span>
            <span className="font-mono text-row font-bold tabular-nums">
              <span className="sr-only">Playoff odds </span>
              <PlayoffOdds odds={row.odds} />
            </span>
          </li>
        ))}
      </ol>
      {/* The link is a whole row, so it is 44px tall. The arrow is drawn, because axe cannot read the contrast of a glyph. */}
      <a
        href={href}
        className="press flex min-h-touch items-center gap-sp-1 border-t border-rule font-mono text-meta font-bold tracking-caps text-accent-ink uppercase no-underline"
      >
        All {week.rows.length} teams
        <svg
          aria-hidden="true"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </a>
    </Card>
  );
}
