/**
 * Quick hits, the last chapter of Act II: one block that holds the lineup choices and the injury toll.
 * Each part keeps its own list and its own prose under a level 4 heading.
 */
import { ReportChapter } from "../report/report-chapter";
import type { QuickHitsChapter } from "../schema/midseason-types";
import { Injuries } from "./injuries";
import { Lineup } from "./lineup";

export function QuickHits({ chapter }: { chapter: QuickHitsChapter }) {
  return (
    <ReportChapter id={chapter.key} title={chapter.title}>
      <div className="flex flex-col gap-sp-5">
        {chapter.chapters.map((part) =>
          part.key === "lineup" ? (
            <Lineup key={part.key} chapter={part} level={4} />
          ) : (
            <Injuries key={part.key} chapter={part} level={4} />
          ),
        )}
      </div>
    </ReportChapter>
  );
}
