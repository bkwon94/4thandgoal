/**
 * The Site answer of the Thread: the launcher of the Tools and the pages to read, the page card of one page with its "Open"
 * button and the "All pages" fold, or the none case. The kept item holds only the page key, so the links come from the pages.
 */
"use client";

import { motion } from "framer-motion";
import { forwardRef, useId } from "react";
import { ArrowLeftRightIcon, ArrowRightIcon, ArrowUpRightIcon, BookOpenIcon, ChevronDownIcon, ChevronRightIcon, DicesIcon, ListOrderedIcon, type LucideIcon, NewspaperIcon, UsersIcon } from "lucide-react";
import { Collapsible, CollapsiblePanel, CollapsibleTrigger } from "@cpc/design/ui/collapsible";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import type { SitePage } from "@/app/site-pages";
import { ALL_PAGES, type SiteAnswerPage } from "./ask-api";
import { QuestionBubble, Surface } from "./miss-card";
import { FAST, QUICK, fadeIn, staggerOf } from "./motion";

/* The lead line of the page card of `label`. */
export const cardLead = (label: string) => `The ${label} has its own page.`;
/* The lead line of the none case: a page that the client lacks. */
export const NONE_LEAD = "The site has no page for that. Here is what it has.";

/* The pages of the site in two groups, each in the order of `pages`: the Tools, and the pages to read. */
type PageGroups = { tools: SitePage[]; reads: SitePage[] };

function groupsOf(pages: SitePage[]): PageGroups {
  return { tools: pages.filter((page) => page.tool), reads: pages.filter((page) => !page.tool) };
}

/* The lead line of the whole site: the count of the Tools and of the pages to read. */
function listLead({ tools, reads }: PageGroups): string {
  return `The site has ${tools.length} ${tools.length === 1 ? "tool" : "tools"} and ${reads.length} ${reads.length === 1 ? "page" : "pages"} to read.`;
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

/* The Tool tone (decision 02 of site-answer): a soft tint of the accent in both themes, with the icon and the label in the accent
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

/* A Tool tile of the launcher: a pale tint of the card in light, and the raised surface with a rule in dark, so no fill
   is solid. Its hover deepens to the hover tint of the "Open" button, on --duration-quick with ease-out. */
const TOOL_TILE =
  "border border-transparent bg-[color-mix(in_srgb,var(--color-accent)_10%,var(--color-card))] text-ink transition-[background-color,transform] duration-150 ease-out hover-fine:bg-[color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))] dark:border-rule dark:bg-raised dark:hover-fine:bg-[color-mix(in_srgb,var(--color-accent)_34%,var(--color-raised))]";
/* A tile of a page to read keeps the plain card surface of the Thread. */
const READ_TILE = "door-sheen border border-door-hair bg-card text-ink transition-[background-color,transform] duration-150 ease-out hover-fine:bg-raised";

/* The props of a tile that pops in from --scale-large with a fade, on --duration-fast, one --duration-stagger after the
   tile before it. The tiles start after the lead line. With motion off, only the fade stays. */
function tileIn(off: boolean, index: number) {
  const transition = fadeIn(FAST, QUICK / 2 + staggerOf(index));
  return off
    ? { initial: { opacity: 0 }, animate: { opacity: 1 }, transition }
    : { initial: { opacity: 0, scale: 0.96 }, animate: { opacity: 1, scale: 1 }, transition, style: { transformOrigin: "top left" } };
}

/* One tile of the launcher: the icon box, the arrow mark in its corner, the label, and the blurb. The whole tile is the
   link. The pop-in sits on the item, so the press of the link keeps its own transform. */
function PageTile({ page, index }: { page: SitePage; index: number }) {
  const off = useMotionOff();
  return (
    <motion.li {...tileIn(off, index)} className="flex">
      <a
        href={page.href}
        className={`press group flex w-full flex-col justify-between gap-sp-3 rounded-card p-sp-4 no-underline ${page.tool ? `min-h-[156px] ${TOOL_TILE}` : `min-h-[132px] ${READ_TILE}`}`}
      >
        <span className="flex items-start justify-between">
          <span className={`grid size-10 place-items-center rounded-full ${page.tool ? TOOL_TINT : READ_ICON_BOX}`}>
            <PageIcon page={page} className="size-sp-5" />
          </span>
          <ArrowUpRightIcon
            aria-hidden
            className="size-sp-4 text-mute transition-transform duration-150 ease-out group-hover:translate-x-sp-0 group-hover:-translate-y-sp-0 motion-reduce:transition-none motion-reduce:group-hover:translate-x-0 motion-reduce:group-hover:translate-y-0"
          />
        </span>
        <span className="flex flex-col gap-sp-1">
          <span className={`leading-tight font-bold ${page.tool ? "text-lead" : "text-body"}`}>{page.label}</span>
          <span className="text-meta leading-body text-ink-2">{page.blurb}</span>
        </span>
      </a>
    </motion.li>
  );
}

/* One group of the launcher under its small label: the Tools in 2 columns, or the pages to read in 2, and 3 from 640 px.
   `from` is the index of its first tile, so the stagger runs on across both groups. */
function TileGroup({ label, pages, from, wide }: { label: string; pages: SitePage[]; from: number; wide: boolean }) {
  const id = useId();
  if (pages.length === 0) return null;
  return (
    <div className="flex flex-col gap-sp-2">
      <span id={id} className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">
        {label}
      </span>
      <ul aria-labelledby={id} className={`m-0 grid list-none grid-cols-2 gap-sp-2 p-0 ${wide ? "tablet:grid-cols-3" : ""}`}>
        {pages.map((page, index) => (
          <PageTile key={page.key} page={page} index={from + index} />
        ))}
      </ul>
    </div>
  );
}

/* The list view of the whole site, a launcher of tiles (decision 02 of site-answer): the lead line on the Thread, then
   the Tools and the pages to read as tiles. */
function Launcher({ pages }: { pages: SitePage[] }) {
  const groups = groupsOf(pages);
  const { tools, reads } = groups;
  return (
    <div className="flex flex-col gap-sp-4">
      <motion.p className="m-0 text-body leading-body font-semibold text-ink" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={fadeIn(FAST)}>
        {listLead(groups)}
      </motion.p>
      <TileGroup label="Tools" pages={tools} from={0} wide={false} />
      <TileGroup label="Pages to read" pages={reads} from={tools.length} wide />
    </div>
  );
}

/* The page card of one page, in the normal Answer card (decision 02 of site-answer): the lead line, the icon box and
   the name, the blurb, one "Open" button, and the other pages in the "All pages" fold. */
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

/* The Site answer of `question`. ALL_PAGES gives the list view. A page key of `pages` gives its page card. MISSING_PAGE,
   or a kept key that the client no longer has, gives the none case: the page card with no page, and the rows of all the
   pages, open. */
export const SiteAnswer = forwardRef<HTMLElement, { question: string; page: SiteAnswerPage; pages: SitePage[] }>(function SiteAnswer({ question, page, pages }, ref) {
  const target = pages.find((candidate) => candidate.key === page);
  return (
    <article ref={ref} aria-label={question} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={question} />
      {page === ALL_PAGES ? (
        <Launcher pages={pages} />
      ) : (
        <Surface>
          {target ? (
            <PageCard page={target} others={pages.filter((other) => other !== target)} />
          ) : (
            <>
              <p className="m-0 text-body leading-tight font-semibold text-ink">{NONE_LEAD}</p>
              <PageRows pages={pages} />
            </>
          )}
        </Surface>
      )}
    </article>
  );
});
