/**
 * Every game: one card per game, by top score, with both avatars, both scores, and a share bar.
 * A tap opens the card in place: the best player of each side, both records, the recap, and one link to a manager page.
 */
"use client";

import { num, record, shortName } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { OpenCard } from "@cpc/design/parts/open-card";
import type { AvatarMap, Matchup, MatchupSide } from "../schema/week-types";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { managerHrefOrNull } from "@cpc/league/hrefs";
import { ShareBar, shareOf } from "../parts/share-bar";
import { WeekChapter } from "../parts/week-chapter";
import { openId, stableId, textId } from "@cpc/design/lib/stable-id";

/* One team of a card. The card is one button, so the name is plain text. A long name cuts at the end of its row. */
function TeamRow({ side, avatars, lead }: { side: MatchupSide; avatars: AvatarMap; lead: boolean }) {
  return (
    <span className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-sp-3">
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} />
      <span className={cn("truncate text-body leading-tight", lead ? "font-bold text-ink" : "text-ink-2")}>
        {side.team.name}
      </span>
      <span className={cn("font-mono text-body tabular-nums", lead ? "font-bold text-ink" : "text-mute")}>
        {num(side.score)}
      </span>
    </span>
  );
}

/* A chip of the best player of one side: the small avatar of its team, then "Best", the player, and the points. */
function BestChip({ side, avatars }: { side: MatchupSide; avatars: AvatarMap }) {
  if (side.top === null) return null;
  return (
    <>
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} size={CHIP_AVATAR} />
      {`Best ${shortName(side.top.name)} ${num(side.top.points)}`}
    </>
  );
}

/* The avatar of a chip, in pixels. It sits inside one line of meta text. */
const CHIP_AVATAR = 20;

/* The chips of an open game card: the best player of each side, then both records. A side with no top player has no chip. */
function chipsOf(matchup: Matchup, avatars: AvatarMap) {
  const [first, second] = matchup.sides;
  const best = [first, second]
    .filter((side) => side.top !== null)
    .map((side) => <BestChip key={side.team.roster_id} side={side} avatars={avatars} />);
  const records = `Records ${record(first.team.wins, first.team.losses)} · ${record(second.team.wins, second.team.losses)}`;
  return [...best, records];
}

/* One game on the Open card. The closed card is the scoreboard, and the open panel holds the chips, the recap, and one link. */
function GameCard({ matchup, avatars, managersHref }: { matchup: Matchup; avatars: AvatarMap; managersHref: string | null }) {
  // The JSON puts the winner first. A tie has no winner, and the first side still leads the card.
  const [first, second] = matchup.sides;
  const href = managerHrefOrNull(managersHref, first.team.roster_id);
  return (
    <OpenCard
      // The id names the game, so a check of the readability floor can open the recap of one game by its control.
      panelId={`recap-${matchup.id}`}
      // The egg hunt names the toggle, the panel, and the recap text by ids from the data.
      headMarks={openId("game", matchup.id)}
      panelMarks={stableId("recap", matchup.id)}
      textMarks={matchup.recap === null ? undefined : textId("blurb", matchup.recap)}
      head={
        <>
          <TeamRow side={first} avatars={avatars} lead />
          <ShareBar share={shareOf(first.score, second.score)} tone="page" />
          <TeamRow side={second} avatars={avatars} lead={false} />
        </>
      }
      chips={chipsOf(matchup, avatars)}
      text={matchup.recap}
      // One link per recap: the manager page of the team that leads the card.
      action={href === null ? null : { href, label: "Manager page", hiddenLabel: ` of ${first.team.name}` }}
    />
  );
}

/* The top score of a game: the score of its first side, the winner. */
const topScore = (matchup: Matchup) => Math.max(matchup.sides[0].score, matchup.sides[1].score);

/* The managers href is the managers index of the season. With null an open recap has no Manager page link. */
export function AllMatchups({
  matchups,
  avatars,
  managersHref = null,
}: {
  matchups: Matchup[];
  avatars: AvatarMap;
  managersHref?: string | null;
}) {
  const games = [...matchups].sort((a, b) => topScore(b) - topScore(a));
  return (
    <WeekChapter id="matchups" title="Every game" note="Tap for the recap">
      {/* Two cards per row from the tablet tier, so the twelve teams fit in less scroll. */}
      <ul className="m-0 grid grid-cols-1 gap-sp-2 p-0 tablet:grid-cols-2">
        {games.map((matchup) => (
          <GameCard key={matchup.id} matchup={matchup} avatars={avatars} managersHref={managersHref} />
        ))}
      </ul>
    </WeekChapter>
  );
}
