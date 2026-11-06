/**
 * One act of the midseason report: its dark title page, then its chapters in the order of the file.
 * The last act can end on a finale, such as the sim replay that the app mounts there.
 */
import type { ReactNode } from "react";
import type { Act } from "../schema/midseason-types";
import { ActTitle } from "./act-title";
import { type Avatars, ChapterPart } from "./chapter-part";

export function ActSection({
  act,
  index,
  avatars,
  finale,
}: {
  act: Act;
  index: number;
  avatars: Avatars;
  finale?: ReactNode;
}) {
  const heading = `${act.key}-heading`;
  return (
    // The rail sits under the top band, so a jump to the act leaves the height of the rail free above the title page.
    <section id={act.key} aria-labelledby={heading} className="flex scroll-mt-[calc(var(--spacing-touch)+1px)] flex-col gap-sp-6">
      <ActTitle index={index} title={act.title} headingId={heading} />
      {act.chapters.map((chapter) => (
        <ChapterPart key={chapter.key} chapter={chapter} avatars={avatars} />
      ))}
      {finale}
    </section>
  );
}
