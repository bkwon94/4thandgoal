/**
 * One tile of the Tools chapter of the home page: a card link with an icon, the name of the tool, and one line of copy.
 * The home tool of each package renders its tile with it, so every tool tile looks the same.
 */
import type { LucideIcon } from "lucide-react";

/* A plain anchor, so the link skips the router. The whole card is the tap target, well over 44px on each side. */
export function HomeTile({ href, icon: Icon, name, line }: { href: string; icon: LucideIcon; name: string; line: string }) {
  return (
    <a
      href={href}
      className="press group flex h-full min-w-0 flex-col gap-sp-3 rounded-card border border-rule bg-card p-sp-4 text-ink no-underline"
    >
      {/* The name of the tool sits beside the icon, so the icon is decorative. */}
      <span className="inline-flex size-touch items-center justify-center rounded-tile border border-rule bg-raised text-accent-ink">
        <Icon aria-hidden className="size-sp-5" />
      </span>
      <b className="text-lead leading-tight group-hover:text-accent-ink">{name}</b>
      <span className="text-meta leading-body text-mute">{line}</span>
    </a>
  );
}
