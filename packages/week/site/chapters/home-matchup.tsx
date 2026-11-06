/**
 * The hero of the home page: the matchup of the latest week with its reason, the margin, both teams, the first sentence
 * of the blurb, and a button to the week. It sits on the band in both themes, as the hero of the week page does.
 */
import { num } from "@cpc/design/format/format";
import { Hero } from "@cpc/design/parts/hero";
import { Rise } from "@cpc/design/parts/rise";
import type { AvatarMap, Pick } from "../schema/week-types";
import { TeamRow } from "./matchup-of-the-week";

/* The week number with two digits, as the week chip writes it: "08". */
const twoDigits = (week: number) => String(week).padStart(2, "0");

/* The first sentence of a blurb. A stop followed by a digit is a decimal point, such as "1.43", so only a stop at the
   end or before a space ends the sentence. */
export function firstSentence(blurb: string): string {
  const match = /^.*?[.!?](?=\s|$)/s.exec(blurb.trim());
  return match ? match[0] : blurb.trim();
}

export function HomeMatchup({
  week,
  pick,
  avatars,
  blurb,
  href,
}: {
  week: number;
  pick: Pick;
  // The avatars with the folder of the week in front of each path, because the home page sits outside the week folder.
  avatars: AvatarMap;
  blurb: string;
  // The href of the week page, with the base path.
  href: string;
}) {
  // The JSON puts the winner first. A tie has no winner, and the first side still leads the hero.
  const [first, second] = pick.sides;
  return (
    <Hero label="Matchup of the Week">
      {/* The intro holds the h1 of the home page, so the label of the hero is plain text. */}
      <Rise step={0}>
        <div className="plate w-fit font-mono text-meta leading-tight font-bold tracking-caps text-on-dark-muted uppercase">
          {`Week ${twoDigits(week)} // Matchup of the Week`}
        </div>
      </Rise>
      <Rise step={1} className="mt-sp-5">
        <div className="plate w-fit font-mono text-meta leading-tight font-bold tracking-caps text-accent-text uppercase">
          {`${pick.reason} · Margin`}
        </div>
        <div className="plate mt-sp-2 w-fit font-mono text-hero leading-none font-bold tracking-grade tabular-nums">
          {num(first.score - second.score)}
        </div>
      </Rise>
      <Rise step={2} className="mt-sp-5 flex flex-col gap-sp-3">
        <TeamRow side={first} avatars={avatars} lead withTop={false} />
        <TeamRow side={second} avatars={avatars} lead={false} withTop={false} />
      </Rise>
      <Rise step={3}>
        <p className="plate mt-sp-5 mb-0 w-fit max-w-measure text-lead leading-body text-on-dark-2">{firstSentence(blurb)}</p>
        {/* A full pill and a 44px tap target, in the brand color, as the week button of the 404 page. */}
        <a
          href={href}
          className="press mt-sp-5 flex min-h-touch items-center justify-center rounded-pill bg-accent px-sp-6 text-body font-bold text-on-dark no-underline"
        >
          {`Read Week ${week}`}
        </a>
      </Rise>
    </Hero>
  );
}
