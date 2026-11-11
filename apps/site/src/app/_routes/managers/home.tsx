/**
 * The home tool of the managers package: the Managers tile of the Tools chapter.
 * The registry of the client build imports it only when the client takes managers.
 */
import { UsersIcon } from "lucide-react";
import { currentManagersHref } from "@/lib/data/manager-data";
import { HomeTile } from "@/app/home-tile";

/* A missing managers file hides the tile, as the menu hides its entry, so the page ships before the pipeline writes the file. */
export function HomeTool() {
  const managersHref = currentManagersHref();
  if (!managersHref) return null;
  // The dock shows the same icon for the managers, so the tile and the dock item read as one place.
  return (
    <HomeTile
      href={managersHref}
      icon={UsersIcon}
      name="Managers"
      line="One page per team: grade, odds, moves, and performers."
    />
  );
}
