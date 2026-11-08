/**
 * The managers index: the title, then the Index list, the ledger of the teams in power-ranking order with the chips of the playoff race.
 * A row opens in place with the grade letter, the grade read, the Grade dial, and a link to the team's manager page.
 */
import { avatarSrc } from "@cpc/league/images";
import { Rise } from "@cpc/design/parts/rise";
import { record } from "@cpc/design/format/format";
import type { Manager, Managers } from "../schema/manager-types";
import { managerHrefFrom } from "@cpc/league/hrefs";
import { type IndexRow, IndexList } from "./index-list";
import { raceGroup } from "./race-group";

/* The facts of the open row. A team with no rankings row or no odds drops that fact from the line. */
function factsOf(manager: Manager): string {
  return [
    record(manager.wins, manager.losses),
    manager.rank !== null ? `Power #${manager.rank}` : null,
    manager.odds ? `${manager.odds.playoff}% playoff` : null,
  ]
    .filter((fact): fact is string => fact !== null)
    .join(" · ");
}

/* The order of the power ranking of the page week. A team with no rankings row goes last, in standings order. */
function byPowerRank(a: Manager, b: Manager): number {
  return (a.rank ?? Infinity) - (b.rank ?? Infinity) || a.standing - b.standing;
}

/* The rows of the ledger. The place is the place in the ledger, so it equals the power rank when every team has one. */
export function indexRows(
  managers: Managers,
  avatars: Readonly<Record<string, string>>,
  managersHref: string,
): IndexRow[] {
  return [...managers.managers].sort(byPowerRank).map((manager, i) => ({
    id: manager.roster_id,
    place: i + 1,
    name: manager.team.name,
    avatar: avatarSrc(avatars, manager.roster_id),
    href: managerHrefFrom(managersHref, manager.roster_id),
    odds: manager.odds?.playoff ?? null,
    group: raceGroup(manager.odds),
    facts: factsOf(manager),
    grade: manager.grade,
  }));
}

/* The page passes the managers index href, so the index holds no base path and no route format. */
export function ManagersIndex({
  managers,
  avatars,
  managersHref,
}: {
  managers: Managers;
  avatars: Readonly<Record<string, string>>;
  managersHref: string;
}) {
  return (
    <div className="px-gutter py-sp-6 tablet:px-0">
      <Rise step={0}>
        <h1 className="m-0 text-headline leading-tight font-bold">Managers</h1>
        <div className="mt-sp-2 font-mono text-meta leading-tight font-bold tracking-wide text-mute uppercase">
          {`${managers.managers.length} teams · through week ${managers.through}`}
        </div>
      </Rise>
      <div className="mt-sp-4">
        <IndexList rows={indexRows(managers, avatars, managersHref)} teams={managers.managers.length} />
      </div>
    </div>
  );
}
