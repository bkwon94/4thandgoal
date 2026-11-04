/**
 * The managers index: one card per team in standings order, with the avatar, the name, the owner, the record, and the grade letter.
 * A card is one link to the team's manager page. A phone stacks the cards; from the tablet tier up, two go per row.
 */
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { record } from "@cpc/design/format/format";
import type { Managers } from "@/lib/manager-types";
import { managerHrefFrom } from "@/lib/routes";
import type { AvatarMap } from "@/lib/week-types";

/* The page passes the managers index href, so the index holds no base path and no route format. */
export function ManagersIndex({ managers, avatars, managersHref }: { managers: Managers; avatars: AvatarMap; managersHref: string }) {
  return (
    <Chapter reveal id="managers">
      <Label heading>Managers</Label>
      {/* The grid gap takes the place of the card margin. minmax(0,1fr) lets a long team name wrap in its column. */}
      <ul className="m-0 flex list-none flex-col gap-sp-2 p-0 tablet:grid tablet:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        {managers.managers.map((manager) => (
          <li key={manager.roster_id}>
            {/* A plain anchor, as the menu links are: each manager page is a static page with no shared state. */}
            <a
              href={managerHrefFrom(managersHref, manager.roster_id)}
              className="press flex min-h-touch items-center gap-sp-3 rounded-card bg-card p-sp-3 text-inherit no-underline"
            >
              <Avatar src={avatarSrc(avatars, manager.roster_id)} />
              {/* The name is the one emphasis of the card. The owner sits under it in the quiet color. */}
              <span className="min-w-0 flex-1">
                <span className="block text-body leading-tight font-extrabold text-ink">{manager.team.name}</span>
                <span className="mt-sp-0 block text-meta text-mute">{manager.team.owner}</span>
              </span>
              <span className="flex-none font-semibold whitespace-nowrap text-mute tabular-nums">{record(manager.wins, manager.losses)}</span>
              {/* The grade letter is the one quiet number at the right end, after the record. A roster with no grade shows a dash. */}
              <span className="w-sp-6 flex-none text-center font-extrabold text-mute">{manager.grade ? manager.grade.letter : "—"}</span>
            </a>
          </li>
        ))}
      </ul>
    </Chapter>
  );
}
