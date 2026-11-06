/**
 * The round photo frame of a headshot or a team avatar: the photo on a ground of the brand glow, cropped at the shoulders.
 * With no image, the frame shows the initials of the name, so a missing photo leaves no hole.
 */
import { cn } from "../lib/utils";

/* The three sizes of the frame: a team row, an award tile, and a hero. Each size token lives in globals.css.
   The initials of the smallest frame take the meta size, 12px on a phone, so they stay over the floor of 11px. */
const SIZES = {
  sm: "size-avatar text-meta",
  md: "size-photo text-meta",
  lg: "size-headshot text-stat",
} as const;

type PhotoFrameProps = {
  // The src of the photo, with the base path, or null when the pipeline has no image.
  src: string | null;
  // The name of the player or the team. It names the frame and gives the initials.
  name: string;
  size?: keyof typeof SIZES;
  // True when the row beside the frame already shows the name, so a screen reader does not hear it twice.
  decorative?: boolean;
  className?: string;
};

/* The first letters of the first two words of a name, in capitals: "Josh Allen" gives "JA". */
export function initialsOf(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join("");
}

export function PhotoFrame({ src, name, size = "md", decorative = false, className }: PhotoFrameProps) {
  const frame = cn("relative inline-flex flex-none overflow-hidden rounded-full shadow-orb", SIZES[size], className);
  if (src === null) {
    // The initials sit on the plain raised surface and not on the glow, so their contrast is the pair of ink on raised.
    return (
      <span
        role={decorative ? undefined : "img"}
        aria-label={decorative ? undefined : name}
        aria-hidden={decorative ? true : undefined}
        className={cn(frame, "items-center justify-center bg-raised font-mono font-bold text-ink")}
      >
        {initialsOf(name)}
      </span>
    );
  }
  return (
    <span className={cn(frame, "photo-ground items-end justify-center")}>
      {/* The top of the photo stays in the frame, so the crop falls at the shoulders and the head is never cut. */}
      <img src={src} alt={decorative ? "" : name} loading="lazy" className="size-full object-cover object-top" />
    </span>
  );
}
