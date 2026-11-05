/**
 * The managers index: one card per team in standings order, with the avatar, the name, the record, the power rank,
 * the playoff odds, the grade letter in a box, and the grade text. The whole card is one link to the team's manager page.
 */
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import { Rise } from "@cpc/design/parts/rise";
import { record } from "@cpc/design/format/format";
import type { Manager, Managers } from "../schema/manager-types";
import { managerHrefFrom } from "@cpc/league/hrefs";

/* The facts of the line under the name. A team with no rankings row or no odds drops that fact from the line. */
function factsOf(manager: Manager): string[] {
  return [
    record(manager.wins, manager.losses),
    manager.rank !== null ? `Power #${manager.rank}` : null,
    manager.odds ? `${manager.odds.playoff}% playoff` : null,
  ].filter((fact): fact is string => fact !== null);
}

/* The grade letter in its box. The box has its own edge, so the letter reads as the one key number of the card.
   A roster with no grade shows a dash in the box. The label names the box, so a screen reader hears "Grade B". */
function GradeBox({ letter }: { letter: string | null }) {
  return (
    <span
      aria-label={letter === null ? "No grade" : `Grade ${letter}`}
      className="flex size-touch flex-none items-center justify-center rounded-tile border border-accent font-mono text-stat leading-none font-bold text-ink"
    >
      {letter ?? "—"}
    </span>
  );
}

/* One card. The anchor fills the card, so a tap anywhere on the card opens the manager page. */
function ManagerCard({ manager, href, avatar }: { manager: Manager; href: string; avatar: string }) {
  const { grade } = manager;
  return (
    // A plain anchor, as the menu links are: each manager page is a static page with no shared state.
    <a
      href={href}
      className="press flex h-full min-h-touch flex-col gap-sp-3 rounded-card border border-rule bg-card p-sp-4 text-ink no-underline hover:border-accent"
    >
      <span className="flex items-center gap-sp-3">
        <Avatar src={avatar} />
        {/* minmax and min-w-0 let a long team name wrap, so the name never cuts off. */}
        <span className="min-w-0 flex-1">
          <span className="block text-lead leading-tight font-bold break-words text-ink">{manager.team.name}</span>
          <span className="mt-sp-1 flex flex-wrap gap-x-sp-2 font-mono text-meta leading-tight text-ink-2 tabular-nums">
            {factsOf(manager).map((fact, i) => (
              <span key={fact}>
                {/* The dot sets the facts apart. A wrapped line starts with a fact, not a dot. */}
                {i > 0 && <span aria-hidden="true">{"· "}</span>}
                {fact}
              </span>
            ))}
          </span>
        </span>
        <GradeBox letter={grade ? grade.letter : null} />
      </span>
      {/* The grade text says what the letter means, such as "Deep at TE. Thin at WR." */}
      {grade && <span className="block text-meta leading-body text-ink-2">{grade.read}</span>}
    </a>
  );
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
      {/* A phone stacks the cards. From the tablet tier up, two go per row. minmax(0,1fr) lets a long name wrap in its column. */}
      <ul className="m-0 mt-sp-5 flex list-none flex-col gap-sp-3 p-0 tablet:grid tablet:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        {managers.managers.map((manager, i) => (
          <li key={manager.roster_id}>
            <Rise step={i + 1} className="h-full">
              <ManagerCard
                manager={manager}
                href={managerHrefFrom(managersHref, manager.roster_id)}
                avatar={avatarSrc(avatars, manager.roster_id)}
              />
            </Rise>
          </li>
        ))}
      </ul>
    </div>
  );
}
