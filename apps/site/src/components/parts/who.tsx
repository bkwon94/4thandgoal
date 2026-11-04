/**
 * The avatar and the team name as one group.
 * An href makes the name a link to the manager page.
 */
import { Avatar } from "@cpc/league/avatar";
import { TeamName } from "@cpc/design/parts/team-name";
import { cn } from "@cpc/design/lib/utils";

/* The avatar and the team name as one group, as the .who rule of the stylesheet sets it.
   Fill makes the group take the free width of a row and lets a long name wrap inside it.
   An href makes the name a link to the manager page. With no href the name is plain text. */
export function Who({ src, name, fill, href = null }: { src: string; name: string; fill?: boolean; href?: string | null }) {
  return (
    <span className={cn("items-center gap-sp-2 align-middle", fill ? "flex min-w-0 flex-1" : "inline-flex")}>
      <Avatar src={src} />
      <span className={cn(fill && "min-w-0")}>
        <TeamName name={name} href={href} />
      </span>
    </span>
  );
}
