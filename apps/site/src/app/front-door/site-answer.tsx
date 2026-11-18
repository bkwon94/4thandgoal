/**
 * The Site answer of the Thread: the page card of one page, with its "Open" button and the "All pages" fold, or the rows
 * of all the pages for a page that the client lacks. The kept item holds only the page key, so the links come from the pages.
 */
"use client";

import { motion } from "framer-motion";
import { forwardRef } from "react";
import { ArrowLeftRightIcon, ArrowRightIcon, BookOpenIcon, ChevronDownIcon, ChevronRightIcon, DicesIcon, ListOrderedIcon, type LucideIcon, NewspaperIcon, UsersIcon } from "lucide-react";
import { Collapsible, CollapsiblePanel, CollapsibleTrigger } from "@cpc/design/ui/collapsible";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { SitePage } from "@/app/site-pages";
import { QuestionBubble, Surface } from "./miss-card";
import { FAST, fadeIn, staggerOf } from "./motion";

/* The lead line of the page card of `label`. */
export const cardLead = (label: string) => `The ${label} has its own page.`;
/* The lead line of the none case: a page that the client lacks. */
export const NONE_LEAD = "The site has no page for that. Here is what it has.";

/* The lead line of the whole site: the count of the Tools and of the pages to read. */
export function listLead(pages: SitePage[]): string {
  const tools = pages.filter((page) => page.tool).length;
  const reads = pages.length - tools;
  return `The site has ${tools} ${tools === 1 ? "tool" : "tools"} and ${reads} ${reads === 1 ? "page" : "pages"} to read.`;
}

/* The mark of each page in its icon box. A page with no mark of its own takes the book. */
const ICONS: Record<string, LucideIcon> = {
  week: NewspaperIcon,
  rankings: ListOrderedIcon,
  managers: UsersIcon,
  analyzer: ArrowLeftRightIcon,
  midseason: BookOpenIcon,
  sim: DicesIcon,
};

function PageIcon({ page, className }: { page: SitePage; className: string }) {
  const Icon = ICONS[page.key] ?? BookOpenIcon;
  return <Icon aria-hidden className={className} strokeWidth={2} />;
}

/* The Tool tone of decision 02: a soft tint of the accent in both themes, with the icon and the label in the accent
   ink, so red marks only a Tool and no fill is solid. A light tint of the card in light, of the raised surface in dark. */
const TOOL_TINT = "bg-[color-mix(in_srgb,var(--color-accent)_20%,var(--color-card))] text-accent-ink dark:bg-[color-mix(in_srgb,var(--color-accent)_24%,var(--color-raised))]";
/* The icon box of a page to read keeps the plain raised surface. */
const READ_ICON_BOX = "bg-raised text-ink-2";
/* The "Open" button of a Tool deepens its tint on hover, on --duration-quick with ease-out. The press utility scales it. */
const TOOL_BUTTON = `${TOOL_TINT} transition-[background-color,transform] duration-150 ease-out hover-fine:bg-[color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))] dark:hover-fine:bg-[color-mix(in_srgb,var(--color-accent)_34%,var(--color-raised))]`;
/* The "Open" button of a page to read keeps the plain surface, so red marks only a Tool. */
const READ_BUTTON = "border border-rule bg-page text-ink transition-[background-color,transform] duration-150 ease-out hover-fine:bg-raised";

/* The props of a row that rises in from --distance-base with a --blur-small, one --duration-stagger after the row above.
   With motion off, only the fade stays. */
function rowIn(off: boolean, index: number) {
  const transition = fadeIn(FAST, staggerOf(index));
  return off
    ? { initial: { opacity: 0 }, animate: { opacity: 1 }, transition }
    : { initial: { opacity: 0, y: 8, filter: "blur(2px)" }, animate: { opacity: 1, y: 0, filter: "blur(0px)" }, transition };
}

/* One row of a page: its icon box, its label, and its blurb. The whole row is the link, at least 52 px tall. */
function PageRow({ page, index }: { page: SitePage; index: number }) {
  const off = useMotionOff();
  return (
    <motion.li {...rowIn(off, index)} className="border-b border-rule last:border-b-0">
      <a
        href={page.href}
        className="group -mx-sp-2 grid min-h-row-touch grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-sp-3 rounded-tile px-sp-2 py-sp-2 text-ink no-underline transition-colors duration-150 ease-out hover-fine:bg-raised"
      >
        <span className={`grid size-9 place-items-center rounded-[10px] ${page.tool ? TOOL_TINT : READ_ICON_BOX}`}>
          <PageIcon page={page} className="size-[18px]" />
        </span>
        <span className="flex min-w-0 flex-col gap-sp-0">
          <span className="text-body leading-tight font-semibold">{page.label}</span>
          <span className="text-meta leading-body text-mute">{page.blurb}</span>
        </span>
        <ChevronRightIcon aria-hidden className="size-sp-4 text-mute transition-transform duration-150 ease-out group-hover:translate-x-sp-0 motion-reduce:transition-none motion-reduce:group-hover:translate-x-0" />
      </a>
    </motion.li>
  );
}

/* The rows of `pages`, in their order. */
export function PageRows({ pages }: { pages: SitePage[] }) {
  return (
    <ul aria-label="Pages" className="m-0 flex list-none flex-col p-0">
      {pages.map((page, index) => (
        <PageRow key={page.key} page={page} index={index} />
      ))}
    </ul>
  );
}

/* The B card of one page: the lead line, the icon box and the name, the blurb, one "Open" button, and the other pages in
   the "All pages" fold. */
function PageCard({ page, others }: { page: SitePage; others: SitePage[] }) {
  return (
    <>
      <p className="m-0 text-body leading-tight font-semibold text-ink">{cardLead(page.label)}</p>
      <div className="flex flex-col gap-sp-3">
        <span className="flex items-center gap-sp-3">
          <span className={`grid size-12 flex-none place-items-center rounded-tile ${page.tool ? TOOL_TINT : READ_ICON_BOX}`}>
            <PageIcon page={page} className="size-sp-6" />
          </span>
          <span className="min-w-0 text-stat leading-tight font-bold tracking-tight text-ink">{page.label}</span>
        </span>
        <p className="m-0 text-body leading-body text-ink-2">{page.blurb}</p>
        <a
          href={page.href}
          className={`press flex min-h-touch items-center justify-center gap-sp-2 rounded-pill px-sp-4 text-body leading-tight font-semibold no-underline ${page.tool ? TOOL_BUTTON : READ_BUTTON}`}
        >
          Open the {page.label}
          <ArrowRightIcon aria-hidden className="size-sp-4" strokeWidth={2.25} />
        </a>
      </div>
      {others.length > 0 && (
        <Collapsible className="flex flex-col border-t border-rule pt-sp-1">
          <CollapsibleTrigger className="group -mx-sp-2 flex min-h-touch items-center justify-between rounded-tile px-sp-2 text-body leading-tight font-semibold text-ink-2 transition-colors duration-150 ease-out hover-fine:bg-raised">
            All pages · {others.length}
            {/* The chevron flips on the Y axis, which works in every browser, on the same 250 ms as the panel. */}
            <ChevronDownIcon aria-hidden className="size-sp-4 transition-transform duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] group-data-open:-scale-y-100 motion-reduce:transition-none" />
          </CollapsibleTrigger>
          <CollapsiblePanel>
            <div className="pt-sp-2">
              <PageRows pages={others} />
            </div>
          </CollapsiblePanel>
        </Collapsible>
      )}
    </>
  );
}

/* The Site answer of `question`. A page key of `pages` gives its page card. `all` gives the rows of every page under the
   count of the site. `missing`, or a kept key that the client no longer has, gives the none case. */
export const SiteAnswer = forwardRef<HTMLElement, { question: string; page: string; pages: SitePage[] }>(function SiteAnswer({ question, page, pages }, ref) {
  const target = pages.find((candidate) => candidate.key === page);
  return (
    <article ref={ref} aria-label={question} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={question} />
      <Surface>
        {target ? (
          <PageCard page={target} others={pages.filter((other) => other !== target)} />
        ) : (
          <>
            <p className="m-0 text-body leading-tight font-semibold text-ink">{page === "all" ? listLead(pages) : NONE_LEAD}</p>
            <PageRows pages={pages} />
          </>
        )}
      </Surface>
    </article>
  );
});
