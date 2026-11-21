/**
 * The hero of the home page: the matchup of the latest week with the winner by the margin, its reason, both teams, and a
 * button to the week, then the first sentence of the blurb under it. The hero sits on the band in both themes.
 */
import { Hero } from "@cpc/design/parts/hero";
import type { HeroScene } from "@cpc/design/parts/scene-math";
import { Rise } from "@cpc/design/parts/rise";
import type { AvatarMap, Pick } from "../schema/week-types";
import { matchupTitle, TeamRow } from "./matchup-of-the-week";
import { textId } from "@cpc/design/lib/stable-id";

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
  scene,
}: {
  week: number;
  pick: Pick;
  // The avatars with the folder of the week in front of each path, because the home page sits outside the week folder.
  avatars: AvatarMap;
  blurb: string;
  // The href of the week page, with the base path.
  href: string;
  // The scene of the week. The home page passes it when this hero is the first hero of the page.
  scene?: HeroScene;
}) {
  // The JSON puts the winner first. A tie has no winner, and the first side still leads the hero.
  const [first, second] = pick.sides;
  return (
    // The first sentence sits under the hero, so the hero stays as short as the others (decision 05).
    <div className="gap-sp-5 flex flex-col">
      <Hero
        label="Matchup of the Week"
        eyebrow={`Week ${twoDigits(week)} // Matchup of the Week`}
        title={matchupTitle(pick)}
        scene={scene}
        // The intro holds the h1 of the home page, so the title of the hero is an h2.
        level={2}
        meta={pick.reason}
        feature={
          <Rise step={1} className="gap-sp-3 flex flex-col">
            <TeamRow side={first} avatars={avatars} lead withTop={false} />
            <TeamRow side={second} avatars={avatars} lead={false} withTop={false} />
          </Rise>
        }
        action={
          <Rise step={2} className="tablet:w-auto w-full">
            {/* A full pill and a 44px tap target, in the brand color, as the week button of the 404 page. */}
            <a
              href={href}
              className="press min-h-touch rounded-pill bg-accent px-sp-6 text-body text-on-dark flex items-center justify-center font-bold no-underline"
            >
              {`Read Week ${week}`}
            </a>
          </Rise>
        }
      />
      <Rise step={3}>
        <p
          className="max-w-measure text-lead leading-body text-ink-2 m-0"
          {...textId("blurb", firstSentence(blurb))}
        >
          {firstSentence(blurb)}
        </p>
      </Rise>
    </div>
  );
}
