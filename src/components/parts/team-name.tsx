/**
 * The team name, as a link to the manager page when the season has one.
 * The page passes the href, so the part holds no route format.
 */
/* A team name, as a link to the manager page when the season has one, else as plain text.
   The link inherits the color, the weight, the size, and the wrap of the name, so the name does not shift.
   Only the hover underline marks it, as on the given player links. It sits on a positioned layer,
   so a row control stretched over the row does not cover it. A plain anchor carries the base path in the href. */
export function TeamName({ name, href }: { name: string; href: string | null }) {
  if (href === null) return name;
  return (
    <a href={href} className="relative z-1 text-inherit no-underline underline-offset-2 hover-fine:underline">
      {name}
    </a>
  );
}
