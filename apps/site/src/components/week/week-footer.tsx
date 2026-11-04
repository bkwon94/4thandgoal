/**
 * The week footer: the last row of the weekly report, with a link to the prior week on the left and the next week on the right.
 * It is a server component. The page finds both weeks at build time, so a new week needs no code change.
 */
import { cn } from "@/lib/utils";
import type { WeekSummary } from "@/lib/week-types";
import { Chapter } from "@/components/parts/chapter";

/* A plain anchor in the home row style, like the week rows of the home page. An anchor skips the router, so the week href carries the base path.
   The touch height keeps a short row a comfortable target. */
function WeekLink({ week, rel }: { week: WeekSummary; rel: "prev" | "next" }) {
  return (
    <a
      href={week.href}
      rel={rel}
      className={cn(
        "press group block min-h-touch border-b border-rule pb-sp-3 text-inherit no-underline",
        rel === "next" && "text-right",
      )}
    >
      <b className="mb-sp-1 block text-lead leading-tight group-hover:text-accent-ink">Week {week.number}</b>
      <span className="block text-meta text-mute tabular-nums">{week.dates}</span>
    </a>
  );
}

/* Each side is a slot of a two-column list. A missing week leaves its slot empty, so the other link keeps its side.
   The chapter gives the footer the reveal and, from the tablet tier, the white card of the other chapters. */
export function WeekFooter({ prior, next }: { prior: WeekSummary | null; next: WeekSummary | null }) {
  return (
    <Chapter reveal>
      <nav aria-label="Weeks">
        <ul className="m-0 grid list-none grid-cols-2 gap-sp-4 p-0">
          <li>{prior && <WeekLink week={prior} rel="prev" />}</li>
          <li>{next && <WeekLink week={next} rel="next" />}</li>
        </ul>
      </nav>
    </Chapter>
  );
}
