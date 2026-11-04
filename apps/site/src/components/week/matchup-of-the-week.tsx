/**
 * The matchup of the week: the label with the reason tag, the score row with both teams, and the blurb.
 * It ports the #motw chapter of the Jinja week page.
 */
import { num } from "@/lib/format/format";
import { cn } from "@/lib/utils";
import type { AvatarMap, MatchupSide, Pick } from "@/lib/week-types";
import { Avatar } from "@/components/parts/avatar";
import { avatarSrc } from "@/lib/avatar";
import { Blurb } from "@/components/parts/blurb";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { Tag } from "@/components/parts/tag";

/* A flex item cannot shrink below its longest word by default, so min-w-0 and hyphens keep a long team name inside a phone.
   From the tablet tier the cell fills its grid column, so each team sits at its edge of the row. */
function TeamCell({ side, avatars, right }: { side: MatchupSide; avatars: AvatarMap; right?: boolean }) {
  return (
    <div
      className={cn(
        "flex w-[36%] min-w-0 tablet:w-auto items-center gap-sp-2 text-lead leading-tight font-extrabold hyphens-auto",
        right && "flex-row-reverse text-right",
      )}
    >
      <Avatar src={avatarSrc(avatars, side.team.roster_id)} />
      <span className="min-w-0">{side.team.name}</span>
    </div>
  );
}

function Points({ side }: { side: MatchupSide }) {
  return (
    <span className={cn("text-score leading-stat font-black whitespace-nowrap tabular-nums", side.loser && "text-accent-ink")}>
      {num(side.score)}
    </span>
  );
}

export function MatchupOfTheWeek({ pick, avatars, blurb }: { pick: Pick; avatars: AvatarMap; blurb: string }) {
  const [first, second] = pick.sides;
  return (
    <Chapter id="motw">
      <Label heading>
        Matchup of the Week <Tag>{pick.reason}</Tag>
      </Label>
      {/* From the tablet tier two equal outer columns hold the teams, so the score sits in the exact center of the row. */}
      <div className="mb-sp-3 flex items-center justify-between gap-sp-2 tablet:grid tablet:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] tablet:gap-sp-4">
        <TeamCell side={first} avatars={avatars} />
        {/* Flex centers the small dash on the big numbers. Inline text would sit it on the baseline. */}
        <div className="flex items-center gap-sp-1 whitespace-nowrap">
          <Points side={first} />
          <span className="text-meta text-mute">–</span>
          <Points side={second} />
        </div>
        <TeamCell side={second} avatars={avatars} right />
      </div>
      <Blurb>{blurb}</Blurb>
    </Chapter>
  );
}
