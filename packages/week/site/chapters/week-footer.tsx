/**
 * The week footer: the last row of the week page, with a card link to the prior week on the left and the next week on the right.
 * It is a server component. The page finds both weeks at build time, so a new week needs no code change.
 */
import { cn } from "@cpc/design/lib/utils";
import type { WeekSummary } from "../schema/week-types";

/* A plain anchor, so the week href carries the base path with scripts off. The whole card is the link, 44px or more tall. */
function WeekLink({ week, rel }: { week: WeekSummary; rel: "prev" | "next" }) {
  return (
    <a
      href={week.href}
      rel={rel}
      className={cn(
        "press flex min-h-touch flex-col gap-sp-1 rounded-card border border-rule bg-card p-sp-4 text-ink no-underline hover-fine:border-accent",
        rel === "next" && "items-end text-right",
      )}
    >
      <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">
        {rel === "prev" ? "Previous" : "Next"}
      </span>
      <b className="text-lead leading-tight">Week {week.number}</b>
      <span className="text-meta text-mute tabular-nums">{week.dates}</span>
    </a>
  );
}

/* Each side is a slot of a two-column list. A missing week leaves its slot empty, so the other link keeps its side. */
export function WeekFooter({ prior, next }: { prior: WeekSummary | null; next: WeekSummary | null }) {
  return (
    <nav aria-label="Weeks">
      <ul className="m-0 grid list-none grid-cols-2 gap-sp-2 p-0">
        <li>{prior && <WeekLink week={prior} rel="prev" />}</li>
        <li>{next && <WeekLink week={next} rel="next" />}</li>
      </ul>
    </nav>
  );
}
