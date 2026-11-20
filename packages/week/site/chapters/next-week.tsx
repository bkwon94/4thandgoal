/**
 * Next week: the blurb, then one card for each game of the next week with both teams and their records.
 * A Must Watch card shows its reason first and takes the brand edge. The players on bye show under their team.
 */
import { record } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import type { AvatarMap, ByePlayer, NextGame, Team } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { WeekChapter } from "../parts/week-chapter";
import { stableId, textId } from "@cpc/design/lib/stable-id";

/* The id of the card of one game, from the roster ids of its two teams, lower first, so a link can reach the game of
   one team. A game of next week takes its own prefix, so the same two teams in both chapters keep two ids. The module
   holds no client code, so a server loader can import it too. */
export function gameId(when: "last" | "next", a: number, b: number): string {
  return `${when === "next" ? "next-game" : "game"}-${Math.min(a, b)}-${Math.max(a, b)}`;
}

/* The players on bye of one side, key starters first, as the JSON lists them. The key starter's name is the one emphasis.
   The line wraps and never cuts, so a long list stays whole. */
function ByeLine({ byes }: { byes: ByePlayer[] }) {
  return (
    <div className="text-meta leading-body text-mute pl-[calc(var(--spacing-avatar)+var(--spacing-sp-3))]">
      <span className="tracking-caps font-mono uppercase">On bye</span>{" "}
      {byes.map((player, index) => (
        <span key={player.player_id}>
          {index > 0 && " · "}
          {player.key ? (
            <strong className="text-ink font-semibold">{player.name}</strong>
          ) : (
            <span>{player.name}</span>
          )}
          {` ${player.position}`}
        </span>
      ))}
    </div>
  );
}

/* One team of a card: the avatar, the name, and the record, then its players on bye. */
function Side({ team, avatars }: { team: Team; avatars: AvatarMap }) {
  return (
    <div className="gap-sp-1 flex flex-col">
      <div className="gap-sp-3 grid grid-cols-[auto_minmax(0,1fr)_auto] items-center">
        <Avatar src={avatarSrc(avatars, team.roster_id)} />
        <span className="text-body truncate leading-tight font-bold">{team.name}</span>
        <span className="text-meta text-ink-2 font-mono tabular-nums">
          {record(team.wins, team.losses)}
        </span>
      </div>
      {team.byes && team.byes.length > 0 && <ByeLine byes={team.byes} />}
    </div>
  );
}

function Game({ game, avatars }: { game: NextGame; avatars: AvatarMap }) {
  return (
    // The article carries the Must Watch state, so a test and a style hook read it without the class names.
    // The id lets the front door link to the next game of one team.
    <article
      id={gameId("next", game.a.roster_id, game.b.roster_id)}
      data-must-watch={game.must_watch}
      {...stableId("next-game", game.a.roster_id, game.b.roster_id)}
    >
      <Card edge={game.must_watch} className="gap-sp-3 flex h-full flex-col">
        {game.must_watch && (
          <div className="gap-sp-1 flex flex-col">
            <span className="text-meta tracking-caps text-accent-ink font-mono leading-tight font-bold uppercase">
              Must Watch
            </span>
            {game.reason && <span className="text-row leading-body text-ink-2">{game.reason}</span>}
          </div>
        )}
        <Side team={game.a} avatars={avatars} />
        <Side team={game.b} avatars={avatars} />
      </Card>
    </article>
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
    <WeekChapter
      id="next-week"
      title="Next week"
      note={`Week ${String(week + 1).padStart(2, "0")}`}
    >
      {blurb && (
        <p
          className="max-w-measure text-lead leading-body text-ink-2 m-0"
          {...textId("blurb", blurb)}
        >
          {blurb}
        </p>
      )}
      <div className="gap-sp-2 tablet:grid-cols-2 grid grid-cols-1">
        {games.map((game) => (
          <Game key={game.a.roster_id} game={game} avatars={avatars} />
        ))}
      </div>
    </WeekChapter>
  );
}
