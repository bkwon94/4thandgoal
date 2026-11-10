/**
 * The Answers of the trade Topics in the Thread: the plain steps while the trade judge works, then the trade check with
 * its Lean, Case, and top Bullets, the trade ideas with each offer, or the Trade page for a trade with an unsure player.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { forwardRef, useId, useState, type ReactNode } from "react";
import { ArrowRightIcon, CheckIcon } from "lucide-react";
import { BulletRows } from "@cpc/analyzer/form/bullet-rows";
import type { AnalyzeResponse, FindResponse, FinderTrade, Lean } from "@cpc/analyzer/lib/analyze-types";
import { prefillQuery, type Prefill } from "@cpc/analyzer/lib/prefill";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { FAST, QUICK, SLOW, STAGGER, VERY_SLOW, fadeIn, riseIn } from "./motion";
import { QuestionBubble } from "./miss-card";
import type { TradeAnswer, TradeForm } from "./trade-api";

/* The Bullets that the check shows of Your side, and of each offer. The Trade page holds each one. */
export const TOP_BULLETS = 3;
export const TOP_OFFER_BULLETS = 2;

/* The line before the first step, by Topic, so the card never sits empty while the first stage runs. */
const FIRST_LINE = { check: "Reading your trade…", ideas: "Looking for trades…" } as const;

/* The five Leans from the no end to the yes end, as on the Trade page, so the lit step shows how strong the call is. */
const SCALE: readonly Lean[] = ["Pass", "Lean no", "Gut call", "Lean yes", "Send it"];
/* A yes leans in the accent and a no in the plain ink, as on the Trade page. */
const LEAN_COLOR: Record<Lean, string> = {
  "Send it": "text-accent-ink",
  "Lean yes": "text-accent-ink",
  "Gut call": "text-ink-2",
  "Lean no": "text-ink",
  Pass: "text-ink",
};

/* The Trade page with the trade of `prefill` in its form. */
const tradeHref = (base: string, prefill: Prefill) => `${base}${prefillQuery(prefill)}`;

/* The line in flight, with the shimmer of transitions-dev: a band of the ink sweeps the mute text on a linear 2 s loop.
   With motion off, it holds still in the mute ink. */
function Shimmer({ children }: { children: string }) {
  const off = useMotionOff();
  if (off) return <span className="text-mute">{children}</span>;
  return (
    <motion.span
      className="bg-clip-text text-transparent [background-image:linear-gradient(90deg,var(--color-mute)_0%,var(--color-mute)_40%,var(--color-ink)_50%,var(--color-mute)_60%,var(--color-mute)_100%)] [background-size:400%_100%]"
      initial={{ backgroundPosition: "100% 0%" }}
      animate={{ backgroundPosition: "0% 0%" }}
      transition={{ duration: 2, ease: "linear", repeat: Infinity }}
    >
      {children}
    </motion.span>
  );
}

/* The steps while the trade judge works. Each step rises in from a blur as it lands. A done step takes a check in the
   mute ink, and the newest step shimmers, so the list reads as work that moves (decision 06). */
function Steps({ mode, steps }: { mode: "check" | "ideas"; steps: string[] }) {
  const off = useMotionOff();
  const lines = steps.length > 0 ? steps : [FIRST_LINE[mode]];
  return (
    <ol role="status" aria-label="Steps" className="m-0 flex list-none flex-col gap-sp-2 px-sp-1 py-sp-1">
      {lines.map((line, index) => {
        const current = index === lines.length - 1;
        return (
          <motion.li key={`${index}-${line}`} className="flex items-center gap-sp-2 text-body leading-tight font-semibold" {...riseIn(off, { text: true })}>
            <span aria-hidden className="flex size-sp-4 flex-none items-center justify-center">
              {current ? (
                <span className="size-sp-1 rounded-full bg-ink" />
              ) : (
                <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={fadeIn(QUICK)}>
                  <CheckIcon className="size-sp-4 text-mute" strokeWidth={2.5} />
                </motion.span>
              )}
            </span>
            {current ? <Shimmer>{line}</Shimmer> : <span className="text-mute">{line}</span>}
          </motion.li>
        );
      })}
    </ol>
  );
}

/* The card of a whole Answer. It settles from a soft blur at 0.98, as the data block of a league Answer does
   (decision 07). With motion off, it only fades in. */
function Settle({ children, label }: { children: ReactNode; label: string }) {
  const off = useMotionOff();
  return (
    <motion.section
      aria-label={label}
      className="door-sheen flex flex-col gap-sp-4 rounded-card border border-door-hair bg-card p-sp-4"
      initial={off ? { opacity: 0 } : { opacity: 0, scale: 0.98, filter: "blur(6px)" }}
      animate={off ? { opacity: 1 } : { opacity: 1, scale: 1, filter: "blur(0px)" }}
      transition={fadeIn(SLOW, 0.04)}
    >
      {children}
    </motion.section>
  );
}

function Caps({ children }: { children: ReactNode }) {
  return <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{children}</span>;
}

/* The link to the Trade page, as "Read the full report" of a league Answer. */
function PageLink({ href, label, delay = 0.3 }: { href: string; label: string; delay?: number }) {
  return (
    <motion.a
      href={href}
      className="press group -mx-sp-2 flex min-h-touch items-center gap-sp-2 self-start rounded-pill px-sp-2 text-body leading-tight font-semibold text-accent-ink no-underline"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={fadeIn(VERY_SLOW, delay)}
    >
      <span>{label}</span>
      <ArrowRightIcon aria-hidden className="size-sp-4 transition-transform duration-150 ease-out group-hover:translate-x-sp-0 motion-reduce:transition-none" strokeWidth={2.25} />
    </motion.a>
  );
}

/* The players that one side gives, as one plain line. */
const names = (players: { name: string }[]) => players.map((player) => player.name).join(", ");

/* The fairness line in the words of decision 08. A lopsided trade helps the side that does not give more. */
export function fairnessLine(doc: AnalyzeResponse): string {
  const fairness = doc.fairness;
  if (!fairness || fairness.state === "fair") return "A fair trade for both teams.";
  const helped = doc.trade.sides.filter((side) => side.roster_id !== fairness.gives_more);
  // A trade of three or four teams helps more than one side, so its line names the side that gives more.
  if (helped.length === 1) return `It helps ${helped[0].team} more.`;
  return `${doc.trade.sides.find((side) => side.roster_id === fairness.gives_more)?.team} gives more.`;
}

/* The Lean word over its 5-step scale. The lit step carries aria-current, so a screen reader hears the step. */
function LeanBlock({ lean }: { lean: Lean }) {
  const off = useMotionOff();
  return (
    <div className="flex flex-col gap-sp-2">
      <Caps>The read</Caps>
      <motion.p className={`m-0 text-score leading-tight font-bold tracking-tight ${LEAN_COLOR[lean]}`} {...riseIn(off, { text: true, delay: 0.1 })}>
        {lean}
      </motion.p>
      <ol aria-label="The Lean scale" className="m-0 grid list-none grid-cols-5 gap-x-sp-1 p-0">
        {SCALE.map((step, index) => {
          const lit = step === lean;
          return (
            <li key={step} aria-current={lit ? "step" : undefined} className="flex flex-col gap-sp-1">
              <motion.span
                aria-hidden
                className={`block h-sp-1 origin-left rounded-pill ${lit ? "bg-accent" : "bg-rule"}`}
                initial={off ? { opacity: 0 } : { opacity: 0, scaleX: 0.6 }}
                animate={off ? { opacity: 1 } : { opacity: 1, scaleX: 1 }}
                transition={fadeIn(FAST, 0.15 + index * STAGGER)}
              />
              <span className={`text-center text-label leading-tight font-bold tracking-caps uppercase ${lit ? "text-ink" : "text-mute"}`}>{step}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

/* The Case, clamped to 4 lines on a phone so the top Bullets stay in view, with a button that opens the rest. From
   the tablet tier it shows in full, as on the Trade page. */
function CaseText({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className="flex flex-col items-start gap-sp-1">
      <p id={id} className={`m-0 text-body leading-body text-ink-2 ${open ? "" : "max-tablet:line-clamp-4"}`}>
        {text}
      </p>
      {!open && (
        <button
          type="button"
          aria-expanded={false}
          aria-controls={id}
          onClick={() => setOpen(true)}
          className="press -mx-sp-2 min-h-touch rounded-pill px-sp-2 text-meta font-semibold text-accent-ink underline underline-offset-4 tablet:hidden"
        >
          Read the full case
        </button>
      )}
    </div>
  );
}

/* The trade check: the trade, the Lean, the Case, the fairness line, the top Bullets of Your side, and the Trade page. */
function CheckBody({ doc, analyze }: { doc: AnalyzeResponse; analyze: string }) {
  const off = useMotionOff();
  const mine = doc.trade.sides.find((side) => side.roster_id === doc.trade.asker) ?? doc.trade.sides[0];
  const partner = doc.trade.sides.find((side) => side.roster_id !== mine.roster_id);
  const bullets = doc.sides.find((side) => side.roster_id === mine.roster_id)?.bullets ?? [];
  const prefill: Prefill = {
    team: mine.roster_id,
    partner: partner?.roster_id ?? null,
    gives: mine.gives.map((player) => player.player_id),
    gets: mine.gets.map((player) => player.player_id),
  };
  return (
    <Settle label="Trade check">
      <p className="m-0 text-body leading-tight text-ink-2">
        You give <span className="font-semibold text-ink">{names(mine.gives)}</span> and get{" "}
        <span className="font-semibold text-ink">{names(mine.gets)}</span>
        {partner ? ` from ${partner.team}` : ""}.
      </p>
      <LeanBlock lean={doc.lean} />
      <motion.div className="flex flex-col gap-sp-2" {...riseIn(off, { text: true, delay: 0.2 })}>
        <CaseText text={doc.case} />
        <p className="m-0 text-body leading-tight font-semibold text-ink">{fairnessLine(doc)}</p>
      </motion.div>
      {bullets.length > 0 && (
        // The bands of the rows say For and Against, and each Bullet speaks to Your team, so no label sits over them.
        <motion.div {...riseIn(off, { delay: 0.28 })}>
          <BulletRows bullets={bullets.slice(0, TOP_BULLETS)} idBase={`door-${mine.roster_id}`} />
        </motion.div>
      )}
      <PageLink href={tradeHref(analyze, prefill)} label="Open it on the Trade page" />
    </Settle>
  );
}

/* One offer of the trade ideas: the headline, what Your team gives and gets, and its Bullets. */
function Offer({ trade, asker, analyze, index }: { trade: FinderTrade; asker: number; analyze: string; index: number }) {
  const off = useMotionOff();
  const mine = trade.sides.find((side) => side.roster_id === asker) ?? trade.sides[0];
  const partner = trade.sides.find((side) => side.roster_id !== mine.roster_id);
  const prefill: Prefill = {
    team: mine.roster_id,
    partner: partner?.roster_id ?? null,
    gives: mine.gives.map((player) => player.player_id),
    gets: mine.gets.map((player) => player.player_id),
  };
  return (
    <motion.li className="flex flex-col gap-sp-2 border-t border-rule pt-sp-3 first:border-t-0 first:pt-0" {...riseIn(off, { delay: 0.12 + index * 0.08 })}>
      {partner && <Caps>With {partner.team}</Caps>}
      {/* The headline leads, because it is the reason to send the offer. The trade itself follows as a plain line. */}
      {trade.headline && <p className="m-0 text-body leading-body font-semibold text-ink">{trade.headline}</p>}
      <p className="m-0 text-body leading-tight text-ink-2">
        You give <span className="font-semibold text-ink">{names(mine.gives)}</span> and get{" "}
        <span className="font-semibold text-ink">{names(mine.gets)}</span>.
      </p>
      {trade.bullets.length > 0 ? (
        <BulletRows bullets={trade.bullets.slice(0, TOP_OFFER_BULLETS)} idBase={`door-offer-${index}`} />
      ) : (
        trade.fact_lines.map((line) => (
          <p key={line} className="m-0 text-body leading-body text-ink-2">
            {line}
          </p>
        ))
      )}
      <PageLink href={tradeHref(analyze, prefill)} label="Check this trade" delay={0.2 + index * 0.08} />
    </motion.li>
  );
}

/* The trade ideas: each offer of the trade judge, or its plain line when it found none. */
function IdeasBody({ doc, analyze }: { doc: FindResponse; analyze: string }) {
  const asker = doc.trade_pair.asker.roster_id;
  return (
    <Settle label="Trade ideas">
      {doc.trades.length > 0 ? (
        <ul className="m-0 flex list-none flex-col gap-sp-4 p-0">
          {doc.trades.map((trade, index) => (
            <Offer key={trade.offer_id} trade={trade} asker={asker} analyze={analyze} index={index} />
          ))}
        </ul>
      ) : (
        <p className="m-0 text-body leading-body text-ink-2">{doc.empty}</p>
      )}
      <PageLink href={tradeHref(analyze, { team: asker, partner: doc.trade_pair.partner?.roster_id ?? null, gives: [], gets: [] })} label="Build a trade on the Trade page" />
    </Settle>
  );
}

/* The Trade page for a trade that names an unsure player. The link fills only the players that the pick is sure of. */
function FormBody({ form, analyze }: { form: TradeForm; analyze: string }) {
  const filled = form.gives.length + form.gets.length;
  return (
    <Settle label="Trade check">
      <p className="m-0 text-body leading-body text-ink-2">
        {filled > 0
          ? "Some players of that trade are not clear. The Trade page holds the ones that are, so pick the rest there."
          : "Name the players to check that trade. The Trade page lists each roster, so pick them there."}
      </p>
      <a
        href={tradeHref(analyze, { team: form.asker, partner: form.partner, gives: form.gives, gets: form.gets })}
        className="press flex min-h-touch items-center gap-sp-2 self-start rounded-pill bg-ink px-sp-4 text-body leading-tight font-semibold text-card no-underline"
      >
        Open the Trade page
        <ArrowRightIcon aria-hidden className="size-sp-4" strokeWidth={2.25} />
      </a>
    </Settle>
  );
}

/* One trade Answer of the Thread: the question, the steps while it works, then the whole Answer. The steps leave as the
   Answer lands, on a quick fade, so the card takes their place. `analyze` is the path of the Trade page. */
export const TradeCard = forwardRef<
  HTMLElement,
  { question: string; mode: "check" | "ideas"; steps: string[]; answer: TradeAnswer | null; analyze: string }
>(function TradeCard({ question, mode, steps, answer, analyze }, ref) {
  return (
    <article ref={ref} aria-label={question} aria-busy={answer === null} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={question} />
      <AnimatePresence mode="wait" initial={false}>
        {answer === null ? (
          <motion.div key="steps" exit={{ opacity: 0, transition: fadeIn(QUICK) }}>
            <Steps mode={mode} steps={steps} />
          </motion.div>
        ) : (
          <motion.div key="answer">
            {answer.kind === "check" && <CheckBody doc={answer.document} analyze={analyze} />}
            {answer.kind === "ideas" && <IdeasBody doc={answer.document} analyze={analyze} />}
            {answer.kind === "form" && <FormBody form={answer.form} analyze={analyze} />}
          </motion.div>
        )}
      </AnimatePresence>
    </article>
  );
});
