/**
 * Next week: one grey card per game with both teams and their records, the Must Watch tag, and the blurb.
 * The week number comes from the page, so the label reads the week after the one on the page.
 * A phone stacks the cards; from the tablet tier up, two go per row, so a card has room for a bye subtitle.
 */
import { record } from "@/lib/format/format";
import { cn } from "@/lib/utils";
import type { AvatarMap, ByePlayer, NextGame, Team } from "@/lib/week-types";
import { avatarSrc } from "@cpc/league/avatar";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { Tag } from "@/components/parts/tag";
import { Who } from "@/components/parts/who";

/* The "vs" line and the bye subtitle share one indent, so both line up under the team names, past the avatar column. */
const PAST_AVATAR = "pl-[calc(var(--spacing-avatar)+var(--spacing-sp-2))]";

/* The players on bye next week, as a subtitle in secondary text under the team row, key starters first.
   It uses no tag and no red, so the Must Watch tag stays the one red signal in the card.
   The key starter's name in ink is the one emphasis; every other word stays mute and normal weight.
   It sets normal weight, because the game div around it is extra bold. The line wraps and never truncates, so a long list stays whole. */
function ByeLine({ byes }: { byes: ByePlayer[] }) {
  return (
    <div className={cn("mt-sp-0 text-label leading-snug font-normal text-mute", PAST_AVATAR)}>
      <span className="mr-sp-1 text-label font-semibold tracking-caps uppercase text-mute">On bye</span>
      {byes.map((player, i) => (
        <span key={player.player_id}>
          {i > 0 && " · "}
          {player.key ? <strong className="font-semibold text-ink">{player.name}</strong> : <span>{player.name}</span>}
          {` ${player.position}`}
        </span>
      ))}
    </div>
  );
}

/* One team per row. The name takes the free width and the record stays whole on the right,
   so a long name never pushes a record or the other team onto a new line. */
function Side({ team, avatars }: { team: Team; avatars: AvatarMap }) {
  return (
    <>
      <div className="flex min-w-0 items-center gap-sp-2">
        <Who src={avatarSrc(avatars, team.roster_id)} name={team.name} fill />
        <span className="flex-none font-semibold whitespace-nowrap text-mute tabular-nums">{record(team.wins, team.losses)}</span>
      </div>
      {team.byes && team.byes.length > 0 && <ByeLine byes={team.byes} />}
    </>
  );
}

function Game({ game, avatars, first }: { game: NextGame; avatars: AvatarMap; first: boolean }) {
  return (
    <div className={cn("rounded-card bg-card p-sp-3", !first && "mt-sp-2 tablet:mt-0")}>
      {/* The Must Watch tag sits at the top of the card as an eyebrow, so a reader sees it before the teams. */}
      {game.must_watch && <Tag className="ml-0 mb-sp-2">Must Watch</Tag>}
      <div className="text-body leading-body font-extrabold">
        <Side team={game.a} avatars={avatars} />
        {/* The "vs" lines up under the names, past the avatar column. */}
        <div className={cn("my-sp-2 text-meta leading-none font-semibold text-mute", PAST_AVATAR)}>
          vs
        </div>
        <Side team={game.b} avatars={avatars} />
      </div>
      {game.must_watch && game.reason && <div className="mt-sp-3 text-meta text-mute">{game.reason}</div>}
    </div>
  );
}

export function NextWeek({
  week,
  games,
  avatars,
  blurb,
}: {
  week: number;
  games: NextGame[];
  avatars: AvatarMap;
  blurb?: string;
}) {
  return (
    <Chapter reveal id="next-week">
      <Label heading>{`Next Week · Week ${week + 1}`}</Label>
      {/* The grid gap takes the place of the card margin. minmax(0,1fr) lets a long team name truncate in its column.
          A lone last card keeps its column width. The grid stays at two columns from the tablet tier up, so a card has room for a bye subtitle. */}
      <div className="tablet:grid tablet:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] tablet:gap-sp-2">
        {games.map((game, i) => (
          <Game key={game.a.roster_id} game={game} avatars={avatars} first={i === 0} />
        ))}
      </div>
      {blurb && <Blurb className="mt-sp-3">{blurb}</Blurb>}
    </Chapter>
  );
}
