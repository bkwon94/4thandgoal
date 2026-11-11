/**
 * The Answers of the trade Topics in the Thread: the plain steps while the trade judge works, then the trade check with
 * its Lean, Case, and top Bullets, the trade ideas with each offer, the players to sell with why, or the Trade page for
 * a trade with an unsure player.
 */
"use client";

import { motion } from "framer-motion";
import { forwardRef, useId, useState, type ReactNode } from "react";
import { ArrowRightIcon } from "lucide-react";
import { BulletRows } from "@cpc/analyzer/form/bullet-rows";
import type { AnalyzeResponse, FindResponse, FinderTrade, Lean, NearIdea } from "@cpc/analyzer/lib/analyze-types";
import { prefillQuery, type Prefill } from "@cpc/analyzer/lib/prefill";
import { Headshot } from "@cpc/league/headshot";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { managerHref } from "@/lib/routes";
import { FAST, SLOW, STAGGER, VERY_SLOW, fadeIn, riseIn } from "./motion";
import { QuestionBubble, Surface } from "./miss-card";
import { StaleLine } from "./personal-answer";
import { type Step, Steps } from "./steps";
import type { SellHigh, TradeAnswer, TradeForm } from "./trade-api";

/* The Bullets that the check shows of Your side, and of each offer. The Trade page holds each one. */
export const TOP_BULLETS = 3;
export const TOP_OFFER_BULLETS = 2;

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

/* The steps of the trade judge as the one step pattern. Each line comes when its stage ends, so while the Answer is
   not in, the newest line is the live one. Once the Answer lands, each line shows done. */
const tradeSteps = (steps: string[], live: boolean): Step[] => steps.map((line, index) => ({ line, done: !live || index < steps.length - 1 }));

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

/* One near idea: an offer that the trade judge weighed and would not send. It keeps the rows of an offer, with no
   headline, in the quieter ink, and the reason it fell short sits under the trade, so the manager reads why not. */
function Near({ idea, asker, analyze, index }: { idea: NearIdea; asker: number; analyze: string; index: number }) {
  const off = useMotionOff();
  const mine = idea.sides.find((side) => side.roster_id === asker) ?? idea.sides[0];
  const partner = idea.sides.find((side) => side.roster_id !== mine.roster_id);
  const prefill: Prefill = {
    team: mine.roster_id,
    partner: partner?.roster_id ?? null,
    gives: mine.gives.map((player) => player.player_id),
    gets: mine.gets.map((player) => player.player_id),
  };
  return (
    <motion.li className="flex flex-col gap-sp-2 border-t border-rule pt-sp-3 first:border-t-0 first:pt-0" {...riseIn(off, { delay: 0.12 + index * 0.08 })}>
      {partner && <Caps>With {partner.team}</Caps>}
      <p className="m-0 text-body leading-tight text-ink-2">
        You give <span className="font-semibold">{names(mine.gives)}</span> and get <span className="font-semibold">{names(mine.gets)}</span>.
      </p>
      {/* The rule on the left marks the reason as a note on the trade above it, not a claim of its own. */}
      <p className="m-0 border-l-2 border-rule pl-sp-3 text-body leading-body text-mute">{idea.reason}</p>
      <PageLink href={tradeHref(analyze, prefill)} label="Check this trade" delay={0.2 + index * 0.08} />
    </motion.li>
  );
}

/* The near ideas under one plain label. The label names the list, so a screen reader hears it with the list. */
function NearList({ near, label, asker, analyze, from }: { near: NearIdea[]; label: string; asker: number; analyze: string; from: number }) {
  const id = useId();
  return (
    // After the picks, a rule closes the picks off, so the label reads as the head of a second list.
    <div className={`flex flex-col gap-sp-3 ${from > 0 ? "border-t border-rule pt-sp-4" : ""}`}>
      <span id={id}>
        <Caps>{label}</Caps>
      </span>
      <ul aria-labelledby={id} className="m-0 flex list-none flex-col gap-sp-4 p-0">
        {near.map((idea, index) => (
          <Near key={idea.offer_id} idea={idea} asker={asker} analyze={analyze} index={from + index} />
        ))}
      </ul>
    </div>
  );
}

/* The trade ideas: each offer of the trade judge, then the near ideas it weighed with why each fell short. With no
   offer to send, the near ideas lead, because an idea is an idea. Only a search that built no offer shows its plain
   line alone. */
function IdeasBody({ doc, analyze }: { doc: FindResponse; analyze: string }) {
  const asker = doc.trade_pair.asker.roster_id;
  return (
    <Settle label="Trade ideas">
      {doc.trades.length > 0 && (
        <ul className="m-0 flex list-none flex-col gap-sp-4 p-0">
          {doc.trades.map((trade, index) => (
            <Offer key={trade.offer_id} trade={trade} asker={asker} analyze={analyze} index={index} />
          ))}
        </ul>
      )}
      {doc.near.length > 0 && (
        <NearList
          near={doc.near}
          label={doc.trades.length > 0 ? "Also weighed" : "Ideas, none a clear win"}
          asker={asker}
          analyze={analyze}
          from={doc.trades.length}
        />
      )}
      {doc.trades.length === 0 && doc.near.length === 0 && <p className="m-0 text-body leading-body text-ink-2">{doc.empty}</p>}
      <PageLink href={tradeHref(analyze, { team: asker, partner: doc.trade_pair.partner?.roster_id ?? null, gives: [], gets: [] })} label="Build a trade on the Trade page" />
    </Settle>
  );
}

/* The ranks of a player to sell, in the words of the side card of the Trade page: the Season rank, then the Recent
   rank only when the document sends one. */
function rankLine(player: SellHigh["picks"][number]["player"]): string | null {
  if (!player.season_rank) return null;
  return player.recent_rank ? `Season rank ${player.season_rank} · Recent rank ${player.recent_rank}` : `Season rank ${player.season_rank}`;
}

/* One player to sell: his headshot, his name, his position and NFL team, his ranks, the headline of why, and its top
   Bullets. The player leads, because the manager reads first who to move, then why. */
function SellPick({ pick, index }: { pick: SellHigh["picks"][number]; index: number }) {
  const off = useMotionOff();
  const { player } = pick;
  const ranks = rankLine(player);
  return (
    <motion.li
      aria-label={`Sell ${player.name}`}
      className="flex flex-col gap-sp-3 border-t border-rule pt-sp-3 first:border-t-0 first:pt-0"
      {...riseIn(off, { delay: 0.12 + index * 0.08 })}
    >
      <div className="flex items-center gap-sp-3">
        <Headshot src={player.headshot} size="avatar" lazy className="flex-none rounded-full bg-page object-cover object-top" />
        <div className="flex min-w-0 flex-col gap-sp-0">
          <p className="m-0 text-body leading-tight font-bold text-ink">{player.name}</p>
          <p className="m-0 text-meta leading-tight text-mute">
            {player.position} · {player.nfl_team}
          </p>
          {ranks && <p className="m-0 text-meta leading-tight text-ink-2">{ranks}</p>}
        </div>
      </div>
      <p className="m-0 text-body leading-body font-semibold text-ink">{pick.headline}</p>
      {pick.bullets.length > 0 && <BulletRows bullets={pick.bullets.slice(0, TOP_OFFER_BULLETS)} idBase={`door-sell-${index}`} />}
    </motion.li>
  );
}

/* Sell high or buy low: each player of Your team to sell, or the plain line of a roster with no clear sell. The full
   report is the manager page of Your team. */
function SellBody({ doc }: { doc: SellHigh }) {
  return (
    <Settle label="Sell high or buy low">
      {doc.picks.length > 0 ? (
        <ul className="m-0 flex list-none flex-col gap-sp-4 p-0">
          {doc.picks.map((pick, index) => (
            <SellPick key={pick.player.player_id} pick={pick} index={index} />
          ))}
        </ul>
      ) : (
        <p className="m-0 text-body leading-body text-ink-2">{doc.empty}</p>
      )}
      <PageLink href={managerHref(String(doc.season), doc.team.roster_id)} label="Open your manager page" />
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

/* One trade Answer of the Thread: the question, the steps in their card while it works, then the whole Answer under
   them. The steps stay above the Answer, so the manager sees the work behind it. `analyze` is the path of the Trade
   page. A stale Answer, whose rosters changed since its read, shows dimmed under the stale line and Refresh, as a stale
   personal Answer. */
export const TradeCard = forwardRef<
  HTMLElement,
  { question: string; steps: string[]; answer: TradeAnswer | null; analyze: string; stale?: { line: string; onRefresh: () => void } | null; morph?: string }
>(function TradeCard({ question, steps, answer, analyze, stale = null, morph }, ref) {
  return (
    <article ref={ref} aria-label={question} aria-busy={answer === null} data-stale={stale ? "" : undefined} className="flex scroll-mt-door-under-head flex-col gap-sp-3">
      <QuestionBubble question={question} morph={morph} />
      {/* The stale line comes before the read it warns about, so the manager sees it first. */}
      {stale && <StaleLine line={stale.line} onRefresh={stale.onRefresh} />}
      {/* The dim is an opacity change only, so reduced motion keeps it as is. */}
      <div className={`flex flex-col gap-sp-3 transition-opacity duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] ${stale ? "opacity-60" : "opacity-100"}`}>
        {/* A tapped trade check opens the Trade page at once, with no step, so it shows no card of steps. */}
        {(answer === null || steps.length > 0) && (
          <Surface>
            <Steps steps={tradeSteps(steps, answer === null)} live={answer === null} />
          </Surface>
        )}
        {answer?.kind === "check" && <CheckBody doc={answer.document} analyze={analyze} />}
        {answer?.kind === "ideas" && <IdeasBody doc={answer.document} analyze={analyze} />}
        {answer?.kind === "form" && <FormBody form={answer.form} analyze={analyze} />}
        {answer?.kind === "sell" && <SellBody doc={answer.document} />}
      </div>
    </article>
  );
});
