/**
 * The round team avatar image, with the swap to the default avatar on an image error. It ports the .avatar rule of the source stylesheet.
 * It is decorative, because the team name always sits next to it. It is a client part, because a server component cannot pass the error handler to the image.
 */
"use client";

import { swapAvatarToDefault } from "@/lib/avatar";

/* A named size maps to a size class of the theme. A number sets the width and the height in pixels, for a size that comes from a layout table. */
const SIZES = { avatar: "size-avatar", headshot: "size-headshot", ring: "size-ring-avatar" } as const;

/* The team name sits next to the avatar, so the image is decorative.
   The size class comes first and the className follows. A plain join keeps each class list as the page had it, because cn can merge or drop a name it does not know. */
export function Avatar({
  src,
  size = "avatar",
  className = "flex-none rounded-full bg-gry object-cover",
}: {
  src: string;
  size?: keyof typeof SIZES | number;
  className?: string;
}) {
  const named = typeof size === "string";
  return (
    <img
      src={src}
      alt=""
      onError={swapAvatarToDefault}
      style={named ? undefined : { width: size, height: size }}
      className={named ? `${SIZES[size]} ${className}` : className}
    />
  );
}
