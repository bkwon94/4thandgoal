/**
 * The round team avatar image. It ports the .avatar rule of the source stylesheet.
 * It is decorative, because the team name always sits next to it.
 */

/* The team name sits next to the avatar, so the image is decorative. */
export function Avatar({ src }: { src: string }) {
  return <img src={src} alt="" className="size-avatar flex-none rounded-full bg-gry object-cover" />;
}
