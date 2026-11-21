/**
 * A lint fixture: the spacing value of spacing.tsx with a one-line ignore and a reason on the line above it.
 * The value rule test expects design/no-arbitrary-value to pass it.
 */
import { cn } from "@/lib/utils";

export const Rail = ({ open }: { open: boolean }) => (
  <nav
    // oxlint-disable-next-line design/no-arbitrary-value -- a one-off offset that no token names
    className={cn("sticky", "top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]", open && "opacity-100")}
  />
);
